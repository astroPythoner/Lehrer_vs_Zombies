from constants import *
from sprites import *
from math import ceil, pi

# Texte zeichnen
def draw_text(surf, text, size, x, y, font_name=HUD_FONT, color=TEXT_COLOR, rect_place="oben_mitte"):
    # Zeichnet den text in der color auf die surf.
    # x und y sind die Koordinaten des Punktes rect_place.
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

def get_text_rect(text, size, font=HUD_FONT):
    font = pygame.font.Font(font, size)
    text_surface = font.render(str(text), True, WHITE)
    return text_surface.get_rect()

def draw_display(game):
    pygame.display.set_caption("{:.2f} - {}".format(game.clock.get_fps(), version))
    # Karte
    time1 = game.make_time_measure()
    # Pro Spieler zeichnen
    for count, camera in enumerate(game.camera):
        # Karte
        try:
            shown_part_of_map = game.map_img.subsurface((camera.inverted.x, camera.inverted.y, int(game.WIDTH / len(game.players)), game.HEIGHT))
        except ValueError:
            # Screen size bigger than map
            #resize_window(min([game.map_img.get_width(), game.WIDTH * len(game.players)]), min([game.map_img.get_height(), game.HEIGHT]))
            shown_part_of_map = game.map_img.subsurface((camera.inverted.x, camera.inverted.y, int(game.WIDTH / len(game.players)), game.HEIGHT))
        game.screen.blit(shown_part_of_map, (int(game.WIDTH / len(game.players) * count), 0))

        # Bildschirm in splitscreen bereiche unterteilen
        screen_part = pygame.Rect((int(game.WIDTH / len(game.players) * count), 0), (int(game.WIDTH / len(game.players)), game.HEIGHT))
        subscreen = game.screen.subsurface(screen_part)

        # Sprites
        for sprite in game.all_sprites:
            if not (game.spielmodus == TUTORIAL and ((isinstance(sprite, Personen_Obstacle) or isinstance(sprite, Personen_Object)) and game.game_status == TUTORIAL_WALK) or (isinstance(sprite, Mob) and (game.game_status == TUTORIAL_WALK or game.game_status == TUTORIAL_COLLECT))):
                if isinstance(sprite, Mob):
                    sprite.draw_health()
                if isinstance(sprite.image, list):
                    if not game.multiplayer:
                        game.screen.blit(sprite.image[count], camera.apply(sprite))
                    else:
                        pos_rect = camera.apply(sprite)
                        subscreen.blit(sprite.image[count], pos_rect)
                else:
                    if not game.multiplayer:
                        game.screen.blit(sprite.image, camera.apply(sprite))
                    else:
                        pos_rect = camera.apply(sprite)
                        subscreen.blit(sprite.image, pos_rect)

        # Bilder auf Spieler oder Zombie malen (z.B. Sprechblasen)
        for player in game.players:
            if player.in_image_on_player:
                player_pos = camera.apply(player)
                subscreen.blit(player.image_to_place_on, (player_pos.x + player.image_verschiebung[0], player_pos.y + player.image_verschiebung[1]))
        for zombie in game.zombies:
            if zombie.in_image_on_mob:
                player_pos = camera.apply(zombie)
                subscreen.blit(zombie.image_to_place_on, (player_pos.x + zombie.image_verschiebung[0], player_pos.y + zombie.image_verschiebung[1]))

        # Kleine Kartenansicht
        if game.schoene_grafik:
            try:
                area_around_player = pygame.Surface((game.small_map_sichtweite, game.small_map_sichtweite))
                area_around_player.blit(game.map_img.subsurface(camera.player_umgebung.x, camera.player_umgebung.y, game.small_map_sichtweite, game.small_map_sichtweite), (0, 0))
                for zombie in game.zombies:
                    pygame.draw.rect(area_around_player, SMALL_MAP_ZOMBIE_COLOR, pygame.Rect(int(zombie.pos.x - camera.player_umgebung.x - game.small_map_circle_sizes[0] / 2), int(zombie.pos.y - camera.player_umgebung.y - game.small_map_circle_sizes[0] / 2), game.small_map_circle_sizes[0], game.small_map_circle_sizes[0]))
                for player in game.players:
                    pygame.draw.circle(area_around_player, SMALL_MAP_PLAYER_COLOR, (int(player.pos.x - camera.player_umgebung.x), int(player.pos.y - camera.player_umgebung.y)), game.small_map_circle_sizes[1])
                try:
                    pygame.draw.circle(area_around_player, SMALL_MAP_ENDGEGNER_COLOR, (int(game.end_gegner.pos.x - camera.player_umgebung.x), int(game.end_gegner.pos.y - camera.player_umgebung.y)), game.small_map_circle_sizes[2])
                except AttributeError:
                    pass
                area_around_player = pygame.transform.scale(area_around_player, (game.small_map_size, game.small_map_size))
                area_around_player.set_alpha(180)
                area_around_player.convert_alpha()
                if game.multiplayer:
                    if count == 1:
                        game.screen.blit(area_around_player, (game.WIDTH - 15 - game.small_map_size, int(game.HEIGHT - 30 - game.HEIGHT * 0.02 - 15 - game.BIG_TEXT - game.small_map_size)))
                        pygame.draw.rect(game.screen, BLACK, pygame.Rect(game.WIDTH - 15 - game.small_map_size, int(game.HEIGHT - 30 - game.HEIGHT * 0.02 - 15 - game.BIG_TEXT - game.small_map_size), game.small_map_size, game.small_map_size), 3)
                    else:
                        game.screen.blit(area_around_player, (15, int(game.HEIGHT - 30 - game.HEIGHT * 0.02 - 15 - game.BIG_TEXT - game.small_map_size)))
                        pygame.draw.rect(game.screen, BLACK, pygame.Rect(15, int(game.HEIGHT - 30 - game.HEIGHT * 0.02 - 15 - game.BIG_TEXT - game.small_map_size), game.small_map_size, game.small_map_size), 3)
                else:
                    game.screen.blit(area_around_player, (game.WIDTH - 15 - game.small_map_size, game.HEIGHT - 20 - 15 - game.BIG_TEXT - game.small_map_size))
                    pygame.draw.rect(game.screen, BLACK, pygame.Rect(game.WIDTH - 15 - game.small_map_size, game.HEIGHT - 20 - 15 - game.BIG_TEXT - game.small_map_size, game.small_map_size, game.small_map_size), 3)
            except Exception:
                pass
    time2 = game.make_time_measure()
    # Im splitscreen schwarze Linie an den Raendern zwischen den einzelnen Screens
    if game.multiplayer:
        for player_num in range(len(game.players)):
            if player_num != 0:
                pygame.draw.line(game.screen, BLIT_SCREEN_LINE_COLOR, (int(game.WIDTH / len(game.players) * player_num), 0), (int(game.WIDTH / len(game.players)) * player_num, game.HEIGHT), 8)
    time3 = game.make_time_measure()
    # Live Bar
    for count, player in enumerate(game.players):
        draw_live_bar(game,player, count)
    time4 = game.make_time_measure()
    # Levelfortschritt
    draw_level_fortschritts_balken(game)
    time5 = game.make_time_measure()
    # Texte: anz Zombies und gesammelte Objekte
    for count, digit in enumerate(str(len(game.zombies))):
        game.screen.blit(game.number_surfaces[int(digit)], (game.num_zombies_text_pos[0] + count * game.bigest_num_length, game.num_zombies_text_pos[1]))
    for count, pos in enumerate(game.personen_item_text_pos):
        for digit_count, digit in enumerate(str(game.werte_since_last_lehrer_change[game.players[count]]["collected_objects"])):
            game.screen.blit(game.number_surfaces[int(digit)], (int(pos[0] + digit_count * game.bigest_num_length), int(pos[1] - game.BIG_TEXT * 1.2)))
    game.screen.blit(game.forground_text_img, (0, 0))
    # Lehrerunlock
    if game.spielmodus != TUTORIAL:
        if time() - game.time_last_lehrer_unlock < 4:
            draw_text(game.screen, LEHRER[game.lehrer_unlocked_last]["anrede"] + " " + game.lehrer_unlocked_last + " freigeschaltet", game.BIG_TEXT, int(game.WIDTH / 2), int(game.HEIGHT - 20 - game.HEIGHT * 0.02 - 3 - game.BIG_TEXT - 5 - game.BIG_TEXT - 10 - 15 - game.BIG_TEXT - 12), rect_place="unten_mitte", color=LEHRER_UNLOCKED_TEXT_COLOR)
            game.screen.blit(PLAYER_IMGES[game.lehrer_unlocked_last], (int(game.WIDTH / 2 - (PLAYER_IMGES[game.lehrer_unlocked_last].get_width()) / 2), int(game.HEIGHT - 20 - game.HEIGHT * 0.02 - 3 - game.BIG_TEXT - 5 - game.BIG_TEXT - 10 - 15 - game.BIG_TEXT - 5 - game.BIG_TEXT - 12 - PLAYER_IMGES[game.lehrer_unlocked_last].get_height())))
    # Waffenupgrade
    if game.spielmodus != TUTORIAL:
        for count, player in enumerate(game.players):
            if player.weapon_upgrade_unlocked and time() - game.weapon_upgrade_unlock_times[count] < 4.5:
                draw_text(game.screen, LEHRER[player.lehrer_name]["weapon_upgrade"]["upgraded_weapon_name"] + " " + " freigeschaltet", game.BIG_TEXT, int((game.WIDTH / len(game.players)) * count + game.WIDTH / len(game.players) / 2), int(game.HEIGHT - 20 - game.HEIGHT * 0.02 - 3 - game.BIG_TEXT - 10 - 15), rect_place="unten_mitte", color=LEHRER_UNLOCKED_TEXT_COLOR)
            elif time() - game.werte_since_last_lehrer_change[player]["time_lehrer_change"] < 5:
                anz_lines = ceil(get_text_rect(LEHRER[player.lehrer_name]["weapon_upgrade"]["unlock_text"], game.BIG_TEXT).width / (game.WIDTH / len(game.players) - 30))
                letter_per_line = int(len(LEHRER[player.lehrer_name]["weapon_upgrade"]["unlock_text"]) / anz_lines)
                for line in range(anz_lines):
                    if line == anz_lines - 1:
                        draw_text(game.screen, LEHRER[player.lehrer_name]["weapon_upgrade"]["unlock_text"][letter_per_line * line:], game.BIG_TEXT, int((game.WIDTH / len(game.players)) * count + game.WIDTH / len(game.players) / 2), int(game.HEIGHT - 20 - game.HEIGHT * 0.02 - 3 - game.BIG_TEXT - 10 - 15 - (game.BIG_TEXT + 5) * (anz_lines - line)), rect_place="unten_mitte",color=LEHRER_UNLOCKED_TEXT_COLOR)
                    else:
                        draw_text(game.screen, LEHRER[player.lehrer_name]["weapon_upgrade"]["unlock_text"][letter_per_line * line:letter_per_line * (line + 1)], game.BIG_TEXT, int((game.WIDTH / len(game.players)) * count + game.WIDTH / len(game.players) / 2), int(game.HEIGHT - 20 - game.HEIGHT * 0.02 - 3 - game.BIG_TEXT - 10 - 15 - (game.BIG_TEXT + 5) * (anz_lines - line)),rect_place="unten_mitte", color=LEHRER_UNLOCKED_TEXT_COLOR)
    # Countdown vor Zombiewelle
    if game.spielmodus == ARENA_MODUS:
        if time() - game.countdown_start_time <= 5:
            size = 0.2 * game.WIDTH
            if size / game.HEIGHT > 0.4:
                size = 0.4 * game.HEIGHT
            draw_text(game.screen, str(5 - round(time() - game.countdown_start_time)), int(size), int(game.WIDTH / 2), int(game.HEIGHT / 2), color=WHITE, rect_place="mitte")
    time6 = game.make_time_measure()
    # Tutorial
    if game.spielmodus == TUTORIAL:
        if game.game_status == TUTORIAL_WALK:
            if game.with_maussteuerung:
                draw_text(game.screen, "Bewege dich mit der Maus und halte Shift zum Schleichen und rückwärts Gehen", game.NORMAL_TEXT, int(game.WIDTH / 2), int(game.HEIGHT * (1 / 3)))
                game.screen.blit(MAUS_IMG, (int(game.WIDTH / 2), 50))
            else:
                draw_text(game.screen, "Bewege dich mit den Pfeiltasten", game.NORMAL_TEXT, int(game.WIDTH / 2), int(game.HEIGHT * (1 / 3)))
                game.screen.blit(PFEILTASTE_IMG, (int(game.WIDTH / 2 - PFEILTASTE_IMG.get_rect().w / 2), 50))
        elif game.game_status == TUTORIAL_COLLECT:
            draw_text(game.screen, "Sammel die Objekte ohne auf die Hindernisse zu treten", game.NORMAL_TEXT, int(game.WIDTH / 2), int(game.HEIGHT * (1 / 3)))
        elif game.game_status == TUTORIAL_SHOOT:
            draw_text(game.screen, "Schieße mit Leertaste oder linker Maustaste auf die Zombies", game.NORMAL_TEXT, int(game.WIDTH / 2), int(game.HEIGHT * (1 / 3)))
            game.screen.blit(MAUS_LINKS_IMG, (int(game.WIDTH / 2 - MAUS_LINKS_IMG.get_rect().w / 2), 50))
            game.screen.blit(LEERTASTE_IMG, (int(game.WIDTH / 2 - LEERTASTE_IMG.get_rect().w / 2), 70 + MAUS_LINKS_IMG.get_rect().h))
        elif game.game_status == TUTORIAL_POWER_UP:
            draw_text(game.screen, "Benutzte mit X oder rechter Maustaste dein Power-Up", game.NORMAL_TEXT, int(game.WIDTH / 2), int(game.HEIGHT * (1 / 3)))
            game.screen.blit(MAUS_RECHTS_IMG, (int(game.WIDTH / 2 - MAUS_RECHTS_IMG.get_rect().w / 2), 50))
            game.screen.blit(X_Y_IMG, (int(game.WIDTH / 2 - X_Y_IMG.get_rect().w / 2), 70 + MAUS_LINKS_IMG.get_rect().h))

    if game.measure_times:
        game.measured_times[4].append(time6 - time1)
        game.measured_times[5].append(time2 - time1)
        game.measured_times[6].append(time4 - time3)
        game.measured_times[7].append(time5 - time4)
        game.measured_times[8].append(time6 - time5)

    pygame.display.flip()

def draw_live_bar(game, player, player_num):

    # Lebensanzeige
    BAR_LENGTH = 0.95 * game.live_bar_img_width
    BAR_HEIGHT = 0.075 * game.live_bar_img_height
    # Prozentualelaenge berechnen
    if player.health / LEHRER[player.lehrer_name]["player_health"] < 0:
        pct = 0
    else:
        pct = player.health / LEHRER[player.lehrer_name]["player_health"]
    if game.multiplayer and player_num >= game.num_players_in_multiplayer / 2:
        fill_rect = pygame.Rect(int(game.WIDTH - (int(game.WIDTH / game.num_players_in_multiplayer) * (game.num_players_in_multiplayer - player_num - 1)) - int(BAR_LENGTH) - int(0.031 * game.live_bar_img_width)), int(0.0426829 * game.live_bar_img_height), int(pct * BAR_LENGTH), int(BAR_HEIGHT))
    else:
        fill_rect = pygame.Rect(int((0.031 * game.live_bar_img_width) + ((game.WIDTH / game.num_players_in_multiplayer) * (player_num))), int(0.0426829 * game.live_bar_img_height), int(pct * BAR_LENGTH), int(BAR_HEIGHT))
    # Farbe
    if pct > 0.6:
        col = LEBENSANZEIGE_GRUEN
    elif pct > 0.3:
        col = LEBENSANZEIGE_GELB
    else:
        col = LEBENSANZEIGE_ROT
    # Rechteck zeichnen
    pygame.draw.rect(game.screen, col, fill_rect)

    # Power-Up
    if time() * 1000 - game.last_power_up_use_time[game.players.index(player)] < LEHRER[player.lehrer_name]["power_up_time"]:
        if game.multiplayer and player_num >= game.num_players_in_multiplayer / 2:
            rect = pygame.Rect((int(game.WIDTH - ((game.WIDTH / game.num_players_in_multiplayer) * (game.num_players_in_multiplayer - player_num - 1)) - int(0.345 * game.live_bar_img_width) - int(0.0139 * game.live_bar_img_width)), int(0.1891 * game.live_bar_img_height)), (int(0.345 * game.live_bar_img_width), int(0.757 * game.live_bar_img_height)))

        else:
            rect = pygame.Rect((int((0.0139 * game.live_bar_img_width) + ((game.WIDTH / game.num_players_in_multiplayer) * (player_num))), int(0.1891 * game.live_bar_img_height)), (int(0.345 * game.live_bar_img_width), int(0.757 * game.live_bar_img_height)))
        pygame.draw.arc(game.screen, POWER_UP_TIME_COLOR, rect, - ((2 * pi / LEHRER[player.lehrer_name]["power_up_time"]) * (time() * 1000 - game.last_power_up_use_time[game.players.index(player)])) + pi/2, pi/2, int(0.022 * game.live_bar_img_width))
    else:
        if game.multiplayer and player_num >= game.num_players_in_multiplayer / 2:
            pygame.draw.circle(game.screen, POWER_UP_TIME_COLOR, (int(game.WIDTH - ((game.WIDTH / game.num_players_in_multiplayer) * (game.num_players_in_multiplayer - player_num - 1)) - int(0.187 * game.live_bar_img_width)), int(0.568 * game.live_bar_img_height)), int(0.176 * game.live_bar_img_width), int(0.022 * game.live_bar_img_width))

        else:
            pygame.draw.circle(game.screen, POWER_UP_TIME_COLOR, (int((0.187 * game.live_bar_img_width) + ((game.WIDTH / game.num_players_in_multiplayer) * (player_num))), int(0.568 * game.live_bar_img_height)), int(0.176 * game.live_bar_img_width), int(0.022 * game.live_bar_img_width))

    # Live Bar Bild oben drauf
    if game.multiplayer and player_num >= game.num_players_in_multiplayer / 2:
        game.screen.blit(game.live_bar_images[player_num], (int(game.WIDTH - ((game.WIDTH / game.num_players_in_multiplayer) * (game.num_players_in_multiplayer - player_num - 1)) - game.live_bar_images[player_num].get_width()), 0))
    else:
        game.screen.blit(game.live_bar_images[player_num], (int((game.WIDTH / game.num_players_in_multiplayer) * (player_num)), 0))

def draw_level_fortschritts_balken(game):
    if game.game_status != COLLECTING_AT_END and game.spielmodus != TUTORIAL:
        # Prozentualelaenge berechnen
        if game.genauerer_spielmodus == AFTER_TIME:
            if game.spielmodus == MAP_MODUS:
                pct = (time() - game.level_start_time) / TIME_MAP_LEVEL
            elif game.spielmodus == ARENA_MODUS:
                if time() - game.countdown_start_time <= 6:
                    pct = (game.num_zombie_wave - 1) / 3
                else:
                    if game.num_zombie_wave == 3:
                        if game.multiplayer:
                            pct = (ENDGEGNER_HEALTH_MULTIPLAYER[game.schwierigkeit - 1] - game.end_gegner.health) / ENDGEGNER_HEALTH_MULTIPLAYER[game.schwierigkeit - 1] / 3 + (game.num_zombie_wave - 1) / 3
                        else:
                            pct = (ENDGEGNER_HEALTH[game.schwierigkeit - 1] - game.end_gegner.health) / ENDGEGNER_HEALTH[game.schwierigkeit - 1] / 3 + (game.num_zombie_wave - 1) / 3
                    else:
                        pct = (time() - game.last_zombie_wave_time) / TIME_BETWEEN_ZOMBIE_WAVES / 3 + (game.num_zombie_wave - 1) / 3
        elif game.genauerer_spielmodus == AFTER_KILLED:
            if game.spielmodus == MAP_MODUS:
                if game.level_start_num_zombies > 0:
                    pct = ((game.level_start_num_zombies - len(game.zombies)) / game.level_start_num_zombies)
                else:
                    pct = 0
            elif game.spielmodus == ARENA_MODUS:
                if time() - game.countdown_start_time <= 6:
                    pct = (game.num_zombie_wave - 1) / 3
                else:
                    if game.num_zombie_wave == 3:
                        if game.multiplayer:
                            pct = (ENDGEGNER_HEALTH_MULTIPLAYER[game.schwierigkeit - 1] - game.end_gegner.health) / ENDGEGNER_HEALTH_MULTIPLAYER[game.schwierigkeit - 1] / 3 + (game.num_zombie_wave - 1) / 3
                        else:
                            pct = (ENDGEGNER_HEALTH[game.schwierigkeit - 1] - game.end_gegner.health) / ENDGEGNER_HEALTH[game.schwierigkeit - 1] / 3 + (game.num_zombie_wave - 1) / 3
                    else:
                        pct = ((game.level_start_num_zombies - len(game.zombies)) / game.level_start_num_zombies) / 3 + (game.num_zombie_wave - 1) / 3
        # Rechteck zeichnen
        pygame.draw.rect(game.screen, LEVEL_FORTSCHRITTS_FARBE, pygame.Rect((15, int(game.HEIGHT - 20 - game.level_bar_height)), (int(pct * game.level_bar_lenght), int(game.level_bar_height))), 0)