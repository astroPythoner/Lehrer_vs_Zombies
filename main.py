import sys
from random import choice
from time import time
from Flappy_Plane.sprites import *
from tilemap import *
from menus import *
from drawing import *

multiplayer_possible = True
try:
    from joystickpins import JoystickPins, KeyboardStick
except Exception:
    try:
        from joystickpins import joystickpins
        JoystickPins = joystickpins.JoystickPins
        KeyboardStick = joystickpins.KeyboardStick
    except Exception:
        multiplayer_possible = False

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
        self.small_map_sichtweite = calculate_fit_size(self,SMALL_MAP_SICHTWEITE_FAKTOR, SMALL_MAP_SICHTWEITE_FAKTOR)

        self.background = pygame.transform.scale(background, (start_width, start_height))
        self.background_rect = self.background.get_rect()

        self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT), pygame.RESIZABLE)
        pygame.display.set_caption("Lehrer vs Zombies! - " + version)
        self.clock = pygame.time.Clock()

        update_text_sizes(self)

        self.maussteuerung_circle_radius = calculate_fit_size(self,0.35, 0.35)

        self.last_personen_obstacle_damage = []
        self.was_on_obstacle_last_time = []
        self.last_personen_object = []
        self.last_power_up_use_time = []
        self.collected_person_objects = []
        self.paused = []

        self.music_volume = game_music_volume
        self.sound_volume = game_sound_volume

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
            width = get_text_rect(LEHRER[lehrer]["anrede"] + " " + LEHRER[lehrer]["name"], self.HUGE_TEXT).width
            if width > self.longest_lehrer_name:
                self.longest_lehrer_name = width
            width = get_text_rect("Waffe: " + str(LEHRER[lehrer]["weapon_name"]), self.SMALL_TEXT, ARIAL_FONT).width
            if width > self.longest_weapon_name:
                self.longest_weapon_name = width
            width = get_text_rect(str(LEHRER[lehrer]["personen_item_text"]) + ":" + str(99), self.BIG_TEXT).width
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
            rect = get_text_rect(x, self.BIG_TEXT)
            if rect.width > self.bigest_num_length:
                self.bigest_num_length = rect.width
        for x in range(10):
            surf = pygame.Surface((self.bigest_num_length, int(self.BIG_TEXT * 1.2)), pygame.SRCALPHA)
            draw_text(surf, x, self.BIG_TEXT, 0, 0, rect_place="oben_links")
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
        self.num_players_in_multiplayer = 1
        self.use_tastatur = True
        self.all_joysticks = []
        self.used_joysticks = []
        self.find_josticks()
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

    # Tastatur und Mauseingaben
    def check_key_or_mouse_pressed(self, check_for=[]):
        ### returns dict of all joysticks with dict of given keys and True or False value depending on wether button was pressed e.x. {"Tastatur":{12:False,3:True},"PlaystationController":{12:False,3:False}}
        return_dict = {"Tastatur": {}}
        for joystick in self.all_joysticks:
            return_dict[joystick.get_name()] = {}
        for joystick in return_dict:
            for key in check_for:
                return_dict[joystick][key] = False

        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT or event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self.quit()

            if event.type == pygame.KEYDOWN:
                if event.key in check_for:
                    return_dict["Tastatur"][event.key] = True
                if "text" in check_for:
                    return_dict["Tastatur"]["text"] = event.unicode

            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    return_dict["Tastatur"][MAUS_LEFT] = event.pos
                elif event.button == 3:
                    return_dict["Tastatur"][MAUS_RIGHT] = event.pos
                elif event.button == 4:
                    return_dict["Tastatur"][MAUS_ROLL_UP] = event.pos
                elif event.button == 5:
                    return_dict["Tastatur"][MAUS_ROLL_DOWN] = event.pos

            if event.type == pygame.VIDEORESIZE:
                resize_window(self, event.w, event.h)

        for joystick in self.all_joysticks:
            keys = {pygame.K_UP: joystick.get_axis_up, pygame.K_DOWN: joystick.get_axis_down, pygame.K_LEFT: joystick.get_axis_left, pygame.K_RIGHT: joystick.get_axis_right, pygame.K_RETURN: joystick.get_start, pygame.K_SPACE: joystick.get_select, pygame.K_a: joystick.get_Y, pygame.K_w: joystick.get_X, pygame.K_s: joystick.get_B, pygame.K_d: joystick.get_A, pygame.K_c: joystick.get_A}
            maus = {MAUS_ROLL_DOWN: joystick.get_shoulder_left, MAUS_ROLL_UP: joystick.get_shoulder_right}
            if joystick.get_start() and joystick.get_select():
                self.quit()
            for key in keys:
                if key in check_for:
                    return_dict[joystick.get_name()][key] = keys[key]()
            for m in maus:
                if maus[m]():
                    return_dict[joystick.get_name()][m] = True

        return return_dict

    def check_key_in_pressed(self, key, pressed):
        for joystick in pressed:
            if key in pressed[joystick]:
                if pressed[joystick][key]:
                    return True
        return False

    def check_maus_pos_on_rect(self, maus_pos, rect):
        return rect.collidepoint(maus_pos)

    def find_josticks(self):
        if multiplayer_possible:
            # Knöpfe und Kontroller finden und Initialisieren
            self.all_joysticks = []
            for joy in range(pygame.joystick.get_count()):
                pygame_joystick = pygame.joystick.Joystick(joy)
                pygame_joystick.init()
                my_joystick = JoystickPins(pygame_joystick)
                print("adding joystick " + my_joystick.get_name())
                self.all_joysticks.append(my_joystick)

    # Zeitmessung
    def make_time_measure(self):
        if self.measure_times:
            return round(time() * 1000, 2)
        return None

    ########## Hier startet das eigentliche Spiel ##########
    def start_game(self):
        pygame.mixer.music.play(loops=-1)

        if self.multiplayer and self.num_players_in_multiplayer > 2:
            self.schoene_grafik = False
        self.game_status = BEFORE_FIRST_GAME
        make_start_game_selection(self)

        while True:
            # Spiel beginnen
            if self.spielmodus == TUTORIAL:
                self.game_status = TUTORIAL_WALK
            else:
                self.game_status = PLAYING
            # für jeden Spieler unterschiedlichen Lehrer finden, die keine Bedingung am Anfang haben
            if self.players != []:
                # Die gleichen Lehrer wie im letzen Spiel solange diese auch direkt freigeschaltet sind
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
                    if len(lehrer_namen) != self.num_players_in_multiplayer:
                        for added_player_num in range(self.num_players_in_multiplayer - len(lehrer_namen)):
                            i = 0
                            namen_gefunden = False
                            while not namen_gefunden and i < len(LEHRER_NAMEN):
                                anderer_spieler_hat_schon_diese_person = False
                                unlocked = False
                                for playerrr in lehrer_namen:
                                    if playerrr == LEHRER_NAMEN[i]:
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

            self.clock.tick(FPS)

            ## eigentliches Spiel starten
            self.game_loop()

            if self.spielmodus == TUTORIAL:
                self.spielmodus = MAP_MODUS
            make_start_game_selection(self)

    ######## Hauptschleife des Spiels #######
    def game_loop(self):
        while self.game_status == PLAYING or self.game_status == COLLECTING_AT_END or (self.spielmodus == TUTORIAL and self.game_status != PLAYER_DIED):
            self.dt = self.clock.tick(FPS) / 1000.0

            pressed = self.check_key_or_mouse_pressed([pygame.K_BACKSPACE, pygame.K_SPACE, pygame.K_RETURN, pygame.K_y, pygame.K_x, pygame.K_c, pygame.K_LEFT, pygame.K_RIGHT, pygame.K_UP, pygame.K_DOWN])

            time1 = self.make_time_measure()
            # Alle Spielaktionen hier ausfuehren
            if False in self.paused:
                # schiessen (auch Dauerschuss)
                if (self.spielmodus == TUTORIAL and (self.game_status == TUTORIAL_POWER_UP or self.game_status == TUTORIAL_SHOOT)) or self.spielmodus != TUTORIAL:
                    for player in self.players:
                        if player.joystick == "Tastatur":
                            if pygame.mouse.get_pressed()[0] or pygame.key.get_pressed()[pygame.K_SPACE]:
                                player.shoot()
                        else:
                            for joystick in self.used_joysticks:
                                if joystick.get_name() == player.joystick:
                                    if joystick.get_B():
                                        player.shoot()
                # alle sprites updaten
                self.all_sprites.update()
                for count, camera in enumerate(self.camera):
                    camera.update(self.players[count])
                # Auf Kollisionen pruefen
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
                    elif self.game_status == TUTORIAL_COLLECT:
                        total_collected = 0
                        for player in self.players:
                            total_collected += self.werte_since_last_lehrer_change[player]["collected_objects"]
                        if total_collected >= 4:
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
                        if MAUS_RIGHT in pressed[player.joystick] or pressed[player.joystick][pygame.K_y] or pressed[player.joystick][pygame.K_x] or pressed[player.joystick][pygame.K_c]:
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
                    if self.players[player_num].joystick == "Tastatur":
                        if pressed["Tastatur"][pygame.K_RETURN]:
                            self.paused[player_num] = True
                            make_lehrer_selection(self,self.screen, player_num)
                            self.clock.tick(FPS)
                    elif pressed[self.players[player_num].joystick][pygame.K_SPACE]:
                        self.paused[player_num] = True
                        make_lehrer_selection(self,self.screen, player_num)
                        self.clock.tick(FPS)

            # Spiel abbrechen
            for player in self.players:
                if player.joystick == "Tastatur":
                    if pressed["Tastatur"][pygame.K_BACKSPACE]:
                        if self.spielmodus == TUTORIAL:
                            self.spielmodus = MAP_MODUS
                            self.map_name = MAP_NAMES[0]
                        self.game_status = BEFORE_FIRST_GAME
                else:
                    if pressed[player.joystick][pygame.K_RETURN]:
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
                update_forground_text_img(self)

            # Etwas freigeschalten?
            if self.spielmodus != TUTORIAL:
                # Lehrer freischalten
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
            draw_display(self)
            time4 = self.make_time_measure()

            if self.measure_times:
                self.fps_werte.append(self.clock.get_fps())
                self.measured_times[0].append(time4 - time1)
                self.measured_times[1].append(time2 - time1)
                self.measured_times[2].append(time3 - time2)
                self.measured_times[3].append(time4 - time3)

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
        update_forground_text_img(self)

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
                    if self.use_tastatur:
                        player = Player(self, obj_center.x, obj_center.y, lehrer_namen[0], 0, "Tastatur")
                        self.players.append(player)
                        self.weapon_upgrade_unlock_times.append(0)
                        self.werte_since_last_lehrer_change[player] = {"shoots": 0, "treffer": 0, "collected_objects": 0, "num_obstacles_stept_on": 0, "time_lehrer_change": time(), "zombies_killed": 0, "collected_health_packs": 0, "num_power_ups": 0}
                    for i, joystick in enumerate(self.used_joysticks):
                        if self.use_tastatur:
                            player = Player(self, obj_center.x, obj_center.y, lehrer_namen[i + 1], i + 1, joystick.get_name())
                        else:
                            player = Player(self, obj_center.x, obj_center.y, lehrer_namen[i], i, joystick.get_name())
                        self.players.append(player)
                        self.weapon_upgrade_unlock_times.append(0)
                        self.werte_since_last_lehrer_change[player] = {"shoots": 0, "treffer": 0, "collected_objects": 0, "num_obstacles_stept_on": 0, "time_lehrer_change": time(), "zombies_killed": 0, "collected_health_packs": 0, "num_power_ups": 0}
                else:
                    if self.use_tastatur:
                        player = Player(self, obj_center.x, obj_center.y, lehrer_namen[0], 0, "Tastatur")
                    else:
                        player = Player(self, obj_center.x, obj_center.y, lehrer_namen[0], 0, self.used_joysticks[0].get_name())
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

        # Fehler abfangen: Spieler nicht auf der Karte, keine Zombies
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

        # Bilder die nur einmal berechnet werden
        for count, player in enumerate(self.players):
            update_live_bar_image(self,player, count)
        update_lehrer_selection_pictures(self)
        update_forground_text_img(self)

        # Zeiten
        self.level_start_time = time()
        self.last_zombie_wave_time = time()
        self.level_start_num_zombies = len(self.zombies)

        # Mini Map
        if self.multiplayer:
            self.small_map_size = calculate_fit_size(self,0.23, 0.23)
        else:
            self.small_map_size = calculate_fit_size(self,0.3, 0.3)
        self.small_map_circle_sizes = [int(self.small_map_size * 0.3), int(self.small_map_size * 0.25), int(self.small_map_size * 0.25)]
        self.small_map_sichtweite = self.small_map_sichtweite

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

    def quit(self):
        if self.measure_times:
            print("Durchschnittliche Fps: ", round(sum(self.fps_werte) / len(self.fps_werte), 3))
            total = sum(self.measured_times[0]) / len(self.measured_times[0])
            print("Total                            :", round(sum(self.measured_times[0]) / len(self.measured_times[0]), 3))
            print("Spielaktionen, Spriteupdates     :", round(sum(self.measured_times[1]) / len(self.measured_times[1]), 3), "  (", round((sum(self.measured_times[1]) / len(self.measured_times[1]) / total) * 100, 2), "% )")
            print("Auf Tasten achten, Spiel zu ende?:", round(sum(self.measured_times[2]) / len(self.measured_times[2]), 3), "  (", round((sum(self.measured_times[2]) / len(self.measured_times[2]) / total) * 100, 2), "% )")
            print("Zeichnen ( draw_display() )      :", round(sum(self.measured_times[3]) / len(self.measured_times[3]), 3), "  (", round((sum(self.measured_times[3]) / len(self.measured_times[3]) / total) * 100, 2), "% )")
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
