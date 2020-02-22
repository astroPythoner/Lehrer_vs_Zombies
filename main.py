import pygame
import sys
from random import choice
from time import time, sleep
from constants import *
from sprites import *
from tilemap import *
from math import pi
import lehrer_funktionen

halbes_pi = pi / 2


class Game:
    def __init__(self):
        # Lehrer funktionen datei vervollstaendigen
        was_lehrerfunktionen_vollstaendig = True
        for lehrer in LEHRER:
            for funktionsname in ["power_up_", "object_collect_", "obstacle_", "health_pack_"]:
                try:
                    name = "lehrer_funktionen." + funktionsname + lehrer.replace(" ", "_") + "(test=True,player=None,game=None)"
                    eval(name)
                except AttributeError:
                    with open("lehrer_funktionen.py", "a") as file:
                        was_lehrerfunktionen_vollstaendig = False
                        file.write("\ndef " + funktionsname + lehrer.replace(" ", "_") + "(game, player, test = False):\n    if not test:\n        pass\n")
        if not was_lehrerfunktionen_vollstaendig:
            raise Exception("lehrer_funktionen.py war nicht vollstaendig und wurde so weit automatisch vervollstaendigt, dass das Spiel beim nachsten Durchlauf funktionert. Mehr Infos zu den Lehrerfunktionen findest du in der Anleitung zum Spielercharakter erstellen unter dem Punkt Unterprogramme")
        pygame.mixer.pre_init(44100, -16, 4, 2048)
        self.WIDTH = start_width
        self.HEIGHT = start_height

        self.GRIDWIDTH = int(start_width / TILESIZE)
        self.GRIDHEIGHT = int(start_height / TILESIZE)
        self.small_map_sichtweite = self.calculate_fit_size(SMALL_MAP_SICHTWEITE_FAKTOR, SMALL_MAP_SICHTWEITE_FAKTOR)

        self.background = pygame.transform.scale(background, (start_width, start_height))
        self.background_rect = self.background.get_rect()

        self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT), pygame.RESIZABLE)
        pygame.display.set_caption("Tilmap Zombie! - " + version)
        self.clock = pygame.time.Clock()

        self.update_text_sizes()

        self.maussteuerung_circle_radius = self.calculate_fit_size(0.35, 0.35)

        self.last_personen_obstacle_damage = []
        self.was_on_obstacle_last_time = []
        self.last_personen_object = []
        self.last_power_up_use_time = []
        self.collected_person_objects = []
        self.paused = []

        self.live_bar_images = []
        if self.WIDTH / self.HEIGHT < 0.4555555:
            self.live_bar_img_width = int(0.375 * self.WIDTH)
            self.live_bar_img_height = int(self.live_bar_img_width / 360 * 164)
        else:
            self.live_bar_img_height = int(0.25625 * self.HEIGHT)
            self.live_bar_img_width = int(self.live_bar_img_height / 164 * 360)
        self.level_bar_lenght = 1
        self.level_bar_height = 1

        self.longest_lehrer_name = 0
        self.longest_weapon_name = 0
        self.longest_object_name = 0
        self.lehrer_to_be_unlocked = []
        self.lehrer_unlocked_sofar = []
        self.time_last_lehrer_unlock = 0
        self.weapon_upgrade_unlock_times = []
        self.upgraded_weapons_lehrer_namen = []
        self.lehrer_unlocked_last = None
        for lehrer in LEHRER:
            width = self.get_text_rect(LEHRER[lehrer]["anrede"] + " " + LEHRER[lehrer]["name"], self.HUGE_TEXT).width
            if width > self.longest_lehrer_name:
                self.longest_lehrer_name = width
            width = self.get_text_rect("Waffe: " + str(LEHRER[lehrer]["weapon_name"]), self.SMALL_TEXT, ARIAL_FONT).width
            if width > self.longest_weapon_name:
                self.longest_weapon_name = width
            width = self.get_text_rect(str(LEHRER[lehrer]["personen_item_text"]) + ":" + str(99), self.BIG_TEXT).width
            if width > self.longest_object_name:
                self.longest_object_name = width
            if LEHRER[lehrer]["bedingungen_fuer_unlock"] != None:
                self.lehrer_to_be_unlocked.append(lehrer)

        self.forground_text_img = pygame.Surface((self.WIDTH, self.HEIGHT), pygame.SRCALPHA)
        self.num_zombies_text_pos = (0, 0)
        self.personen_item_text_pos = []
        self.bigest_num_length = 0
        self.number_surfaces = {}
        for x in range(10):
            rect = self.get_text_rect(x, self.BIG_TEXT)
            if rect.width > self.bigest_num_length:
                self.bigest_num_length = rect.width
        for x in range(10):
            surf = pygame.Surface((self.bigest_num_length, int(self.BIG_TEXT * 1.2)), pygame.SRCALPHA)
            self.draw_text(surf, x, self.BIG_TEXT, 0, 0, rect_place="oben_links")
            self.number_surfaces[x] = surf

        self.lehrer_selection_surfaces = {}

        self.schoene_grafik = True

        self.game_status = START_GAME
        self.schwierigkeit = 3
        self.spielmodus = MAP_MODUS
        self.genauerer_spielmodus = AFTER_KILLED
        self.map_name = MAP_NAMES[0]
        self.with_maussteuerung = True
        self.multiplayer = False
        self.num_players_in_multiplayer = 2
        self.players = []

        self.level_start_time = 0
        self.last_zombie_wave_time = 0
        self.countdown_start_time = 0
        self.num_zombie_wave = 1
        self.level_start_num_zombies = 0

        self.endgegner_pos = (0, 0)
        self.endgegner_kill_pos = (0, 0)
        self.endgegner_jump_points = []
        self.endgegner_after_kill_respawn_point = []

        self.werte_since_last_lehrer_change = {}  # mehr Moeglichkeiten fuer Bedingungen

        self.player_pos = (0, 0)

        self.measure_times = False
        self.fps_werte = []
        self.measured_times = [[], [], [], [], [], [], [], [], []]

    def draw_text(self, surf, text, size, x, y, font_name=HUD_FONT, color=TEXT_COLOR, rect_place="oben_mitte"):
        # Zeichnet den text in der color auf die surf.
        # x und y sind die Koordinaten des Punktes rect_place. rect_place kann "oben_mitte", "oben_links" oder "oben_rechts" sein.
        font = pygame.font.Font(font_name, size)
        text_surface = font.render(str(text), True, color)
        text_rect = text_surface.get_rect()

        x = int(x)
        y = int(y)

        if rect_place == "oben_mitte":
            text_rect.midtop = (x, y)
        elif rect_place == "oben_links":
            text_rect.topleft = (x, y)
        elif rect_place == "oben_rechts":
            text_rect.topright = (x, y)
        elif rect_place == "mitte_rechts":
            text_rect.midright = (x, y)
        elif rect_place == "mitte_links":
            text_rect.midleft = (x, y)
        elif rect_place == "mitte":
            text_rect.center = (x, y)
        elif rect_place == "unten_mitte":
            text_rect.midbottom = (x, y)
        elif rect_place == "unten_rechts":
            text_rect.bottomright = (x, y)
        elif rect_place == "unten_links":
            text_rect.bottomleft = (x, y)
        else:
            print("rect_pos given to draw_text is not known")
        surf.blit(text_surface, text_rect)
        return text_rect

    def get_text_rect(self, text, size, font=HUD_FONT):
        font = pygame.font.Font(font, size)
        text_surface = font.render(str(text), True, WHITE)
        return text_surface.get_rect()

    def check_key_or_mouse_pressed(self, check_for=[], joystick_num="both"):
        return_dict = {}

        for key in check_for:
            return_dict[key] = False
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT or event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self.quit()

            if event.type == pygame.KEYDOWN:
                if event.key in check_for:
                    return_dict[event.key] = True
                if "text" in check_for:
                    return_dict["text"] = event.unicode

            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    return_dict[MAUS_LEFT] = event.pos
                elif event.button == 3:
                    return_dict[MAUS_RIGHT] = event.pos
                elif event.button == 4:
                    return_dict[MAUS_ROLL_UP] = event.pos
                elif event.button == 5:
                    return_dict[MAUS_ROLL_DOWN] = event.pos

            if event.type == pygame.VIDEORESIZE:
                self.window_resize(event.w, event.h)

        return return_dict

    def check_maus_pos_on_rect(self, maus_pos, rect):
        return rect.collidepoint(maus_pos)

    def draw_start_game_screen(self, loading=False):
        return_dict = {}

        # Hintergrund
        self.screen.blit(self.background, self.background_rect)

        # Schoene oder fluessige Grafik
        if self.schoene_grafik:
            return_dict["Grafik"] = self.draw_text(self.screen, "schöne Grafik", self.NORMAL_TEXT, 10, 10, rect_place="oben_links", color=AUSWAHL_TEXT_COLOR)
        else:
            return_dict["Grafik"] = self.draw_text(self.screen, "flüssige Grafik", self.NORMAL_TEXT, 10, 10, rect_place="oben_links", color=AUSWAHL_TEXT_COLOR)

        # Maussteuerung an oder aus
        if self.with_maussteuerung:
            return_dict["Maus"] = self.draw_text(self.screen, "Maussteuerung", self.NORMAL_TEXT, 10, 15 + self.NORMAL_TEXT, rect_place="oben_links", color=AUSWAHL_TEXT_COLOR)
        else:
            return_dict["Maus"] = self.draw_text(self.screen, "Tastatursteuerung", self.NORMAL_TEXT, 10, 15 + self.NORMAL_TEXT, rect_place="oben_links", color=AUSWAHL_TEXT_COLOR)

        # Spielerkaerung
        return_dict["Hilfe"] = self.draw_text(self.screen, "Hilfe/Erklärung", self.NORMAL_TEXT, self.WIDTH - 10, 10, rect_place="oben_rechts", color=AUSWAHL_TEXT_COLOR)

        # Titel
        if self.game_status == PLAYER_DIED:
            self.draw_text(self.screen, "GAME OVER", self.GIANT_TEXT, int(self.WIDTH / 2), int(self.HEIGHT * 0.13), rect_place="mitte", color=AUSWAHL_TEXT_RED)
        elif self.game_status == WON_GAME:
            self.draw_text(self.screen, "YOU WON", self.GIANT_TEXT, int(self.WIDTH / 2), int(self.HEIGHT * 0.13), rect_place="mitte", color=AUSWAHL_TEXT_GREEN)
        else:
            self.draw_text(self.screen, "Zombie!", self.GIANT_TEXT, int(self.WIDTH / 2), int(self.HEIGHT * 0.13), rect_place="mitte", color=AUSWAHL_TEXT_COLOR)

        # Schwierigkeit
        circle_size = self.calculate_fit_size(0.02604167, 0.0390625)
        self.draw_text(self.screen, "Schwierigkeit", int(self.BIG_TEXT * 1.2), int(self.WIDTH / 2), int(self.HEIGHT * 0.25), color=AUSWAHL_TEXT_COLOR)
        pygame.draw.line(self.screen, AUSWAHL_TEXT_COLOR, (int(self.WIDTH * (1 / 6)), int(self.HEIGHT * 0.38)), (int(self.WIDTH * (5 / 6)), int(self.HEIGHT * 0.38)), 5)
        for schwierigkeitsstufe in range(1, 6):
            if self.schwierigkeit == schwierigkeitsstufe and not loading:
                return_dict["Schwierigkeit_" + str(schwierigkeitsstufe)] = pygame.draw.circle(self.screen, AUSWAHL_TEXT_GREEN, (int(self.WIDTH * (schwierigkeitsstufe / 6)), int(self.HEIGHT * 0.38)), circle_size, 0)
            else:
                return_dict["Schwierigkeit_" + str(schwierigkeitsstufe)] = pygame.draw.circle(self.screen, AUSWAHL_TEXT_COLOR, (int(self.WIDTH * (schwierigkeitsstufe / 6)), int(self.HEIGHT * 0.38)), circle_size, 0)
            self.draw_text(self.screen, str(schwierigkeitsstufe), int(circle_size * 1.3), int(self.WIDTH * (schwierigkeitsstufe / 6)), int(self.HEIGHT * 0.38), color=BLACK, rect_place="mitte")

        # Spielmodus
        self.draw_text(self.screen, "SPIELMODUS", int(self.BIG_TEXT * 1.2), int(self.WIDTH / 2), int(self.HEIGHT * 0.47), color=AUSWAHL_TEXT_COLOR)
        if self.spielmodus != MAP_MODUS or loading:
            return_dict[MAP_MODUS] = self.draw_text(self.screen, "Zombie Map", self.NORMAL_TEXT, int(self.WIDTH * 2 / 3), int(self.HEIGHT * 0.57), color=AUSWAHL_TEXT_COLOR, rect_place="mitte")
            if loading and self.spielmodus == MAP_MODUS:
                spielmodus_rect = return_dict[MAP_MODUS]
        elif self.spielmodus == MAP_MODUS:
            spielmodus_rect = self.draw_text(self.screen, "Zombie Map", self.NORMAL_TEXT, int(self.WIDTH * 2 / 3), int(self.HEIGHT * 0.57), color=AUSWAHL_TEXT_GREEN, rect_place="mitte")
            return_dict[MAP_MODUS] = spielmodus_rect
        if self.spielmodus != ARENA_MODUS or loading:
            return_dict[ARENA_MODUS] = self.draw_text(self.screen, "Arena Modus", self.NORMAL_TEXT, int(self.WIDTH * 1 / 3), int(self.HEIGHT * 0.57), color=AUSWAHL_TEXT_COLOR, rect_place="mitte")
            if loading and self.spielmodus == ARENA_MODUS:
                spielmodus_rect = return_dict[ARENA_MODUS]
        elif self.spielmodus == ARENA_MODUS:
            spielmodus_rect = self.draw_text(self.screen, "Arena Modus", self.NORMAL_TEXT, int(self.WIDTH * 1 / 3), int(self.HEIGHT * 0.57), color=AUSWAHL_TEXT_GREEN, rect_place="mitte")
            return_dict[ARENA_MODUS] = spielmodus_rect
        # weitere Spielmodus einstellung
        if self.spielmodus == MAP_MODUS:
            pygame.draw.line(self.screen, AUSWAHL_TEXT_COLOR, spielmodus_rect.midbottom, (int(self.WIDTH * 2 / 4), int(self.HEIGHT * 0.62)), 3)
            pygame.draw.line(self.screen, AUSWAHL_TEXT_COLOR, spielmodus_rect.midbottom, (int(self.WIDTH * 3 / 4), int(self.HEIGHT * 0.62)), 3)
            if self.genauerer_spielmodus == AFTER_TIME and not loading:
                return_dict[AFTER_TIME + "0"] = self.draw_text(self.screen, "Gewonnen nach", self.NORMAL_TEXT, int(self.WIDTH * 2 / 4), int(self.HEIGHT * 0.62), color=AUSWAHL_TEXT_GREEN, rect_place="oben_mitte")
                return_dict[AFTER_TIME + "1"] = self.draw_text(self.screen, "Zeit", self.NORMAL_TEXT, int(self.WIDTH * 2 / 4), int(self.HEIGHT * 0.62) + self.NORMAL_TEXT + 5, color=AUSWAHL_TEXT_GREEN, rect_place="oben_mitte")
            else:
                return_dict[AFTER_TIME + "0"] = self.draw_text(self.screen, "Gewonnen nach", self.NORMAL_TEXT, int(self.WIDTH * 2 / 4), int(self.HEIGHT * 0.62), color=AUSWAHL_TEXT_COLOR, rect_place="oben_mitte")
                return_dict[AFTER_TIME + "1"] = self.draw_text(self.screen, "Zeit", self.NORMAL_TEXT, int(self.WIDTH * 2 / 4), int(self.HEIGHT * 0.62) + self.NORMAL_TEXT + 5, color=AUSWAHL_TEXT_COLOR, rect_place="oben_mitte")
            if self.genauerer_spielmodus == AFTER_KILLED and not loading:
                return_dict[AFTER_KILLED + "0"] = self.draw_text(self.screen, "Gewonnen nach", self.NORMAL_TEXT, int(self.WIDTH * 3 / 4), int(self.HEIGHT * 0.62), color=AUSWAHL_TEXT_GREEN, rect_place="oben_mitte")
                return_dict[AFTER_KILLED + "1"] = self.draw_text(self.screen, "töten aller Zombies", self.NORMAL_TEXT, int(self.WIDTH * 3 / 4), int(self.HEIGHT * 0.62) + self.NORMAL_TEXT + 5, color=AUSWAHL_TEXT_GREEN, rect_place="oben_mitte")
            else:
                return_dict[AFTER_KILLED + "0"] = self.draw_text(self.screen, "Gewonnen nach", self.NORMAL_TEXT, int(self.WIDTH * 3 / 4), int(self.HEIGHT * 0.62), color=AUSWAHL_TEXT_COLOR, rect_place="oben_mitte")
                return_dict[AFTER_KILLED + "1"] = self.draw_text(self.screen, "töten aller Zombies", self.NORMAL_TEXT, int(self.WIDTH * 3 / 4), int(self.HEIGHT * 0.62) + self.NORMAL_TEXT + 5, color=AUSWAHL_TEXT_COLOR, rect_place="oben_mitte")
        elif self.spielmodus == ARENA_MODUS:
            pygame.draw.line(self.screen, AUSWAHL_TEXT_COLOR, spielmodus_rect.midbottom, (int(self.WIDTH * 1 / 4), int(self.HEIGHT * 0.62)), 3)
            pygame.draw.line(self.screen, AUSWAHL_TEXT_COLOR, spielmodus_rect.midbottom, (int(self.WIDTH * 2 / 4), int(self.HEIGHT * 0.62)), 3)
            if self.genauerer_spielmodus == AFTER_TIME:
                return_dict[AFTER_TIME + "0"] = self.draw_text(self.screen, "Zombiewelle nach", self.NORMAL_TEXT, int(self.WIDTH * 1 / 4), int(self.HEIGHT * 0.62), color=AUSWAHL_TEXT_GREEN, rect_place="oben_mitte")
                return_dict[AFTER_TIME + "1"] = self.draw_text(self.screen, "Zeit", self.NORMAL_TEXT, int(self.WIDTH * 1 / 4), int(self.HEIGHT * 0.62) + self.NORMAL_TEXT + 5, color=AUSWAHL_TEXT_GREEN, rect_place="oben_mitte")
            else:
                return_dict[AFTER_TIME + "0"] = self.draw_text(self.screen, "Zombiewelle nach", self.NORMAL_TEXT, int(self.WIDTH * 1 / 4), int(self.HEIGHT * 0.62), color=AUSWAHL_TEXT_COLOR, rect_place="oben_mitte")
                return_dict[AFTER_TIME + "1"] = self.draw_text(self.screen, "Zeit", self.NORMAL_TEXT, int(self.WIDTH * 1 / 4), int(self.HEIGHT * 0.62) + self.NORMAL_TEXT + 5, color=AUSWAHL_TEXT_COLOR, rect_place="oben_mitte")
            if self.genauerer_spielmodus == AFTER_KILLED:
                return_dict[AFTER_KILLED + "0"] = self.draw_text(self.screen, "Zombiewelle nach", self.NORMAL_TEXT, int(self.WIDTH * 2 / 4), int(self.HEIGHT * 0.62), color=AUSWAHL_TEXT_GREEN, rect_place="oben_mitte")
                return_dict[AFTER_KILLED + "1"] = self.draw_text(self.screen, "töten aller Zombies", self.NORMAL_TEXT, int(self.WIDTH * 2 / 4), int(self.HEIGHT * 0.62) + self.NORMAL_TEXT + 5, color=AUSWAHL_TEXT_GREEN, rect_place="oben_mitte")
            else:
                return_dict[AFTER_KILLED + "0"] = self.draw_text(self.screen, "Zombiewelle nach", self.NORMAL_TEXT, int(self.WIDTH * 2 / 4), int(self.HEIGHT * 0.62), color=AUSWAHL_TEXT_COLOR, rect_place="oben_mitte")
                return_dict[AFTER_KILLED + "1"] = self.draw_text(self.screen, "töten aller Zombies", self.NORMAL_TEXT, int(self.WIDTH * 2 / 4), int(self.HEIGHT * 0.62) + self.NORMAL_TEXT + 5, color=AUSWAHL_TEXT_COLOR, rect_place="oben_mitte")

        # Karte
        self.draw_text(self.screen, "KARTE", int(self.BIG_TEXT * 1.2), int(self.WIDTH / 2), int(self.HEIGHT * 0.74), color=AUSWAHL_TEXT_COLOR)
        for map_count, karten_name in enumerate(MAP_NAMES):
            if self.map_name == karten_name and not loading:
                return_dict["Map" + str(map_count)] = self.draw_text(self.screen, karten_name, self.NORMAL_TEXT, int(self.WIDTH * (map_count + 1) / (len(MAP_NAMES) + 1)), int(self.HEIGHT * 0.84), color=AUSWAHL_TEXT_GREEN, rect_place="mitte")
            else:
                return_dict["Map" + str(map_count)] = self.draw_text(self.screen, karten_name, self.NORMAL_TEXT, int(self.WIDTH * (map_count + 1) / (len(MAP_NAMES) + 1)), int(self.HEIGHT * 0.84), color=AUSWAHL_TEXT_COLOR, rect_place="mitte")

        if loading:
            self.draw_text(self.screen, "Lädt ...", self.HUGE_TEXT, int(self.WIDTH / 2), int(self.HEIGHT * 0.94), rect_place="mitte", color=AUSWAHL_TEXT_RED)
        else:
            return_dict["Spielen"] = self.draw_text(self.screen, "Spielen", self.HUGE_TEXT, int(self.WIDTH / 2), int(self.HEIGHT * 0.94), rect_place="mitte", color=AUSWAHL_TEXT_COLOR)
        pygame.display.flip()

        return return_dict

    def make_start_game_selection(self):
        while True:
            self.clock.tick(FPS)
            maus_rects = self.draw_start_game_screen()

            pressed = self.check_key_or_mouse_pressed([pygame.K_RETURN])

            if MAUS_LEFT in pressed:
                if self.check_maus_pos_on_rect(pressed[MAUS_LEFT], maus_rects["Grafik"]):
                    if self.schoene_grafik:
                        self.schoene_grafik = False
                    else:
                        self.schoene_grafik = True

                if self.check_maus_pos_on_rect(pressed[MAUS_LEFT], maus_rects["Maus"]):
                    if self.with_maussteuerung:
                        self.with_maussteuerung = False
                    else:
                        self.with_maussteuerung = True

                if self.check_maus_pos_on_rect(pressed[MAUS_LEFT], maus_rects["Hilfe"]):
                    self.make_spielerklaerung()

                for schwierigkeitsstufe in range(1, 6):
                    if self.check_maus_pos_on_rect(pressed[MAUS_LEFT], maus_rects["Schwierigkeit_" + str(schwierigkeitsstufe)]):
                        self.schwierigkeit = schwierigkeitsstufe

                if self.check_maus_pos_on_rect(pressed[MAUS_LEFT], maus_rects[MAP_MODUS]):
                    self.spielmodus = MAP_MODUS

                if self.check_maus_pos_on_rect(pressed[MAUS_LEFT], maus_rects[ARENA_MODUS]):
                    self.spielmodus = ARENA_MODUS

                if self.check_maus_pos_on_rect(pressed[MAUS_LEFT], maus_rects[AFTER_TIME + "0"]) or self.check_maus_pos_on_rect(pressed[MAUS_LEFT], maus_rects[AFTER_TIME + "1"]):
                    self.genauerer_spielmodus = AFTER_TIME

                if self.check_maus_pos_on_rect(pressed[MAUS_LEFT], maus_rects[AFTER_KILLED + "0"]) or self.check_maus_pos_on_rect(pressed[MAUS_LEFT], maus_rects[AFTER_KILLED + "1"]):
                    self.genauerer_spielmodus = AFTER_KILLED

                for map_count, karten_name in enumerate(MAP_NAMES):
                    if self.check_maus_pos_on_rect(pressed[MAUS_LEFT], maus_rects["Map" + str(map_count)]):
                        self.map_name = karten_name

            if MAUS_ROLL_UP in pressed:
                self.schwierigkeit += 1
                if self.schwierigkeit > 5:
                    self.schwierigkeit = 5

            if MAUS_ROLL_DOWN in pressed:
                self.schwierigkeit -= 1
                if self.schwierigkeit < 1:
                    self.schwierigkeit = 1

            if (MAUS_LEFT in pressed and self.check_maus_pos_on_rect(pressed[MAUS_LEFT], maus_rects["Spielen"])) or pressed[pg.K_RETURN]:
                for player_num in range(len(self.players)):
                    self.paused[player_num] = False
                self.draw_start_game_screen(loading=True)
                if self.map_name == "Toturial":
                    self.spielmodus = TUTORIAL
                break

    def make_lehrer_selection_pictures(self):
        if self.multiplayer:
            lehrer_asuwahl_breite = int(self.WIDTH / self.num_players_in_multiplayer)
        else:
            lehrer_asuwahl_breite = self.WIDTH

        for lehrer in LEHRER_NAMEN:
            surf = pygame.Surface((lehrer_asuwahl_breite, 300), pygame.SRCALPHA)
            surf.convert_alpha()
            #  () = Bild des Spielers
            #  ██ = Neutrales, Schlechtes, Waffe
            #  |___| = Power Up
            #
            #  normal size:                smaler:                tiny:
            #  #########################   ####################   ###############
            #  #Herr Lefka () █ █ |   |#   #Herr Lefka () █ █ #   #Herr Lefka ()#
            #  #Beschreibung......|   |#   #Beschreibung.|   |#   # █ █ █  |   |#
            #  #Infos.............|___|#   #.............|   |#   #Beschrei|   |#
            #  #########################   #Infos........|___|#   #ung.....|___|#
            #                              #..................#   #........     #
            #                              ####################   #Infos........#
            #                                                     #.............#
            #                                                     ###############

            # Name
            self.draw_text(surf, LEHRER[lehrer]["anrede"] + " " + LEHRER[lehrer]["name"], self.HUGE_TEXT, 15, 15, rect_place="oben_links", color=AUSWAHL_TEXT_COLOR)
            # Bild des Lehrers
            surf.blit(PLAYER_IMGES[lehrer], (self.longest_lehrer_name + 30, 15))

            # Kleine Bilder: Bei normal size und smaler sind die kleinen Bilder noch rechts neben dem Lehrername, bei tiny darunter
            # Waffe (Bildgroesse passend berechnen)
            if isinstance(BULLET_IMGES[lehrer], type(dict)):
                bild_hoehe = BULLET_IMGES[lehrer][list(BULLET_IMGES[lehrer])[0]].get_height()
                bild_breite = BULLET_IMGES[lehrer][list(BULLET_IMGES[lehrer])[0]].get_width()
            else:
                bild_hoehe = BULLET_IMGES[lehrer].get_height()
                bild_breite = BULLET_IMGES[lehrer].get_width()
            if bild_hoehe != bild_breite:
                if bild_breite > bild_hoehe:
                    end_hoehe = int((25 / bild_breite) * bild_hoehe)
                    end_breite = 25
                else:
                    end_breite = int((25 / bild_hoehe) * bild_breite)
                    end_hoehe = 25
            else:
                end_hoehe = 25
                end_breite = 25
            # Gesamtbreite von den drei kleinen Bilder berechnen (Waffe,Neutral,Schlechtes)
            total_width = 15 + 49 + 10 + 49 + 20 + 25 + 5 + self.longest_weapon_name
            # _  ↓  _  ↓  _  ↓ _         ↓
            # Neutr Schlecht Waffe     Waffenname
            if self.longest_lehrer_name + 30 + 49 + 35 + total_width < lehrer_asuwahl_breite:
                kleine_bilder_tiefer = False
                distance_from_right_side = 0
                if self.longest_lehrer_name + 30 + 49 + 35 + total_width + 122 < lehrer_asuwahl_breite:  # normal size (Power-up passt auchnoch daneben)
                    distance_from_right_side = 125
                # Waffe zeichnen
                if isinstance(BULLET_IMGES[lehrer], type(dict)):
                    surf.blit(pygame.transform.scale(BULLET_IMGES[lehrer][list(BULLET_IMGES[lehrer])[0]], (end_breite, end_hoehe)), (lehrer_asuwahl_breite - distance_from_right_side - 15 - 49 - 10 - 49 - 20 - 25, 22))
                else:
                    surf.blit(pygame.transform.scale(BULLET_IMGES[lehrer], (end_breite, end_hoehe)), (lehrer_asuwahl_breite - distance_from_right_side - 15 - 49 - 10 - 49 - 20 - 25, 22))
                self.draw_text(surf, "Waffe: " + str(LEHRER[lehrer]["weapon_name"]), self.SMALL_TEXT, lehrer_asuwahl_breite - distance_from_right_side - 15 - 49 - 10 - 49 - 20 - 25 - 5, 22, rect_place="oben_rechts", font_name=ARIAL_FONT, color=AUSWAHL_TEXT_COLOR)
                # Neutrales Objekt zeichnen
                surf.blit(PEROSNEN_OBJECT_IMGES[lehrer]["icon"], (lehrer_asuwahl_breite - distance_from_right_side - 15 - 49, 12))
                # Schlechtes Objekt zeichnen
                surf.blit(PERSONEN_OBSTACLE_IMGES[lehrer]["icon"], (lehrer_asuwahl_breite - distance_from_right_side - 15 - 49 - 10 - 49, 12))
            else:  # Bilder muessen drunter gezeichnet werden
                kleine_bilder_tiefer = True
                # Waffe zeichnen
                if isinstance(BULLET_IMGES[lehrer], type(dict)):
                    surf.blit(pygame.transform.scale(BULLET_IMGES[lehrer][list(BULLET_IMGES[lehrer])[0]], (end_breite, end_hoehe)), (15, 22 + max([self.HUGE_TEXT + 10, 50])))
                else:
                    surf.blit(pygame.transform.scale(BULLET_IMGES[lehrer], (end_breite, end_hoehe)), (15, 22 + max([self.HUGE_TEXT + 10, 50])))
                self.draw_text(surf, "Waffe: " + str(LEHRER[lehrer]["weapon_name"]), self.SMALL_TEXT, 15 + 25 + 5, 22 + max([self.HUGE_TEXT + 10, 50]), rect_place="oben_links", font_name=ARIAL_FONT, color=AUSWAHL_TEXT_COLOR)
                # Neutrales Objekt zeichnen
                surf.blit(PEROSNEN_OBJECT_IMGES[lehrer]["icon"], (15 + 25 + 5 + self.longest_weapon_name + 20, 12 + max([self.HUGE_TEXT + 10, 50])))
                # Schlechtes Objekt zeichnen
                surf.blit(PERSONEN_OBSTACLE_IMGES[lehrer]["icon"], (15 + 25 + 5 + self.longest_weapon_name + 20 + 49 + 10, 12 + max([self.HUGE_TEXT + 10, 50])))

            # Power-Up
            if self.longest_lehrer_name + 30 + 49 + 35 + total_width + 122 < lehrer_asuwahl_breite:  # normal size -> power_up oben rechts
                power_up_img_oben = True
                surf.blit(PERSONEN_POWER_UP_ICONS[lehrer], (lehrer_asuwahl_breite - 125, 15))
            else:  # power_up 50 pixel weiter unten rechts
                power_up_img_oben = False
                surf.blit(PERSONEN_POWER_UP_ICONS[lehrer], (lehrer_asuwahl_breite - 125, 15 + max([self.HUGE_TEXT + 10, 50])))

            # Beschreibung
            # herausfinden wie viele Zeichen noch vor das Power-Up Bild passen
            lehrer_beschreibung = LEHRER[lehrer]["personen_beschreibung"]
            platz_fuer_beschreibung = lehrer_asuwahl_breite - 125
            # umbrechen
            letzter_umbruch = 0
            einzelne_texte = []
            for letter_count, letter in enumerate(lehrer_beschreibung):
                if self.get_text_rect(lehrer_beschreibung[letzter_umbruch:letter_count], self.SMALL_TEXT).width > platz_fuer_beschreibung:
                    einzelne_texte.append(lehrer_beschreibung[letzter_umbruch:letter_count])
                    letzter_umbruch = letter_count
            einzelne_texte.append(lehrer_beschreibung[letzter_umbruch:len(lehrer_beschreibung)])
            # ausgeben
            unteres_ende_beschreibung = 0
            for text_count, text in enumerate(einzelne_texte):
                if not kleine_bilder_tiefer:
                    rect = self.draw_text(surf, text, self.SMALL_TEXT, 15, 15 + self.HUGE_TEXT + 10 + text_count * (self.SMALL_TEXT + 5), rect_place="oben_links", font_name=ARIAL_FONT, color=AUSWAHL_TEXT_COLOR)
                else:
                    rect = self.draw_text(surf, text, self.SMALL_TEXT, 15, 15 + self.HUGE_TEXT + 10 + max([self.HUGE_TEXT + 10, 50]) + text_count * (self.SMALL_TEXT + 5), rect_place="oben_links", font_name=ARIAL_FONT, color=AUSWAHL_TEXT_COLOR)
                unteres_ende_beschreibung = rect.bottom

            # Kurzinfo
            self.screen.blit(SMALL_HEART_IMG, (15, unteres_ende_beschreibung + 16))
            infotexte = [str(LEHRER[lehrer]["player_health"]), "Geschw:" + str(LEHRER[lehrer]["player_speed"]), "Powerup zeit:" + str(round(LEHRER[lehrer]["power_up_time"] / 1000, 1)), "Nachladezeit:" + str(LEHRER[lehrer]["weapon_rate"]), "Ungenauigkeit:" + str(LEHRER[lehrer]["weapon_spread"]),
                         "Schussweite:" + str(round((LEHRER[lehrer]["weapon_bullet_speed"] * LEHRER[lehrer]["weapon_lifetime"]) / 1000)), "Schaden:" + str(LEHRER[lehrer]["weapon_damage"])]
            rechte_kante_letzter_text = 28
            zeile = 0
            unteres_ende = 0
            for text in infotexte:
                if rechte_kante_letzter_text + 7 + self.get_text_rect(text, self.SMALL_TEXT, ARIAL_FONT).width > platz_fuer_beschreibung:
                    zeile += 1
                    rechte_kante_letzter_text = 8
                rect = self.draw_text(surf, text, self.SMALL_TEXT, rechte_kante_letzter_text + 7, unteres_ende_beschreibung + 25 + (self.SMALL_TEXT + 5) * zeile, rect_place="mitte_links", font_name=ARIAL_FONT, color=AUSWAHL_TEXT_COLOR)
                rechte_kante_letzter_text = rect.right
                unteres_ende = rect.bottom

            gesmat_hoehe = 122
            if not power_up_img_oben:
                gesmat_hoehe += 50
            if unteres_ende > gesmat_hoehe:
                gesmat_hoehe = unteres_ende
            gesmat_hoehe += 10

            cropped = pygame.Surface((lehrer_asuwahl_breite, gesmat_hoehe), pygame.SRCALPHA)
            cropped.convert_alpha()
            cropped.blit(surf, (0, 0))
            self.lehrer_selection_surfaces[lehrer] = cropped

    def draw_lehrer_selection(self, surf, selected, player_num, such_text=""):
        return_dict = {}

        if self.multiplayer:
            linker_rand = int(self.WIDTH / len(self.players) * player_num)
            lehrer_asuwahl_breite = int(self.WIDTH / len(self.players))
        else:
            linker_rand = 0
            lehrer_asuwahl_breite = self.WIDTH

        subsurface = self.background.subsurface((linker_rand, 0, int(self.WIDTH / len(self.players)), self.HEIGHT))
        subsurface_rect = subsurface.get_rect()
        surf.blit(subsurface, (subsurface_rect.x + linker_rand, subsurface_rect.y))

        if such_text == "":
            untere_kante_letzter_lehrer = 0
        else:
            self.draw_text(surf, "Suche: " + such_text, self.BIG_TEXT, linker_rand + 10, 10, rect_place="oben_links", color=AUSWAHL_TEXT_COLOR)
            pygame.draw.line(surf, LEHRER_AUSWAHL_LINE_COLOR, (linker_rand, self.BIG_TEXT + 20), (linker_rand + lehrer_asuwahl_breite, self.BIG_TEXT + 20), 3)
            untere_kante_letzter_lehrer = self.BIG_TEXT + 20

        if selected not in LEHRER:
            lehrer = LEHRER_NAMEN[len(LEHRER_NAMEN) - 1]
        else:
            if LEHRER_NAMEN.index(selected) - 1 < 0:
                lehrer = LEHRER_NAMEN[len(LEHRER_NAMEN) - 1]
            else:
                lehrer = LEHRER_NAMEN[LEHRER_NAMEN.index(selected) - 1]

        is_there_a_match = False
        for name in LEHRER_NAMEN:
            anderer_spieler_hat_schon_diese_person = False
            unlocked = True
            passt_zu_suche = True
            if self.multiplayer:
                for count, player in enumerate(self.players):
                    if player.lehrer_name == name and count != player_num:
                        anderer_spieler_hat_schon_diese_person = True
            if LEHRER[name]["bedingungen_fuer_unlock"] != None:
                unlocked = name in self.lehrer_unlocked_sofar
            if such_text != "":
                if not such_text.lower() in name.lower():
                    passt_zu_suche = False
            if anderer_spieler_hat_schon_diese_person == False and unlocked == True and passt_zu_suche == True:
                is_there_a_match = True
        if not is_there_a_match:
            self.draw_text(surf, "kein Suchergebnis", self.BIG_TEXT, linker_rand + 10, untere_kante_letzter_lehrer + 20, rect_place="oben_links", color=AUSWAHL_TEXT_COLOR)
            pygame.display.flip()
            return []

        while True:
            if LEHRER_NAMEN.index(lehrer) + 1 >= len(LEHRER_NAMEN):
                lehrer = LEHRER_NAMEN[0]
            else:
                lehrer = LEHRER_NAMEN[LEHRER_NAMEN.index(lehrer) + 1]

            while True:
                anderer_spieler_hat_schon_diese_person = False
                unlocked = True
                passt_zu_suche = True
                if self.multiplayer:
                    for count, player in enumerate(self.players):
                        if player.lehrer_name == lehrer and count != player_num:
                            anderer_spieler_hat_schon_diese_person = True
                if LEHRER[lehrer]["bedingungen_fuer_unlock"] != None:
                    unlocked = lehrer in self.lehrer_unlocked_sofar
                if such_text != "":
                    if not such_text.lower() in lehrer.lower():
                        passt_zu_suche = False
                if anderer_spieler_hat_schon_diese_person == False and unlocked == True and passt_zu_suche == True:
                    break
                else:
                    if LEHRER_NAMEN.index(lehrer) + 1 >= len(LEHRER_NAMEN):
                        lehrer = LEHRER_NAMEN[0]
                    else:
                        lehrer = LEHRER_NAMEN[LEHRER_NAMEN.index(lehrer) + 1]

            if lehrer not in return_dict.values():
                start_hoehe_dieses_lehrer = untere_kante_letzter_lehrer

                self.screen.blit(self.lehrer_selection_surfaces[lehrer], (linker_rand, start_hoehe_dieses_lehrer))

                untere_kante_letzter_lehrer = start_hoehe_dieses_lehrer + self.lehrer_selection_surfaces[lehrer].get_height()
                untere_kante_letzter_lehrer += 10
                if untere_kante_letzter_lehrer >= self.HEIGHT:
                    break

                return_dict[(start_hoehe_dieses_lehrer, untere_kante_letzter_lehrer)] = lehrer

                # Linie
                pygame.draw.line(surf, LEHRER_AUSWAHL_LINE_COLOR, (linker_rand, untere_kante_letzter_lehrer), (linker_rand + lehrer_asuwahl_breite, untere_kante_letzter_lehrer), 2)

            else:
                break

        pygame.display.flip()

        return return_dict

    def make_lehrer_selection(self, surf, player_num):
        self.draw_lehrer_selection(surf, None, player_num)
        alter_lehrer = self.players[player_num].lehrer_name
        selected_lehrer_num = list(LEHRER).index(alter_lehrer)
        last_selected_lehrer_num = selected_lehrer_num
        self.draw_lehrer_selection(surf, list(LEHRER)[selected_lehrer_num], player_num)
        last_selection_change = time()
        such_text = ""
        while True:
            lehrer_y_positions = self.draw_lehrer_selection(surf, list(LEHRER)[selected_lehrer_num], player_num, such_text)

            pressed = self.check_key_or_mouse_pressed([pygame.K_RETURN, pygame.K_DOWN, pygame.K_UP, pygame.K_BACKSPACE, "text"])

            # Auswahl aendern
            if (pressed[pygame.K_UP] or MAUS_ROLL_UP in pressed) and time() - last_selection_change > 0.2 and lehrer_y_positions != []:
                # Lehrer auswahl aendern, dabei darauf achten das Lehrer schon freigeschaltet ist und noch nicht von anderen Spielern ausgewaehlt wurde
                last_selection_change = time()
                if selected_lehrer_num > 0:
                    selected_lehrer_num -= 1
                else:
                    selected_lehrer_num = len(LEHRER_NAMEN) - 1
                while True:
                    anderer_spieler_hat_schon_diese_person = False
                    unlocked = True
                    passt_zu_suche = True
                    if self.multiplayer:
                        for count, player in enumerate(self.players):
                            if player.lehrer_name == LEHRER_NAMEN[selected_lehrer_num] and count != player_num:
                                anderer_spieler_hat_schon_diese_person = True
                    if LEHRER[LEHRER_NAMEN[selected_lehrer_num]]["bedingungen_fuer_unlock"] != None:
                        unlocked = LEHRER_NAMEN[selected_lehrer_num] in self.lehrer_unlocked_sofar
                    if such_text != "":
                        if not such_text.lower() in LEHRER_NAMEN[selected_lehrer_num].lower():
                            passt_zu_suche = False
                    if anderer_spieler_hat_schon_diese_person == False and unlocked == True and passt_zu_suche == True:
                        break
                    else:
                        if selected_lehrer_num > 0:
                            selected_lehrer_num -= 1
                        else:
                            selected_lehrer_num = len(LEHRER_NAMEN) - 1

            if (pressed[pygame.K_DOWN] or MAUS_ROLL_DOWN in pressed) and time() - last_selection_change > 0.2 and lehrer_y_positions != []:
                # Lehrer auswahl aendern, dabei darauf chaten das Lehrer schon freigeschaltet ist und noch nicht von anderen Spielern ausgewaehlt wurde
                last_selection_change = time()
                if selected_lehrer_num < len(list(LEHRER)) - 1:
                    selected_lehrer_num += 1
                else:
                    selected_lehrer_num = 0
                while True:
                    anderer_spieler_hat_schon_diese_person = False
                    unlocked = True
                    passt_zu_suche = True
                    if self.multiplayer:
                        for count, player in enumerate(self.players):
                            if player.lehrer_name == LEHRER_NAMEN[selected_lehrer_num] and count != player_num:
                                anderer_spieler_hat_schon_diese_person = True
                    if LEHRER[LEHRER_NAMEN[selected_lehrer_num]]["bedingungen_fuer_unlock"] != None:
                        unlocked = LEHRER_NAMEN[selected_lehrer_num] in self.lehrer_unlocked_sofar
                    if such_text != "":
                        if not such_text.lower() in LEHRER_NAMEN[selected_lehrer_num].lower():
                            passt_zu_suche = False
                    if anderer_spieler_hat_schon_diese_person == False and unlocked == True and passt_zu_suche == True:
                        break
                    else:
                        if selected_lehrer_num < len(list(LEHRER)) - 1:
                            selected_lehrer_num += 1
                        else:
                            selected_lehrer_num = 0

            # Nach Lehrer suchen durch Text eingeben
            if pressed["text"] != False:
                such_text += pressed["text"]
            if pressed[pygame.K_BACKSPACE]:
                such_text = such_text[:-2]

            # Auswaehlen
            if MAUS_LEFT in pressed:
                for lehrer_y_position in lehrer_y_positions:
                    if pressed[MAUS_LEFT][1] < lehrer_y_position[1] and pressed[MAUS_LEFT][1] > lehrer_y_position[0]:
                        self.change_to_other_lehrer(lehrer_y_positions[lehrer_y_position], alter_lehrer, self.players[player_num])
                        self.paused[player_num] = False
                        return

            # Zurueck
            if pressed[pygame.K_RETURN]:
                self.paused[player_num] = False
                return

    def change_to_other_lehrer(self, lehrer_name, alter_lehrer, player):
        self.werte_since_last_lehrer_change[player] = {"shoots": 0, "treffer": 0, "collected_objects": 0, "num_obstacles_stept_on": 0, "time_lehrer_change": time(), "zombies_killed": 0, "collected_health_packs": 0, "num_power_ups": 0}
        player.lehrer_name = lehrer_name
        player.weapon_upgrade_unlocked = False
        player.update_image()
        if player.health / LEHRER[alter_lehrer]["player_health"] * LEHRER[player.lehrer_name]["player_health"] > LEHRER[player.lehrer_name]["player_health"]:
            player.health = LEHRER[player.lehrer_name]["player_health"]
        else:
            player.health = player.health / LEHRER[alter_lehrer]["player_health"] * LEHRER[player.lehrer_name]["player_health"]
        for obstacle in self.personen_obstacles:
            obstacle.update_image()
        for object in self.personen_objects:
            object.update_image()
        for zombie in self.zombies:
            zombie.update_image()
        self.update_live_bar_image(player, self.players.index(player))
        self.update_forground_text_img()

    def make_spielerklaerung(self):

        while True:
            self.screen.blit(self.background, (0, 0))
            orig_width = ERKLAERUNG.get_width()
            orig_height = ERKLAERUNG.get_height()
            width = int(self.WIDTH)
            if orig_width / width < orig_height / self.HEIGHT:
                height = int(self.HEIGHT)
                width = int(orig_width * (self.HEIGHT / orig_height))
                pos = (int((self.WIDTH - width) / 2), 0)
                self.screen.blit(pygame.transform.scale(ERKLAERUNG, (width, height)), pos)
            else:
                height = int(orig_height * (width / orig_width))
                pos = (0, int((self.HEIGHT - height) / 2))
                self.screen.blit(pygame.transform.scale(ERKLAERUNG, (width, height)), pos)
            pygame.display.flip()

            self.clock.tick(FPS)
            pressed = self.check_key_or_mouse_pressed([pygame.K_ESCAPE])

            if MAUS_LEFT in pressed:
                if self.check_maus_pos_on_rect(pressed[MAUS_LEFT], pygame.Rect((int(pos[0] + (width / 2) - (0.3 * width)), int(pos[1] + height - 0.3 * height)), (int(0.6 * width), int(0.6 * height)))):
                    break

    def make_time_measure(self):
        if self.measure_times:
            return round(time() * 1000, 2)
        return None

    def calculate_fit_size(self, max_width_faktor, max_height_faktor):
        size = max_width_faktor * self.WIDTH
        if size / self.HEIGHT > max_height_faktor:
            size = max_height_faktor * self.HEIGHT
        return int(size)

    def update_text_sizes(self):
        # Textgroessen
        self.GIANT_TEXT = self.calculate_fit_size(0.0666, 0.1)
        self.HUGE_TEXT = self.calculate_fit_size(0.0416, 0.0625)
        self.BIG_TEXT = self.calculate_fit_size(0.0333, 0.05)
        self.NORMAL_TEXT = self.calculate_fit_size(0.02708, 0.040625)
        self.SMALL_TEXT = self.calculate_fit_size(0.0208, 0.03125)

    def window_resize(self, width, height):
        self.WIDTH = width
        self.HEIGHT = height
        self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT), pygame.RESIZABLE)
        self.GRIDWIDTH = int(start_width / TILESIZE)
        self.GRIDHEIGHT = int(start_height / TILESIZE)
        self.small_map_sichtweite = self.calculate_fit_size(SMALL_MAP_SICHTWEITE_FAKTOR, SMALL_MAP_SICHTWEITE_FAKTOR)
        self.maussteuerung_circle_radius = self.calculate_fit_size(0.35, 0.35)
        self.background = pygame.transform.scale(background, (self.WIDTH, self.HEIGHT))
        self.background_rect = self.background.get_rect()
        self.update_text_sizes()
        self.number_surfaces = {}
        self.bigest_num_length = 0
        for x in range(10):
            rect = self.get_text_rect(x, self.BIG_TEXT)
            if rect.width > self.bigest_num_length:
                self.bigest_num_length = rect.width
        for x in range(10):
            surf = pygame.Surface((self.bigest_num_length, int(self.BIG_TEXT * 1.2)), pygame.SRCALPHA)
            self.draw_text(surf, x, self.BIG_TEXT, 0, 0, rect_place="oben_links")
            self.number_surfaces[x] = surf
        if self.WIDTH / self.HEIGHT < 0.4555555:
            self.live_bar_img_width = int(0.375 * self.WIDTH)
            self.live_bar_img_height = int(self.live_bar_img_width / 360 * 164)
        else:
            self.live_bar_img_height = int(0.25625 * self.HEIGHT)
            self.live_bar_img_width = int(self.live_bar_img_height / 164 * 360)
        self.longest_lehrer_name = 0
        self.longest_weapon_name = 0
        self.longest_object_name = 0
        for lehrer in LEHRER:
            width = self.get_text_rect(LEHRER[lehrer]["anrede"] + " " + lehrer, self.HUGE_TEXT).width
            if width > self.longest_lehrer_name:
                self.longest_lehrer_name = width
            width = self.get_text_rect("Waffe: " + str(LEHRER[lehrer]["weapon_name"]), self.SMALL_TEXT, ARIAL_FONT).width
            if width > self.longest_weapon_name:
                self.longest_weapon_name = width
            width = self.get_text_rect(str(LEHRER[lehrer]["personen_item_text"]) + ":" + str(99), self.BIG_TEXT).width
            if width > self.longest_object_name:
                self.longest_object_name = width
        self.make_lehrer_selection_pictures()
        if self.game_status != BEFORE_FIRST_GAME:
            self.update_forground_text_img()
            for count, player in enumerate(self.players):
                self.update_live_bar_image(player, count)
            for count, camera in enumerate(self.camera):
                camera.update(self.players[count])
            if self.multiplayer:
                self.small_map_size = self.calculate_fit_size(0.23, 0.23)
            else:
                self.small_map_size = self.calculate_fit_size(0.3, 0.3)
        self.clock.tick(FPS)

    ########## Hier startet das eigentliche Spiel ##########
    def start_game(self):
        pygame.mixer.music.play(loops=-1)

        if self.multiplayer and self.num_players_in_multiplayer > 2:
            self.schoene_grafik = False
        self.game_status = BEFORE_FIRST_GAME
        self.make_start_game_selection()

        if self.multiplayer:
            self.small_map_size = self.calculate_fit_size(0.23, 0.23)
        else:
            self.small_map_size = self.calculate_fit_size(0.3, 0.3)
        self.small_map_circle_sizes = [int(self.small_map_size * 0.3), int(self.small_map_size * 0.25), int(self.small_map_size * 0.25)]
        self.small_map_sichtweite = self.small_map_sichtweite
        self.make_lehrer_selection_pictures()

        while True:
            # Spiel beginnen
            if self.spielmodus == TUTORIAL:
                self.game_status = TUTORIAL_WALK
            else:
                self.game_status = PLAYING
            if self.players != []:
                # Die gleichen Lehrer wie im letzen Spiuel solange diese auch direkt freigeschaltet sind
                if not self.multiplayer:
                    if LEHRER[self.players[0].lehrer_name]["bedingungen_fuer_unlock"] == None:
                        self.new([self.players[0].lehrer_name])
                    else:
                        i = 0
                        namen_gefunden = False
                        while not namen_gefunden and i < len(LEHRER_NAMEN):
                            if LEHRER[LEHRER_NAMEN[i]]["bedingungen_fuer_unlock"] == None:
                                self.new([LEHRER_NAMEN[i]])
                                namen_gefunden = True
                            i += 1
                else:
                    lehrer_namen = []
                    for player_num, player in enumerate(self.players):
                        if LEHRER[player.lehrer_name]["bedingungen_fuer_unlock"] == None:
                            lehrer_namen.append(player.lehrer_name)
                        else:
                            i = 0
                            namen_gefunden = False
                            while not namen_gefunden and i < len(LEHRER_NAMEN):
                                anderer_spieler_hat_schon_diese_person = False
                                unlocked = False
                                for count, playerrr in enumerate(self.players):
                                    if playerrr.lehrer_name == LEHRER_NAMEN[i] and count != player_num:
                                        anderer_spieler_hat_schon_diese_person = True
                                if LEHRER[LEHRER_NAMEN[i]]["bedingungen_fuer_unlock"] == None:
                                    unlocked = True
                                if anderer_spieler_hat_schon_diese_person == False and unlocked == True:
                                    lehrer_namen.append(LEHRER_NAMEN[i])
                                    namen_gefunden = True
                                i += 1
                    self.new(lehrer_namen)
            else:
                # Fuer jeden Spieler Lehrer auswaehlen, dabei darauf achten, dass Lehrer freigeschaltet sind und nicht mehrer Spieler den gleichen Spieler bekommen
                lehrer_namen = []
                if self.multiplayer:
                    i = 0
                    num_namen = 0
                    while num_namen < self.num_players_in_multiplayer and i < len(LEHRER_NAMEN):
                        if LEHRER[LEHRER_NAMEN[i]]["bedingungen_fuer_unlock"] == None:
                            num_namen += 1
                            lehrer_namen.append(LEHRER_NAMEN[i])
                        i += 1
                else:
                    i = 0
                    namen_gefunden = False
                    while not namen_gefunden and i < len(LEHRER_NAMEN):
                        if LEHRER[LEHRER_NAMEN[i]]["bedingungen_fuer_unlock"] == None:
                            lehrer_namen.append(LEHRER_NAMEN[i])
                            namen_gefunden = True
                        i += 1
                self.new(lehrer_namen)
            for count, player in enumerate(self.players):
                self.update_live_bar_image(player, count)
            self.clock.tick(FPS)
            self.level_start_time = time()
            self.last_zombie_wave_time = time()
            self.level_start_num_zombies = len(self.zombies)
            self.update_forground_text_img()

            ######## Hauptschleife des Spiels #######
            while self.game_status == PLAYING or self.game_status == COLLECTING_AT_END or (self.spielmodus == TUTORIAL and self.game_status != PLAYER_DIED):
                self.dt = self.clock.tick(FPS) / 1000.0

                pressed = self.check_key_or_mouse_pressed([pygame.K_BACKSPACE, pygame.K_RETURN, pygame.K_y, pygame.K_x, pygame.K_c, pygame.K_LEFT, pygame.K_RIGHT, pygame.K_UP, pygame.K_DOWN])

                time1 = self.make_time_measure()
                # Alle Spielaktionen hier ausfuehren
                if False in self.paused:
                    # alle sprites updaten
                    if (self.spielmodus == TUTORIAL and (self.game_status == TUTORIAL_POWER_UP or self.game_status == TUTORIAL_SHOOT)) or self.spielmodus != TUTORIAL:
                        for player in self.players:
                            if pygame.mouse.get_pressed()[0] or pygame.key.get_pressed()[pygame.K_SPACE]:
                                player.shoot()
                    self.all_sprites.update()
                    for count, camera in enumerate(self.camera):
                        camera.update(self.players[count])
                    self.detect_and_react_collisions()
                    # Im Arena Modus neue Zombiewellen losschicken
                    if self.spielmodus == ARENA_MODUS and self.num_zombie_wave < 3:
                        if not time() - self.countdown_start_time <= 6:  # wenn nicht gerade im Countdown schauen, ob Zeit abgelaufen, bzw. zombies getoetet
                            if self.genauerer_spielmodus == AFTER_TIME and time() - self.last_zombie_wave_time >= TIME_BETWEEN_ZOMBIE_WAVES:
                                self.countdown_start_time = time()
                                self.make_new_zombie_wave()
                                self.num_zombie_wave += 1
                                self.last_zombie_wave_time = time() + 5
                            elif self.genauerer_spielmodus == AFTER_KILLED and len(self.zombies) == 0:
                                self.countdown_start_time = time()
                                self.make_new_zombie_wave()
                                self.num_zombie_wave += 1
                                self.last_zombie_wave_time = time() + 5
                    # Im Tutorial weiter machen:
                    if self.spielmodus == TUTORIAL:
                        if self.game_status == TUTORIAL_WALK and time() - self.werte_since_last_lehrer_change[self.players[0]]["time_lehrer_change"] > 8:
                            self.game_status = TUTORIAL_COLLECT
                        elif self.game_status == TUTORIAL_COLLECT and self.werte_since_last_lehrer_change[self.players[0]]["collected_objects"] >= 4:
                            self.game_status = TUTORIAL_SHOOT
                        elif self.game_status == TUTORIAL_SHOOT and len(self.zombies) == 0:
                            self.game_status = TUTORIAL_POWER_UP
                            self.make_new_zombie_wave()
                        elif self.game_status == TUTORIAL_POWER_UP and len(self.zombies) == 0:
                            if self.werte_since_last_lehrer_change[self.players[0]]["num_power_ups"] >= 1:
                                self.game_status = COLLECTING_AT_END
                                self.find_at_end = Find_at_End(self, self.player_pos.x, self.player_pos.y)
                            else:
                                self.make_new_zombie_wave()
                    # Power-Up benutzen
                    if (self.spielmodus == TUTORIAL and self.game_status == TUTORIAL_POWER_UP) or self.spielmodus != TUTORIAL:
                        for count, player in enumerate(self.players):
                            if MAUS_RIGHT in pressed or pressed[pygame.K_y] or pressed[pygame.K_x] or pressed[pygame.K_c]:
                                if time() * 1000 - self.last_power_up_use_time[count] >= LEHRER[player.lehrer_name]["power_up_time"]:
                                    eval("lehrer_funktionen.power_up_" + player.lehrer_name.replace(" ", "_") + "(self,player)")
                                    self.werte_since_last_lehrer_change[player]["num_power_ups"] += 1
                                    if self.spielmodus == TUTORIAL and self.game_status == TUTORIAL_POWER_UP:
                                        self.last_power_up_use_time[count] = round(time() * 1000) - LEHRER[player.lehrer_name]["power_up_time"] + 2500
                                    else:
                                        self.last_power_up_use_time[count] = round(time() * 1000)
                time2 = self.make_time_measure()
                # Pause druecken (Lehrerauswahl)
                if self.spielmodus != TUTORIAL:
                    for player_num in range(len(self.players)):
                        if pressed[pygame.K_RETURN]:
                            self.paused[player_num] = True
                            self.make_lehrer_selection(self.screen, player_num)
                            self.clock.tick(FPS)

                # Spiel abbrechen
                if pressed[pygame.K_BACKSPACE]:
                    if self.spielmodus == TUTORIAL:
                        self.spielmodus = MAP_MODUS
                        self.map_name = MAP_NAMES[0]
                    self.game_status = BEFORE_FIRST_GAME
                # Spiel gewonnen?
                if ((self.spielmodus == MAP_MODUS and (len(self.zombies) == 0 or (self.genauerer_spielmodus == AFTER_TIME and time() - self.level_start_time >= TIME_MAP_LEVEL))) or (self.spielmodus == ARENA_MODUS and self.num_zombie_wave == 3 and not self.end_gegner.alive)) and self.game_status == PLAYING:
                    self.game_status = COLLECTING_AT_END
                    if self.spielmodus == ARENA_MODUS:
                        self.find_at_end = Find_at_End(self, self.endgegner_kill_pos.x, self.endgegner_kill_pos.y)
                    else:
                        self.find_at_end = Find_at_End(self, self.player_pos.x, self.player_pos.y)
                    self.update_forground_text_img()

                # Lehrer freischalten
                if self.spielmodus != TUTORIAL:
                    for lehrer in self.lehrer_to_be_unlocked:
                        if not lehrer in self.lehrer_unlocked_sofar:
                            for player in self.players:
                                unlocked = eval(LEHRER[lehrer]["bedingungen_fuer_unlock"])
                                if unlocked:
                                    self.lehrer_unlocked_sofar.append(lehrer)
                                    self.lehrer_unlocked_last = lehrer
                                    self.time_last_lehrer_unlock = time()
                    # Waffen upgrade freischalten
                    for count, player in enumerate(self.players):
                        if not player.weapon_upgrade_unlocked:
                            unlocked = eval(LEHRER[player.lehrer_name]["weapon_upgrade"]["upgrade_bedingungen"])
                            if unlocked or player.lehrer_name in self.upgraded_weapons_lehrer_namen:
                                player.weapon_upgrade_unlocked = True
                                player.update_image()
                                self.weapon_upgrade_unlock_times[count] = time()
                                if player.lehrer_name not in self.upgraded_weapons_lehrer_namen:
                                    self.upgraded_weapons_lehrer_namen.append(player.lehrer_name)

                time3 = self.make_time_measure()
                # zeichnen
                self.draw_display()
                time4 = self.make_time_measure()

                if self.measure_times:
                    self.fps_werte.append(self.clock.get_fps())
                    self.measured_times[0].append(time4 - time1)
                    self.measured_times[1].append(time2 - time1)
                    self.measured_times[2].append(time3 - time2)
                    self.measured_times[3].append(time4 - time3)

            if self.spielmodus == TUTORIAL:
                self.spielmodus = MAP_MODUS
            self.make_start_game_selection()

    def make_new_zombie_wave(self):
        if self.num_zombie_wave == 3 - 1:
            self.end_gegner = End_Gegner(self)
        else:
            neue_zombies = []
            for tile_object in self.map.tmxdata.objects:
                obj_center = vec(tile_object.x + tile_object.width / 2, tile_object.y + tile_object.height / 2)
                if tile_object.name == 'zombie':
                    neue_zombies.append([obj_center.x, obj_center.y])
            if self.spielmodus != TUTORIAL:
                for x in range(int(0.5 * len(neue_zombies))):
                    neue_zombies.pop(randrange(len(neue_zombies)))
                for x in range(int(len(neue_zombies) * SCHWIERIGKEIT_ZOMBIE_KILLS[self.schwierigkeit - 1])):
                    neue_zombies.pop(randrange(len(neue_zombies)))
            for neuer_zombie in neue_zombies:
                if self.spielmodus != TUTORIAL:
                    Grab(self, neuer_zombie[0], neuer_zombie[1])
                else:
                    Mob(self, neuer_zombie[0], neuer_zombie[0])
        self.update_forground_text_img()

    def new(self, lehrer_namen):
        self.players = []
        self.end_gegner = None
        self.endgegner_jump_points = []
        self.endgegner_after_kill_respawn_point = []
        self.lehrer_unlocked_sofar = []
        self.weapon_upgrade_unlock_times = []
        self.upgraded_weapons_lehrer_namen = []
        self.endgegner_zombies = pygame.sprite.Group()
        self.werte_since_last_lehrer_change = {}

        # Spritegruppen
        self.all_sprites = pygame.sprite.LayeredUpdates()
        self.obstacles = pygame.sprite.Group()
        self.personen_obstacles = pygame.sprite.Group()
        self.personen_objects = pygame.sprite.Group()
        self.zombies = pygame.sprite.Group()
        self.bullets = pygame.sprite.Group()
        self.endgegner_bullets = pygame.sprite.Group()
        self.health_packs = pygame.sprite.Group()

        # Karte laden
        if self.spielmodus == MAP_MODUS:
            self.map = TiledMap(path.join(map_folder, self.map_name + '_big.tmx'))
        elif self.spielmodus == ARENA_MODUS:
            self.map = TiledMap(path.join(map_folder, self.map_name + '_small.tmx'))
        elif self.spielmodus == TUTORIAL:
            self.map = TiledMap(path.join(map_folder, 'Tutorial.tmx'))
        self.map_img = self.map.make_map()
        self.map.rect = self.map_img.get_rect()
        self.small_map_sichtweite = min([self.small_map_sichtweite, self.map_img.get_width(), self.map_img.get_height()])
        for count, tile_object in enumerate(self.map.tmxdata.objects):
            obj_center = vec(tile_object.x + tile_object.width / 2, tile_object.y + tile_object.height / 2)
            if tile_object.name == 'player':
                self.player_pos = obj_center
                if self.multiplayer:
                    for i in range(self.num_players_in_multiplayer):
                        player = Player(self, obj_center.x, obj_center.y, lehrer_namen[i], i)
                        self.players.append(player)
                        self.weapon_upgrade_unlock_times.append(0)
                        self.werte_since_last_lehrer_change[player] = {"shoots": 0, "treffer": 0, "collected_objects": 0, "num_obstacles_stept_on": 0, "time_lehrer_change": time(), "zombies_killed": 0, "collected_health_packs": 0, "num_power_ups": 0}
                else:
                    player = Player(self, obj_center.x, obj_center.y, lehrer_namen[0], 0)
                    self.players.append(player)
                    self.weapon_upgrade_unlock_times.append(0)
                    self.werte_since_last_lehrer_change[player] = {"shoots": 0, "treffer": 0, "collected_objects": 0, "num_obstacles_stept_on": 0, "time_lehrer_change": time(), "zombies_killed": 0, "collected_health_packs": 0, "num_power_ups": 0}
        for count, tile_object in enumerate(self.map.tmxdata.objects):
            obj_center = vec(tile_object.x + tile_object.width / 2, tile_object.y + tile_object.height / 2)
            if tile_object.name == 'zombie':
                Mob(self, obj_center.x, obj_center.y)
            if tile_object.name == 'obstacle':
                Obstacle(self, tile_object.x, tile_object.y, tile_object.width, tile_object.height)
            if tile_object.name == 'Personen obstacle':
                if tile_object.width > tile_object.height:
                    for obstacle_num in range(int(tile_object.width / 64)):
                        if obstacle_num == 0:
                            Personen_Obstacle(self, tile_object.x + obstacle_num * 64, tile_object.y, 64, 64, orientation=OW, is_begin=True)
                        elif obstacle_num == int(tile_object.width / 64) - 1:
                            Personen_Obstacle(self, tile_object.x + obstacle_num * 64, tile_object.y, 64, 64, orientation=OW, is_end=True)
                        else:
                            Personen_Obstacle(self, tile_object.x + obstacle_num * 64, tile_object.y, 64, 64, orientation=OW)
                else:
                    for obstacle_num in range(int(tile_object.height / 64)):
                        if obstacle_num == 0:
                            Personen_Obstacle(self, tile_object.x, tile_object.y + obstacle_num * 64, 64, 64, orientation=NS, is_begin=True)
                        elif obstacle_num == int(tile_object.height / 64) - 1:
                            Personen_Obstacle(self, tile_object.x, tile_object.y + obstacle_num * 64, 64, 64, orientation=NS, is_end=True)
                        else:
                            Personen_Obstacle(self, tile_object.x, tile_object.y + obstacle_num * 64, 64, 64, orientation=NS)
            if tile_object.name == 'Personen objekt':
                Personen_Object(self, tile_object.x, tile_object.y,
                                tile_object.width, tile_object.height)
            if tile_object.name in 'health':
                Health_Pack(self, obj_center)
            if tile_object.name == 'endgegner':
                self.endgegner_jump_points.append(obj_center)
                self.endgegner_pos = obj_center
            if tile_object.name == 'endgegner_jump_points':
                self.endgegner_jump_points.append(obj_center)
            if tile_object.name == 'endgegner_after_kill_point':
                self.endgegner_after_kill_respawn_point.append(obj_center)

        # Fehler abfangen: Spieler nicht auf der Karte, zu wenig joysticks fuer alle Spieler
        # for count,player in enumerate(self.players):
        #    try:
        #        self.all_joysticks[count]
        #    except IndexError:
        #        self.all_joysticks.append(JoystickPins(KeyboardStick()))
        if len(self.players) == 0:
            raise Exception("No place to put player in loaded map")
        if len(self.zombies) == 0:
            raise Exception("No zombie found in loaded map")

        # Bei der Arena die haelfte der Zombies wieder toeten
        if self.spielmodus == ARENA_MODUS:
            for x in range(int(0.5 * len(self.zombies))):
                choice(list(self.zombies)).kill()

        # Je nach Schwierigkeit ein paar Zombies direkt toeten, und ein paar health_packs entfernen
        if self.spielmodus != TUTORIAL:
            for x in range(int(len(self.zombies) * SCHWIERIGKEIT_ZOMBIE_KILLS[self.schwierigkeit - 1])):
                choice(list(self.zombies)).kill()
            for x in range(int(len(self.health_packs) * SCHWIERIGKEIT_HEALTH_KILLS[self.schwierigkeit - 1])):
                choice(list(self.health_packs)).kill()

        # Sonstiges
        self.num_zombie_wave = 1
        self.camera = []
        self.paused = []
        self.last_personen_object = []
        self.was_on_obstacle_last_time = []
        self.last_power_up_use_time = []
        self.collected_person_objects = []
        self.live_bar_images = []
        for player in self.players:
            self.camera.append(Camera(self.map.width, self.map.height, self))
            self.paused.append(False)
            self.last_personen_obstacle_damage.append(0)
            self.last_personen_object.append(None)
            self.was_on_obstacle_last_time.append(False)
            self.last_power_up_use_time.append(round(time() * 1000))
            self.collected_person_objects.append(0)
            self.live_bar_images.append(False)

        if self.spielmodus != TUTORIAL:
            LEVEL_START_WAV.play()

    def detect_and_react_collisions(self):
        for count, player in enumerate(self.players):
            # Spieler sammelt ein Health Pack
            hits = pygame.sprite.spritecollide(player, self.health_packs, False)
            for hit in hits:
                if player.health < LEHRER[player.lehrer_name]["player_health"]:
                    hit.kill()
                    player.add_health(LEHRER[player.lehrer_name]["health_pack_amount"])
                    eval("lehrer_funktionen.health_pack_" + player.lehrer_name.replace(" ", "_") + "(self,player)")
                    self.werte_since_last_lehrer_change[player]["collected_health_packs"] += 1

            # Zombie beruehrt Spieler
            if not (self.spielmodus == TUTORIAL and (self.game_status == TUTORIAL_WALK or self.game_status == TUTORIAL_COLLECT)):
                hits = pygame.sprite.spritecollide(player, self.zombies, False, collide_hit_rect)
                for hit in hits:
                    if random() < 0.7:
                        choice(PLAYER_HIT_WAVS).play()
                    if self.paused[count] == False:
                        player.health -= MOB_DAMAGE[self.schwierigkeit - 1]
                    hit.vel = vec(0, 0)
                    if player.health <= 0:
                        self.game_status = PLAYER_DIED
                if hits:
                    player.hit()
                    player.pos += vec(MOB_KNOCKBACK, 0).rotate(-hits[0].rot)

            # Endgegner beruehrt Spieler
            if self.spielmodus == ARENA_MODUS and self.num_zombie_wave == 3 and time() - self.end_gegner.spawn_time > 6 and self.end_gegner.alive:
                hits = pygame.sprite.spritecollide(self.end_gegner, self.players, False)
                if len(hits) > 0:
                    if count == 0:
                        self.end_gegner.mask = pygame.mask.from_surface(self.end_gegner.image)
                    hit = pygame.sprite.collide_mask(self.end_gegner, player)
                    if hit is not None:
                        if self.paused[count] == False:
                            player.health = int(player.health / 2)
                            player.pos = choice(self.endgegner_after_kill_respawn_point)
                            player.hit()

            # Endgegner schiesst den Spieler ab
            hits = pygame.sprite.spritecollide(player, self.endgegner_bullets, False, collide_hit_rect)
            for hit in hits:
                if self.paused[count] == False:
                    player.health -= ENDGEGNER_WEAPON_DAMAGE[self.schwierigkeit - 1]
                if player.health <= 0:
                    self.game_status = PLAYER_DIED
                hit.kill()

            # Spieler laeuft auf ein personenabhaegiges Hindernis (z.B Naegel am Boden)
            if self.spielmodus == TUTORIAL and self.game_status != TUTORIAL_WALK or self.spielmodus != TUTORIAL:
                hits = pygame.sprite.spritecollide(player, self.personen_obstacles, False, collide_hit_rect)
                for hit in hits:
                    if pygame.time.get_ticks() - self.last_personen_obstacle_damage[count] > 60:
                        self.last_personen_obstacle_damage[count] = pygame.time.get_ticks()
                        if random() < 0.7:
                            choice(PLAYER_HIT_WAVS).play()
                        if self.paused[count] == False:
                            player.health -= LEHRER[player.lehrer_name]["obstacle_damage"]
                        if player.health <= 0:
                            self.game_status = PLAYER_DIED
                    if LEHRER[player.lehrer_name]["obstacle_kill"]:
                        hit.kill()
                    if self.was_on_obstacle_last_time[count] == False:
                        eval("lehrer_funktionen.obstacle_" + player.lehrer_name.replace(" ", "_") + "(self,player)")
                        self.werte_since_last_lehrer_change[player]["num_obstacles_stept_on"] += 1
                    self.was_on_obstacle_last_time[count] = True
                if hits == []:
                    self.was_on_obstacle_last_time[count] = False

            # Spieler laeuft auf personenabhaengiges Objekt (Reaktion: personenabhaengige Reaktion z.B Pfandflasche sammeln)
            if self.spielmodus == TUTORIAL and self.game_status != TUTORIAL_WALK or self.spielmodus != TUTORIAL:
                hits = pygame.sprite.spritecollide(player, self.personen_objects, False, collide_hit_rect)
                for hit in hits:
                    if self.last_personen_object[count] == None:
                        self.last_personen_object[count] = hit
                        self.collected_person_objects[count] += 1
                        self.werte_since_last_lehrer_change[player]["collected_objects"] += 1
                        if LEHRER[player.lehrer_name]["object_kill"]:
                            hit.kill()
                        eval("lehrer_funktionen.object_collect_" + player.lehrer_name.replace(" ", "_") + "(self,player)")
                if hits == []:
                    self.last_personen_object[count] = None

            # Spieler sammelt das Objekt, das am Ende gefunden wird ein
            if self.game_status == COLLECTING_AT_END:
                if pygame.sprite.collide_rect(player, self.find_at_end):
                    if self.spielmodus == TUTORIAL:
                        self.spielmodus = MAP_MODUS
                        self.map_name = MAP_NAMES[0]
                    self.find_at_end.collected = True
                    self.game_status = WON_GAME

        # Schuss trifft Zombie
        hits = pygame.sprite.groupcollide(self.zombies, self.bullets, False, True)
        for mob in hits:
            for bullet in hits[mob]:
                mob.health -= bullet.damage
                self.werte_since_last_lehrer_change[bullet.player]["treffer"] += 1
                if mob.health <= 0:
                    self.werte_since_last_lehrer_change[bullet.player]["zombies_killed"] += 1
            mob.vel = vec(0, 0)

        # Schuss trifft Endgegner
        if self.spielmodus == ARENA_MODUS and self.num_zombie_wave == 3 and time() - self.end_gegner.spawn_time > 6 and self.end_gegner.alive:
            hits = pygame.sprite.spritecollide(self.end_gegner, self.bullets, False)
            if len(hits) > 0:
                self.end_gegner.mask = pygame.mask.from_surface(self.end_gegner.image)
                for bullet in self.bullets:
                    hit = pygame.sprite.collide_mask(self.end_gegner, bullet)
                    if hit is not None:
                        self.werte_since_last_lehrer_change[player]["treffer"] += 1
                        bullet.kill()
                        self.end_gegner.health -= 1
                        if self.end_gegner.health <= 0:
                            self.end_gegner.alive = False
                            self.endgegner_kill_pos = self.end_gegner.pos
                            End_Gegner_Explosion(self, self.endgegner_kill_pos)
                            self.end_gegner.kill()

    def draw_display(self):
        pygame.display.set_caption("{:.2f} - {}".format(self.clock.get_fps(), version))
        # Zeichnen
        time1 = self.make_time_measure()
        for count, camera in enumerate(self.camera):
            # Karte
            try:
                shown_part_of_map = self.map_img.subsurface((camera.inverted.x, camera.inverted.y, int(self.WIDTH / len(self.players)), self.HEIGHT))
            except ValueError:
                # Screen size bigger than map
                self.window_resize(self.map_img.get_width(), self.map_img.get_height())
                shown_part_of_map = self.map_img.subsurface((camera.inverted.x, camera.inverted.y, int(self.WIDTH / len(self.players)), self.HEIGHT))
            self.screen.blit(shown_part_of_map, (int(self.WIDTH / len(self.players) * count), 0))

            # Bildschirm in splitscreen bereiche unterteilen
            screen_part = pygame.Rect((int(self.WIDTH / len(self.players) * count), 0), (int(self.WIDTH / len(self.players)), self.HEIGHT))
            subscreen = self.screen.subsurface(screen_part)

            # Sprites
            for sprite in self.all_sprites:
                if not (self.spielmodus == TUTORIAL and ((isinstance(sprite, Personen_Obstacle) or isinstance(sprite, Personen_Object)) and self.game_status == TUTORIAL_WALK) or (isinstance(sprite, Mob) and (self.game_status == TUTORIAL_WALK or self.game_status == TUTORIAL_COLLECT))):
                    if isinstance(sprite, Mob):
                        sprite.draw_health()
                    if isinstance(sprite.image, list):
                        if not self.multiplayer:
                            self.screen.blit(sprite.image[count], camera.apply(sprite))
                        else:
                            pos_rect = camera.apply(sprite)
                            subscreen.blit(sprite.image[count], pos_rect)
                    else:
                        if not self.multiplayer:
                            self.screen.blit(sprite.image, camera.apply(sprite))
                        else:
                            pos_rect = camera.apply(sprite)
                            subscreen.blit(sprite.image, pos_rect)

            # Bilder auf Spieler oder Zombie malen (z.B. Sprechblasen)
            for player in self.players:
                if player.in_image_on_player:
                    player_pos = camera.apply(player)
                    subscreen.blit(player.image_to_place_on, (player_pos.x + player.image_verschiebung[0], player_pos.y + player.image_verschiebung[1]))
            for zombie in self.zombies:
                if zombie.in_image_on_mob:
                    player_pos = camera.apply(zombie)
                    subscreen.blit(zombie.image_to_place_on, (player_pos.x + zombie.image_verschiebung[0], player_pos.y + zombie.image_verschiebung[1]))

            # Kleine Kartenansicht
            if self.schoene_grafik:
                try:
                    area_around_player = pygame.Surface((self.small_map_sichtweite, self.small_map_sichtweite))
                    area_around_player.blit(self.map_img.subsurface(camera.player_umgebung.x, camera.player_umgebung.y, self.small_map_sichtweite, self.small_map_sichtweite), (0, 0))
                    for zombie in self.zombies:
                        pygame.draw.rect(area_around_player, SMALL_MAP_ZOMBIE_COLOR, pygame.Rect(int(zombie.pos.x - camera.player_umgebung.x - self.small_map_circle_sizes[0] / 2), int(zombie.pos.y - camera.player_umgebung.y - self.small_map_circle_sizes[0] / 2), self.small_map_circle_sizes[0], self.small_map_circle_sizes[0]))
                    for player in self.players:
                        pygame.draw.circle(area_around_player, SMALL_MAP_PLAYER_COLOR, (int(player.pos.x - camera.player_umgebung.x), int(player.pos.y - camera.player_umgebung.y)), self.small_map_circle_sizes[1])
                    try:
                        pygame.draw.circle(area_around_player, SMALL_MAP_ENDGEGNER_COLOR, (int(self.end_gegner.pos.x - camera.player_umgebung.x), int(self.end_gegner.pos.y - camera.player_umgebung.y)), self.small_map_circle_sizes[2])
                    except AttributeError:
                        pass
                    area_around_player = pygame.transform.scale(area_around_player, (self.small_map_size, self.small_map_size))
                    area_around_player.set_alpha(180)
                    area_around_player.convert_alpha()
                    if self.multiplayer:
                        if count == 1:
                            self.screen.blit(area_around_player, (self.WIDTH - 15 - self.small_map_size, int(self.HEIGHT - 30 - self.HEIGHT * 0.02 - 15 - self.BIG_TEXT - self.small_map_size)))
                            pygame.draw.rect(self.screen, BLACK, pygame.Rect(self.WIDTH - 15 - self.small_map_size, int(self.HEIGHT - 30 - self.HEIGHT * 0.02 - 15 - self.BIG_TEXT - self.small_map_size), self.small_map_size, self.small_map_size), 3)
                        else:
                            self.screen.blit(area_around_player, (15, int(self.HEIGHT - 30 - self.HEIGHT * 0.02 - 15 - self.BIG_TEXT - self.small_map_size)))
                            pygame.draw.rect(self.screen, BLACK, pygame.Rect(15, int(self.HEIGHT - 30 - self.HEIGHT * 0.02 - 15 - self.BIG_TEXT - self.small_map_size, self.small_map_size, self.small_map_size)), 3)
                    else:
                        self.screen.blit(area_around_player, (self.WIDTH - 15 - self.small_map_size, self.HEIGHT - 20 - 15 - self.BIG_TEXT - self.small_map_size))
                        pygame.draw.rect(self.screen, BLACK, pygame.Rect(self.WIDTH - 15 - self.small_map_size, self.HEIGHT - 20 - 15 - self.BIG_TEXT - self.small_map_size, self.small_map_size, self.small_map_size), 3)
                except Exception:
                    pass
        time2 = self.make_time_measure()
        # Im splitscreen schwarze Linie an den Raendern zwischen den einzelnen Screens
        if self.multiplayer:
            for player_num in range(len(self.players)):
                if player_num != 0:
                    pygame.draw.line(self.screen, BLIT_SCREEN_LINE_COLOR, (int(self.WIDTH / len(self.players) * player_num), 0), (int(self.WIDTH / len(self.players)) * player_num, self.HEIGHT), 8)
        time3 = self.make_time_measure()
        # Live Bar
        for count, player in enumerate(self.players):
            self.draw_live_bar(player, count)
        time4 = self.make_time_measure()
        # Levelfortschritt
        self.draw_level_fortschritts_balken()
        time5 = self.make_time_measure()
        # Texte
        for count, digit in enumerate(str(len(self.zombies))):
            self.screen.blit(self.number_surfaces[int(digit)], (self.num_zombies_text_pos[0] + count * self.bigest_num_length, self.num_zombies_text_pos[1]))
        for count, pos in enumerate(self.personen_item_text_pos):
            for digit_count, digit in enumerate(str(self.werte_since_last_lehrer_change[self.players[count]]["collected_objects"])):
                self.screen.blit(self.number_surfaces[int(digit)], (int(pos[0] + digit_count * self.bigest_num_length), int(pos[1] - self.BIG_TEXT * 1.2)))
        self.screen.blit(self.forground_text_img, (0, 0))
        # Lehrerunlock
        if self.spielmodus != TUTORIAL:
            if time() - self.time_last_lehrer_unlock < 4:
                self.draw_text(self.screen, LEHRER[self.lehrer_unlocked_last]["anrede"] + " " + self.lehrer_unlocked_last + " freigeschaltet", self.BIG_TEXT, int(self.WIDTH / 2), int(self.HEIGHT - 20 - self.HEIGHT * 0.02 - 3 - self.BIG_TEXT - 5 - self.BIG_TEXT - 10 - 15 - self.BIG_TEXT - 12), rect_place="unten_mitte", color=LEHRER_UNLOCKED_TEXT_COLOR)
                self.screen.blit(PLAYER_IMGES[self.lehrer_unlocked_last], (int(self.WIDTH / 2 - (PLAYER_IMGES[self.lehrer_unlocked_last].get_width()) / 2), int(self.HEIGHT - 20 - self.HEIGHT * 0.02 - 3 - self.BIG_TEXT - 5 - self.BIG_TEXT - 10 - 15 - self.BIG_TEXT - 5 - self.BIG_TEXT - 12 - PLAYER_IMGES[self.lehrer_unlocked_last].get_height())))
        # Waffenupgrade
        if self.spielmodus != TUTORIAL:
            for count, player in enumerate(self.players):
                if player.weapon_upgrade_unlocked and time() - self.weapon_upgrade_unlock_times[count] < 4.5:
                    self.draw_text(self.screen, LEHRER[player.lehrer_name]["weapon_upgrade"]["upgraded_weapon_name"] + " " + " freigeschaltet", self.BIG_TEXT, int(self.WIDTH / 2), int(self.HEIGHT - 20 - self.HEIGHT * 0.02 - 3 - self.BIG_TEXT - 10 - 15), rect_place="unten_mitte", color=LEHRER_UNLOCKED_TEXT_COLOR)
                elif time() - self.werte_since_last_lehrer_change[player]["time_lehrer_change"] < 5:
                    if self.get_text_rect(LEHRER[player.lehrer_name]["weapon_upgrade"]["unlock_text"], self.BIG_TEXT).width > self.WIDTH:
                        text = LEHRER[player.lehrer_name]["weapon_upgrade"]["unlock_text"]
                        self.draw_text(self.screen, text[:int(len(text) / 2)], self.BIG_TEXT, int(self.WIDTH / 2), int(self.HEIGHT - 20 - self.HEIGHT * 0.02 - 3 - self.BIG_TEXT - 10 - 15 - self.BIG_TEXT - 5), rect_place="unten_mitte", color=LEHRER_UNLOCKED_TEXT_COLOR)
                        self.draw_text(self.screen, text[int(len(text) / 2):], self.BIG_TEXT, int(self.WIDTH / 2), int(self.HEIGHT - 20 - self.HEIGHT * 0.02 - 3 - self.BIG_TEXT - 10 - 15), rect_place="unten_mitte", color=LEHRER_UNLOCKED_TEXT_COLOR)
                    else:
                        self.draw_text(self.screen, LEHRER[player.lehrer_name]["weapon_upgrade"]["unlock_text"], self.BIG_TEXT, int(self.WIDTH / 2), int(self.HEIGHT - 20 - self.HEIGHT * 0.02 - 3 - self.BIG_TEXT - 10 - 15), rect_place="unten_mitte", color=LEHRER_UNLOCKED_TEXT_COLOR)
        # Countdown vor Zombiewelle
        if self.spielmodus == ARENA_MODUS:
            if time() - self.countdown_start_time <= 5:
                self.draw_text(self.screen, str(5 - round(time() - self.countdown_start_time)), self.calculate_fit_size(0.2, 0.4), int(self.WIDTH / 2), int(self.HEIGHT / 2), color=WHITE, rect_place="mitte")
        time6 = self.make_time_measure()
        # Tutorial
        if self.spielmodus == TUTORIAL:
            if self.game_status == TUTORIAL_WALK:
                if self.with_maussteuerung:
                    self.draw_text(self.screen, "Bewege dich mit der Maus und halte Shift zum Schleichen und rückwärts Gehen", self.NORMAL_TEXT, int(self.WIDTH / 2), int(self.HEIGHT * (1 / 3)))
                    self.screen.blit(MAUS_IMG, (int(self.WIDTH / 2), 20))
                else:
                    self.draw_text(self.screen, "Bewege dich mit den Pfeiltasten", self.NORMAL_TEXT, int(self.WIDTH / 2), int(self.HEIGHT * (1 / 3)))
                    self.screen.blit(PFEILTASTE_IMG, (int(self.WIDTH / 2 - PFEILTASTE_IMG.get_rect().w / 2), 20))
            elif self.game_status == TUTORIAL_COLLECT:
                self.draw_text(self.screen, "Sammel die Objekte ohne auf die Hindernisse zu treten", self.NORMAL_TEXT, int(self.WIDTH / 2), int(self.HEIGHT * (1 / 3)))
            elif self.game_status == TUTORIAL_SHOOT:
                self.draw_text(self.screen, "Schieße mit Leertaste oder linker Maustaste auf die Zombies", self.NORMAL_TEXT, int(self.WIDTH / 2), int(self.HEIGHT * (1 / 3)))
                self.screen.blit(MAUS_LINKS_IMG, (int(self.WIDTH / 2 - MAUS_LINKS_IMG.get_rect().w / 2), 20))
                self.screen.blit(LEERTASTE_IMG, (int(self.WIDTH / 2 - LEERTASTE_IMG.get_rect().w / 2), 40 + MAUS_LINKS_IMG.get_rect().h))
            elif self.game_status == TUTORIAL_POWER_UP:
                self.draw_text(self.screen, "Benutzte mit X oder rechter Maustaste dein Power-Up", self.NORMAL_TEXT, int(self.WIDTH / 2), int(self.HEIGHT * (1 / 3)))
                self.screen.blit(MAUS_RECHTS_IMG, (int(self.WIDTH / 2 - MAUS_RECHTS_IMG.get_rect().w / 2), 20))
                self.screen.blit(X_Y_IMG, (int(self.WIDTH / 2 - X_Y_IMG.get_rect().w / 2), 40 + MAUS_LINKS_IMG.get_rect().h))

        if self.measure_times:
            self.measured_times[4].append(time6 - time1)
            self.measured_times[5].append(time2 - time1)
            self.measured_times[6].append(time4 - time3)
            self.measured_times[7].append(time5 - time4)
            self.measured_times[8].append(time6 - time5)

        pygame.display.flip()

    def update_forground_text_img(self):
        surface = pygame.Surface((self.WIDTH, self.HEIGHT), pygame.SRCALPHA)
        self.personen_item_text_pos = []
        # Texte
        if self.multiplayer:
            rect = self.draw_text(surface, 'Zombies: ', self.BIG_TEXT, int(self.WIDTH / 2 - (3 * self.bigest_num_length) / 2), 10, rect_place="oben_mitte")
            self.num_zombies_text_pos = (int(self.WIDTH / 2 - (3 * self.bigest_num_length) / 2 + rect.width / 2), 10)
            for count, player in enumerate(self.players):
                if count >= self.num_players_in_multiplayer / 2:
                    rect = self.draw_text(surface, LEHRER[player.lehrer_name]["personen_item_text"] + ": ", self.BIG_TEXT, int(self.WIDTH - ((self.WIDTH / self.num_players_in_multiplayer) * (self.num_players_in_multiplayer - count - 1)) - 10 - 2 * self.bigest_num_length), int(self.HEIGHT - 30 - self.HEIGHT * 0.02), rect_place="unten_rechts")
                    self.personen_item_text_pos.append((int(self.WIDTH - ((self.WIDTH / self.num_players_in_multiplayer) * (self.num_players_in_multiplayer - count - 1)) - 10 - 2 * self.bigest_num_length), int(self.HEIGHT - 30 - self.HEIGHT * 0.02)))
                else:
                    rect = self.draw_text(surface, LEHRER[player.lehrer_name]["personen_item_text"] + ": ", self.BIG_TEXT, int(10 + ((self.WIDTH / self.num_players_in_multiplayer) * (count))), int(self.HEIGHT - 30 - self.HEIGHT * 0.02), rect_place="unten_links")
                    self.personen_item_text_pos.append((10 + ((int(self.WIDTH / self.num_players_in_multiplayer) * (count)) + rect.width), int(self.HEIGHT - 30 - self.HEIGHT * 0.02)))
        else:
            rect = self.draw_text(surface, 'Zombies: ', self.BIG_TEXT, self.WIDTH - 10 - 3 * self.bigest_num_length, 10, rect_place="oben_rechts")
            self.num_zombies_text_pos = (self.WIDTH - 10 - 3 * self.bigest_num_length, 10)
            rect = self.draw_text(surface, LEHRER[self.players[0].lehrer_name]["personen_item_text"] + ": ", self.BIG_TEXT, self.WIDTH - 10 - 2 * self.bigest_num_length, self.HEIGHT - 20, rect_place="unten_rechts")
            self.personen_item_text_pos = [(self.WIDTH - 10 - 2 * self.bigest_num_length, self.HEIGHT - 20)]
        if self.spielmodus == ARENA_MODUS:
            if self.multiplayer:
                self.draw_text(surface, 'Welle: ' + str(self.num_zombie_wave), self.BIG_TEXT, int(self.WIDTH / 2), int(self.HEIGHT - 20 - self.HEIGHT * 0.02 - 3 - self.BIG_TEXT - 10), rect_place="oben_mitte")
            else:
                self.draw_text(surface, 'Welle: ' + str(self.num_zombie_wave), self.BIG_TEXT, 10, int(self.HEIGHT - 20 - self.HEIGHT * 0.02 - 3 - self.BIG_TEXT - 10), rect_place="oben_links")

        if self.multiplayer:
            self.level_bar_lenght = self.WIDTH - 15 - 15
        else:
            self.level_bar_lenght = self.WIDTH - self.longest_object_name - 15 - 15 - 10
        self.level_bar_height = self.HEIGHT * 0.02
        if self.game_status == COLLECTING_AT_END:
            self.draw_text(surface, TEXT_FIND_AT_END, self.BIG_TEXT, 15, int(self.HEIGHT - 17 - self.BIG_TEXT), rect_place="oben_links", color=LEVEL_FORTSCHRITTS_FARBE)
        else:
            if self.spielmodus == ARENA_MODUS:
                for x in range(3):
                    pygame.draw.circle(surface, LEVEL_FORTSCHRITTS_FARBE, (int(15 + self.level_bar_lenght / 3 * x), int(self.HEIGHT - 20 - self.level_bar_height / 2)), int(self.level_bar_height * 0.8), 3)
            if self.spielmodus != TUTORIAL:
                pygame.draw.rect(surface, LEVEL_FORTSCHRITTS_FARBE, pygame.Rect((15, int(self.HEIGHT - 20 - self.level_bar_height - 3)), (self.level_bar_lenght + 6, int(self.level_bar_height + 6))), 3)

        self.forground_text_img = surface

    def update_live_bar_image(self, player, player_num):
        surface = pygame.Surface((int(self.live_bar_img_width + self.WIDTH / 3), int(self.live_bar_img_height + self.HEIGHT / 4)), pygame.SRCALPHA)
        bild_breite = surface.get_width()

        # Power-Up Icon
        if self.multiplayer and player_num >= self.num_players_in_multiplayer / 2:
            surface.blit(pygame.transform.scale(PERSONEN_POWER_UP_ICONS[player.lehrer_name], (int(0.338888 * self.live_bar_img_width), int(0.743902 * self.live_bar_img_height))),
                         (bild_breite - int(0.338888 * self.live_bar_img_width) - int(0.01666 * self.live_bar_img_width), int(0.195122 * self.live_bar_img_height)))
        else:
            surface.blit(pygame.transform.scale(PERSONEN_POWER_UP_ICONS[player.lehrer_name], (int(0.338888 * self.live_bar_img_width), int(0.743902 * self.live_bar_img_height))),
                         (int(0.01666 * self.live_bar_img_width), int(0.195122 * self.live_bar_img_height)))

        # Neutrales Icon
        if self.multiplayer and player_num >= self.num_players_in_multiplayer / 2:
            surface.blit(pygame.transform.scale(PEROSNEN_OBJECT_IMGES[player.lehrer_name]["icon"], (int(0.13611 * self.live_bar_img_width), int(0.13611 * self.live_bar_img_width))),
                         (bild_breite - int(0.13611 * self.live_bar_img_width) - int(0.40833 * self.live_bar_img_width), int(0.182926 * self.live_bar_img_height)))
        else:
            surface.blit(pygame.transform.scale(PEROSNEN_OBJECT_IMGES[player.lehrer_name]["icon"], (int(0.13611 * self.live_bar_img_width), int(0.13611 * self.live_bar_img_width))),
                         (int(0.40833 * self.live_bar_img_width), int(0.182926 * self.live_bar_img_height)))

        # Schelchtes Icon
        if self.multiplayer and player_num >= self.num_players_in_multiplayer / 2:
            surface.blit(pygame.transform.scale(PERSONEN_OBSTACLE_IMGES[player.lehrer_name]["icon"], (int(0.13611 * self.live_bar_img_width), int(0.13611 * self.live_bar_img_width))),
                         (bild_breite - int(0.13611 * self.live_bar_img_width) - int(0.3722 * self.live_bar_img_width), int(0.52439 * self.live_bar_img_height)))
        else:
            surface.blit(pygame.transform.scale(PERSONEN_OBSTACLE_IMGES[player.lehrer_name]["icon"], (int(0.13611 * self.live_bar_img_width), int(0.13611 * self.live_bar_img_width))),
                         (int(0.3722 * self.live_bar_img_width), int(0.52439 * self.live_bar_img_height)))

        # Live Bar Bild oben drauf
        if self.multiplayer and player_num >= self.num_players_in_multiplayer / 2:
            surface.blit(pygame.transform.flip(pygame.transform.scale(LIVE_BAR_IMG, (int(self.live_bar_img_width), int(self.live_bar_img_height))), True, False), (bild_breite - self.live_bar_img_width, 0))
        else:
            surface.blit(pygame.transform.scale(LIVE_BAR_IMG, (int(self.live_bar_img_width), int(self.live_bar_img_height))), (0, 0))

        # Texte zum Lehrer
        if self.multiplayer and player_num >= self.num_players_in_multiplayer / 2:
            self.draw_text(surface, LEHRER[player.lehrer_name]["anrede"] + " " + LEHRER[player.lehrer_name]["name"], self.NORMAL_TEXT, int(bild_breite - 0.6805 * self.live_bar_img_width, 0.165 * self.live_bar_img_height), rect_place="oben_rechts")
        else:
            self.draw_text(surface, LEHRER[player.lehrer_name]["anrede"] + " " + LEHRER[player.lehrer_name]["name"], self.NORMAL_TEXT, int(0.6805 * self.live_bar_img_width, 0.165 * self.live_bar_img_height), rect_place="oben_links")
        # Beschreibung umbrechen und dann jede Zeile einzeln zeichnen
        beschreibungs_texte = [""]
        array_num = 0
        for count, letter in enumerate(LEHRER[player.lehrer_name]["personen_beschreibung"]):
            beschreibungs_texte[array_num] += letter
            if count % 20 == 0 and count != 0:
                array_num += 1
                beschreibungs_texte.append("")
        for count, text in enumerate(beschreibungs_texte):
            if self.multiplayer and player_num >= self.num_players_in_multiplayer / 2:
                self.draw_text(surface, beschreibungs_texte[count], self.SMALL_TEXT, int(bild_breite - 0.569444 * self.live_bar_img_width, 0.2 * self.live_bar_img_height + self.NORMAL_TEXT + count * (self.SMALL_TEXT + 5)), rect_place="oben_rechts", font_name=ARIAL_FONT, color=BLACK)
            else:
                self.draw_text(surface, beschreibungs_texte[count], self.SMALL_TEXT, int(0.569444 * self.live_bar_img_width, 0.2 * self.live_bar_img_height + self.NORMAL_TEXT + count * (self.SMALL_TEXT + 5)), rect_place="oben_links", font_name=ARIAL_FONT, color=BLACK)

        self.live_bar_images[player_num] = surface

    def draw_live_bar(self, player, player_num):

        # Lebensanzeige
        BAR_LENGTH = 0.95 * self.live_bar_img_width
        BAR_HEIGHT = 0.075 * self.live_bar_img_height
        # Prozentualelaenge berechnen
        if player.health / LEHRER[player.lehrer_name]["player_health"] < 0:
            pct = 0
        else:
            pct = player.health / LEHRER[player.lehrer_name]["player_health"]
        if self.multiplayer and player_num >= self.num_players_in_multiplayer / 2:
            fill_rect = pygame.Rect(int(self.WIDTH - ((int(self.WIDTH / self.num_players_in_multiplayer) * (self.num_players_in_multiplayer - player_num - 1)) - int(BAR_LENGTH) - int(0.031 * self.live_bar_img_width))), int(0.0426829 * self.live_bar_img_height), int(pct * BAR_LENGTH), int(BAR_HEIGHT))
        else:
            fill_rect = pygame.Rect(int((0.031 * self.live_bar_img_width) + ((self.WIDTH / self.num_players_in_multiplayer) * (player_num))), int(0.0426829 * self.live_bar_img_height), int(pct * BAR_LENGTH), int(BAR_HEIGHT))
        # Farbe
        if pct > 0.6:
            col = LEBENSANZEIGE_GRUEN
        elif pct > 0.3:
            col = LEBENSANZEIGE_GELB
        else:
            col = LEBENSANZEIGE_ROT
        # Rechteck zeichnen
        pygame.draw.rect(self.screen, col, fill_rect)

        # Power-Up
        if time() * 1000 - self.last_power_up_use_time[self.players.index(player)] < LEHRER[player.lehrer_name]["power_up_time"]:
            if self.multiplayer and player_num >= self.num_players_in_multiplayer / 2:
                rect = pygame.Rect((int(self.WIDTH - ((self.WIDTH / self.num_players_in_multiplayer) * (self.num_players_in_multiplayer - player_num - 1)) - int(0.345 * self.live_bar_img_width) - int(0.0139 * self.live_bar_img_width)), int(0.1891 * self.live_bar_img_height)), (int(0.345 * self.live_bar_img_width), int(0.757 * self.live_bar_img_height)))

            else:
                rect = pygame.Rect((int((0.0139 * self.live_bar_img_width) + ((self.WIDTH / self.num_players_in_multiplayer) * (player_num))), int(0.1891 * self.live_bar_img_height)), (int(0.345 * self.live_bar_img_width), int(0.757 * self.live_bar_img_height)))
            pygame.draw.arc(self.screen, POWER_UP_TIME_COLOR, rect, - ((2 * pi / LEHRER[player.lehrer_name]["power_up_time"]) * (time() * 1000 - self.last_power_up_use_time[self.players.index(player)])) + halbes_pi, halbes_pi, int(0.022 * self.live_bar_img_width))
        else:
            if self.multiplayer and player_num >= self.num_players_in_multiplayer / 2:
                pygame.draw.circle(self.screen, POWER_UP_TIME_COLOR, (int(self.WIDTH - ((self.WIDTH / self.num_players_in_multiplayer) * (self.num_players_in_multiplayer - player_num - 1)) - int(0.187 * self.live_bar_img_width)), int(0.568 * self.live_bar_img_height)), int(0.176 * self.live_bar_img_width), int(0.022 * self.live_bar_img_width))

            else:
                pygame.draw.circle(self.screen, POWER_UP_TIME_COLOR, (int((0.187 * self.live_bar_img_width) + ((self.WIDTH / self.num_players_in_multiplayer) * (player_num))), int(0.568 * self.live_bar_img_height)), int(0.176 * self.live_bar_img_width), int(0.022 * self.live_bar_img_width))

        # Live Bar Bild oben drauf
        if self.multiplayer and player_num >= self.num_players_in_multiplayer / 2:
            self.screen.blit(self.live_bar_images[player_num], (int(self.WIDTH - ((self.WIDTH / self.num_players_in_multiplayer) * (self.num_players_in_multiplayer - player_num - 1)) - self.live_bar_images[player_num].get_width()), 0))
        else:
            self.screen.blit(self.live_bar_images[player_num], (int((self.WIDTH / self.num_players_in_multiplayer) * (player_num)), 0))

    def draw_level_fortschritts_balken(self):
        if self.game_status != COLLECTING_AT_END and self.spielmodus != TUTORIAL:
            # Prozentualelaenge berechnen
            if self.genauerer_spielmodus == AFTER_TIME:
                if self.spielmodus == MAP_MODUS:
                    pct = (time() - self.level_start_time) / TIME_MAP_LEVEL
                elif self.spielmodus == ARENA_MODUS:
                    if time() - self.countdown_start_time <= 6:
                        pct = (self.num_zombie_wave - 1) / 3
                    else:
                        if self.num_zombie_wave == 3:
                            if self.multiplayer:
                                pct = (ENDGEGNER_HEALTH_MULTIPLAYER[self.schwierigkeit - 1] - self.end_gegner.health) / ENDGEGNER_HEALTH_MULTIPLAYER[self.schwierigkeit - 1] / 3 + (self.num_zombie_wave - 1) / 3
                            else:
                                pct = (ENDGEGNER_HEALTH[self.schwierigkeit - 1] - self.end_gegner.health) / ENDGEGNER_HEALTH[self.schwierigkeit - 1] / 3 + (self.num_zombie_wave - 1) / 3
                        else:
                            pct = (time() - self.last_zombie_wave_time) / TIME_BETWEEN_ZOMBIE_WAVES / 3 + (self.num_zombie_wave - 1) / 3
            elif self.genauerer_spielmodus == AFTER_KILLED:
                if self.spielmodus == MAP_MODUS:
                    if self.level_start_num_zombies > 0:
                        pct = ((self.level_start_num_zombies - len(self.zombies)) / self.level_start_num_zombies)
                    else:
                        pct = 0
                elif self.spielmodus == ARENA_MODUS:
                    if time() - self.countdown_start_time <= 6:
                        pct = (self.num_zombie_wave - 1) / 3
                    else:
                        if self.num_zombie_wave == 3:
                            if self.multiplayer:
                                pct = (ENDGEGNER_HEALTH_MULTIPLAYER[self.schwierigkeit - 1] - self.end_gegner.health) / ENDGEGNER_HEALTH_MULTIPLAYER[self.schwierigkeit - 1] / 3 + (self.num_zombie_wave - 1) / 3
                            else:
                                pct = (ENDGEGNER_HEALTH[self.schwierigkeit - 1] - self.end_gegner.health) / ENDGEGNER_HEALTH[self.schwierigkeit - 1] / 3 + (self.num_zombie_wave - 1) / 3
                        else:
                            pct = ((self.level_start_num_zombies - len(self.zombies)) / self.level_start_num_zombies) / 3 + (self.num_zombie_wave - 1) / 3
            # Rechteck zeichnen
            pygame.draw.rect(self.screen, LEVEL_FORTSCHRITTS_FARBE, pygame.Rect((15, self.HEIGHT - 20 - self.level_bar_height), (int(pct * self.level_bar_lenght), self.level_bar_height)), 0)

    def quit(self):
        if self.measure_times:
            print("Durchschnittliche Fps: ", round(sum(self.fps_werte) / len(self.fps_werte), 3))
            total = sum(self.measured_times[0]) / len(self.measured_times[0])
            print("Total                            :", round(sum(self.measured_times[0]) / len(self.measured_times[0]), 3))
            print("Spielaktionen, Spriteupdates     :", round(sum(self.measured_times[1]) / len(self.measured_times[1]), 3), "  (", round((sum(self.measured_times[1]) / len(self.measured_times[1]) / total) * 100, 2), "% )")
            print("Auf Tasten achten, Spiel zu ende?:", round(sum(self.measured_times[2]) / len(self.measured_times[2]), 3), "  (", round((sum(self.measured_times[2]) / len(self.measured_times[2]) / total) * 100, 2), "% )")
            print("Zeichnen ( self.draw_display() ) :", round(sum(self.measured_times[3]) / len(self.measured_times[3]), 3), "  (", round((sum(self.measured_times[3]) / len(self.measured_times[3]) / total) * 100, 2), "% )")
            draw_total = sum(self.measured_times[4]) / len(self.measured_times[4])
            print("Zeichnen Total                   :", round(sum(self.measured_times[4]) / len(self.measured_times[4]), 3))
            print("map,smallmap,sprites,sprechbalsen:", round(sum(self.measured_times[5]) / len(self.measured_times[5]), 3), "  (", round((sum(self.measured_times[5]) / len(self.measured_times[5]) / draw_total) * 100, 2), "% )")
            print("Lebens und Powerupanzeige        :", round(sum(self.measured_times[6]) / len(self.measured_times[6]), 3), "  (", round((sum(self.measured_times[6]) / len(self.measured_times[6]) / draw_total) * 100, 2), "% )")
            print("Levelfortschrittsbalken          :", round(sum(self.measured_times[7]) / len(self.measured_times[7]), 3), "  (", round((sum(self.measured_times[7]) / len(self.measured_times[7]) / draw_total) * 100, 2), "% )")
            print("Texte                            :", round(sum(self.measured_times[8]) / len(self.measured_times[8]), 3), "  (", round((sum(self.measured_times[8]) / len(self.measured_times[8]) / draw_total) * 100, 2), "% )")
        pygame.quit()
        sys.exit()


# create the game object
g = Game()
while True:
    g.start_game()
