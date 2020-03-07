from constants import *
from drawing import draw_text, get_text_rect

def resize_window(game, width, height):
    ### Resize the sreen ###
    game.WIDTH = width
    game.HEIGHT = height
    game.screen = pygame.display.set_mode((game.WIDTH, game.HEIGHT), pygame.RESIZABLE)
    game.GRIDWIDTH = int(start_width / TILESIZE)
    game.GRIDHEIGHT = int(start_height / TILESIZE)
    game.small_map_sichtweite = calculate_fit_size(game,SMALL_MAP_SICHTWEITE_FAKTOR, SMALL_MAP_SICHTWEITE_FAKTOR)
    game.maussteuerung_circle_radius = calculate_fit_size(game,0.35, 0.35)
    game.background = pygame.transform.scale(background, (game.WIDTH, game.HEIGHT))
    game.background_rect = game.background.get_rect()
    update_text_sizes(game)
    game.number_surfaces = {}
    game.bigest_num_length = 0
    for x in range(10):
        rect = get_text_rect(x, game.BIG_TEXT)
        if rect.width > game.bigest_num_length:
            game.bigest_num_length = rect.width
    for x in range(10):
        surf = pygame.Surface((game.bigest_num_length, int(game.BIG_TEXT * 1.2)), pygame.SRCALPHA)
        draw_text(surf, x, game.BIG_TEXT, 0, 0, rect_place="oben_links")
        game.number_surfaces[x] = surf
    if game.WIDTH / game.HEIGHT < 0.4555555:
        game.live_bar_img_width = int(0.375 * game.WIDTH)
        game.live_bar_img_height = int(game.live_bar_img_width / 360 * 164)
    else:
        game.live_bar_img_height = int(0.25625 * game.HEIGHT)
        game.live_bar_img_width = int(game.live_bar_img_height / 164 * 360)
    game.longest_lehrer_name = 0
    game.longest_weapon_name = 0
    game.longest_object_name = 0
    for lehrer in LEHRER:
        width = get_text_rect(LEHRER[lehrer]["anrede"] + " " + lehrer, game.HUGE_TEXT).width
        if width > game.longest_lehrer_name:
            game.longest_lehrer_name = width
        width = get_text_rect("Waffe: " + str(LEHRER[lehrer]["weapon_name"]), game.SMALL_TEXT, ARIAL_FONT).width
        if width > game.longest_weapon_name:
            game.longest_weapon_name = width
        width = get_text_rect(str(LEHRER[lehrer]["personen_item_text"]) + ":" + str(99), game.BIG_TEXT).width
        if width > game.longest_object_name:
            game.longest_object_name = width
    update_lehrer_selection_pictures(game,)
    if game.game_status != BEFORE_FIRST_GAME:
        game.update_forground_text_img()
        for count, player in enumerate(game.players):
            game.update_live_bar_image(player, count)
        for count, camera in enumerate(game.camera):
            camera.update(game.players[count])
        if game.multiplayer:
            game.small_map_size = calculate_fit_size(game,0.23, 0.23)
        else:
            game.small_map_size = calculate_fit_size(game,0.3, 0.3)
    game.clock.tick(FPS)

def calculate_fit_size(game, max_width_faktor, max_height_faktor):
    ### caltulate size so it fits to WIDTH and HEIGHT
    size = max_width_faktor * game.WIDTH
    if size / game.HEIGHT > max_height_faktor:
        size = max_height_faktor * game.HEIGHT
    return int(size)

def update_text_sizes(game):
    ### calulate textsizes depending on screen size ###
    # Textgroessen
    game.GIANT_TEXT = calculate_fit_size(game,0.0666, 0.1)
    game.HUGE_TEXT = calculate_fit_size(game,0.0416, 0.0625)
    game.BIG_TEXT = calculate_fit_size(game,0.0333, 0.05)
    game.NORMAL_TEXT = calculate_fit_size(game,0.02708, 0.040625)
    game.SMALL_TEXT = calculate_fit_size(game,0.0208, 0.03125)

def update_live_bar_image(game, player, player_num):
    ### update live bar image ###
    surface = pygame.Surface((int(game.live_bar_img_width + game.WIDTH / 3), int(game.live_bar_img_height + game.HEIGHT / 4)), pygame.SRCALPHA)
    bild_breite = surface.get_width()

    # Power-Up Icon
    if game.multiplayer and player_num >= game.num_players_in_multiplayer / 2:
        surface.blit(pygame.transform.scale(PERSONEN_POWER_UP_ICONS[player.lehrer_name], (int(0.338888 * game.live_bar_img_width), int(0.743902 * game.live_bar_img_height))),(bild_breite - int(0.338888 * game.live_bar_img_width) - int(0.01666 * game.live_bar_img_width), int(0.195122 * game.live_bar_img_height)))
    else:
        surface.blit(pygame.transform.scale(PERSONEN_POWER_UP_ICONS[player.lehrer_name], (int(0.338888 * game.live_bar_img_width), int(0.743902 * game.live_bar_img_height))),(int(0.01666 * game.live_bar_img_width), int(0.195122 * game.live_bar_img_height)))

    # Neutrales Icon
    if game.multiplayer and player_num >= game.num_players_in_multiplayer / 2:
        surface.blit(pygame.transform.scale(PEROSNEN_OBJECT_IMGES[player.lehrer_name]["icon"], (int(0.13611 * game.live_bar_img_width), int(0.13611 * game.live_bar_img_width))),(bild_breite - int(0.13611 * game.live_bar_img_width) - int(0.40833 * game.live_bar_img_width), int(0.182926 * game.live_bar_img_height)))
    else:
        surface.blit(pygame.transform.scale(PEROSNEN_OBJECT_IMGES[player.lehrer_name]["icon"], (int(0.13611 * game.live_bar_img_width), int(0.13611 * game.live_bar_img_width))),(int(0.40833 * game.live_bar_img_width), int(0.182926 * game.live_bar_img_height)))

    # Schelchtes Icon
    if game.multiplayer and player_num >= game.num_players_in_multiplayer / 2:
        surface.blit(pygame.transform.scale(PERSONEN_OBSTACLE_IMGES[player.lehrer_name]["icon"], (int(0.13611 * game.live_bar_img_width), int(0.13611 * game.live_bar_img_width))),(bild_breite - int(0.13611 * game.live_bar_img_width) - int(0.3722 * game.live_bar_img_width), int(0.52439 * game.live_bar_img_height)))
    else:
        surface.blit(pygame.transform.scale(PERSONEN_OBSTACLE_IMGES[player.lehrer_name]["icon"], (int(0.13611 * game.live_bar_img_width), int(0.13611 * game.live_bar_img_width))),(int(0.3722 * game.live_bar_img_width), int(0.52439 * game.live_bar_img_height)))

    # Live Bar Bild oben drauf
    if game.multiplayer and player_num >= game.num_players_in_multiplayer / 2:
        surface.blit(pygame.transform.flip(pygame.transform.scale(LIVE_BAR_IMG, (int(game.live_bar_img_width), int(game.live_bar_img_height))), True, False), (bild_breite - game.live_bar_img_width, 0))
    else:
        surface.blit(pygame.transform.scale(LIVE_BAR_IMG, (int(game.live_bar_img_width), int(game.live_bar_img_height))), (0, 0))

    # Texte zum Lehrer
    if game.multiplayer and player_num >= game.num_players_in_multiplayer / 2:
        draw_text(surface, LEHRER[player.lehrer_name]["anrede"] + " " + LEHRER[player.lehrer_name]["name"], game.NORMAL_TEXT, int(bild_breite - 0.6805 * game.live_bar_img_width), int(0.165 * game.live_bar_img_height), rect_place="oben_rechts")
    else:
        draw_text(surface, LEHRER[player.lehrer_name]["anrede"] + " " + LEHRER[player.lehrer_name]["name"], game.NORMAL_TEXT, int(0.6805 * game.live_bar_img_width), int(0.165 * game.live_bar_img_height), rect_place="oben_links")
    # Beschreibung umbrechen und dann jede Zeile einzeln zeichnen
    beschreibungs_texte = [""]
    array_num = 0
    for count, letter in enumerate(LEHRER[player.lehrer_name]["personen_beschreibung"]):
        beschreibungs_texte[array_num] += letter
        if count % 20 == 0 and count != 0:
            array_num += 1
            beschreibungs_texte.append("")
    for count, text in enumerate(beschreibungs_texte):
        if game.multiplayer and player_num >= game.num_players_in_multiplayer / 2:
            draw_text(surface, beschreibungs_texte[count], game.SMALL_TEXT, int(bild_breite - 0.569444 * game.live_bar_img_width), int(0.2 * game.live_bar_img_height + game.NORMAL_TEXT + count * (game.SMALL_TEXT + 5)), rect_place="oben_rechts", font_name=ARIAL_FONT, color=BLACK)
        else:
            draw_text(surface, beschreibungs_texte[count], game.SMALL_TEXT, int(0.569444 * game.live_bar_img_width), int(0.2 * game.live_bar_img_height + game.NORMAL_TEXT + count * (game.SMALL_TEXT + 5)), rect_place="oben_links", font_name=ARIAL_FONT, color=BLACK)

    game.live_bar_images[player_num] = surface

def update_forground_text_img(game):
    ### update image with textes on game ###
    surface = pygame.Surface((game.WIDTH, game.HEIGHT), pygame.SRCALPHA)
    game.personen_item_text_pos = []
    # Texte
    if game.multiplayer:
        rect = draw_text(surface, 'Zombies: ', game.BIG_TEXT, int(game.WIDTH / 2 - (3 * game.bigest_num_length) / 2), 0, rect_place="oben_mitte")
        game.num_zombies_text_pos = (int(game.WIDTH / 2 - (3 * game.bigest_num_length) / 2 + rect.width / 2), 0)
        for count, player in enumerate(game.players):
            if count >= game.num_players_in_multiplayer / 2:
                rect = draw_text(surface, LEHRER[player.lehrer_name]["personen_item_text"] + ": ", game.BIG_TEXT, int(game.WIDTH - ((game.WIDTH / game.num_players_in_multiplayer) * (game.num_players_in_multiplayer - count - 1)) - 10 - 2 * game.bigest_num_length), int(game.HEIGHT - 30 - game.HEIGHT * 0.02), rect_place="unten_rechts")
                game.personen_item_text_pos.append((int(game.WIDTH - ((game.WIDTH / game.num_players_in_multiplayer) * (game.num_players_in_multiplayer - count - 1)) - 10 - 2 * game.bigest_num_length), int(game.HEIGHT - 30 - game.HEIGHT * 0.02)))
            else:
                rect = draw_text(surface, LEHRER[player.lehrer_name]["personen_item_text"] + ": ", game.BIG_TEXT, int(10 + ((game.WIDTH / game.num_players_in_multiplayer) * (count))), int(game.HEIGHT - 30 - game.HEIGHT * 0.02), rect_place="unten_links")
                game.personen_item_text_pos.append((10 + ((int(game.WIDTH / game.num_players_in_multiplayer) * (count)) + rect.width), int(game.HEIGHT - 30 - game.HEIGHT * 0.02)))
    else:
        rect = draw_text(surface, 'Zombies: ', game.BIG_TEXT, game.WIDTH - 10 - 3 * game.bigest_num_length, 0, rect_place="oben_rechts")
        game.num_zombies_text_pos = (game.WIDTH - 10 - 3 * game.bigest_num_length, 0)
        rect = draw_text(surface, LEHRER[game.players[0].lehrer_name]["personen_item_text"] + ": ", game.BIG_TEXT, game.WIDTH - 10 - 2 * game.bigest_num_length, game.HEIGHT - 20, rect_place="unten_rechts")
        game.personen_item_text_pos = [(game.WIDTH - 10 - 2 * game.bigest_num_length, game.HEIGHT - 20)]
    if game.spielmodus == ARENA_MODUS:
        if game.multiplayer:
            draw_text(surface, 'Welle: ' + str(game.num_zombie_wave), game.BIG_TEXT, int(game.WIDTH / 2), int(game.HEIGHT - 20 - game.HEIGHT * 0.02 - 3 - game.BIG_TEXT - 10), rect_place="oben_mitte")
        else:
            draw_text(surface, 'Welle: ' + str(game.num_zombie_wave), game.BIG_TEXT, 10, int(game.HEIGHT - 20 - game.HEIGHT * 0.02 - 3 - game.BIG_TEXT - 10), rect_place="oben_links")

    if game.multiplayer:
        game.level_bar_lenght = game.WIDTH - 15 - 15
    else:
        game.level_bar_lenght = game.WIDTH - game.longest_object_name - 15 - 15 - 10
    game.level_bar_height = game.HEIGHT * 0.02
    if game.game_status == COLLECTING_AT_END:
        draw_text(surface, TEXT_FIND_AT_END, game.BIG_TEXT, 15, int(game.HEIGHT - 17 - game.BIG_TEXT), rect_place="oben_links", color=LEVEL_FORTSCHRITTS_FARBE)
    else:
        if game.spielmodus == ARENA_MODUS:
            for x in range(3):
                pygame.draw.circle(surface, LEVEL_FORTSCHRITTS_FARBE, (int(15 + game.level_bar_lenght / 3 * x), int(game.HEIGHT - 20 - game.level_bar_height / 2)), int(game.level_bar_height * 0.8), 3)
        if game.spielmodus != TUTORIAL:
            pygame.draw.rect(surface, LEVEL_FORTSCHRITTS_FARBE, pygame.Rect((15, int(game.HEIGHT - 20 - game.level_bar_height - 3)), (game.level_bar_lenght + 6, int(game.level_bar_height + 6))), 3)

    game.forground_text_img = surface

def update_lehrer_selection_pictures(game):
    ### redraw pictures for selection of teachers ###
    if game.multiplayer:
        lehrer_asuwahl_breite = int(game.WIDTH / game.num_players_in_multiplayer)
    else:
        lehrer_asuwahl_breite = game.WIDTH

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
        draw_text(surf, LEHRER[lehrer]["anrede"] + " " + LEHRER[lehrer]["name"], game.HUGE_TEXT, 15, 15, rect_place="oben_links", color=AUSWAHL_TEXT_COLOR)
        # Bild des Lehrers
        surf.blit(PLAYER_IMGES[lehrer], (game.longest_lehrer_name + 30, 15))

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
        total_width = 15 + 49 + 10 + 49 + 20 + 25 + 5 + game.longest_weapon_name
        # _  ↓  _  ↓  _  ↓ _         ↓
        # Neutr Schlecht Waffe     Waffenname
        if game.longest_lehrer_name + 30 + 49 + 35 + total_width < lehrer_asuwahl_breite:
            kleine_bilder_tiefer = False
            distance_from_right_side = 0
            if game.longest_lehrer_name + 30 + 49 + 35 + total_width + 122 < lehrer_asuwahl_breite:  # normal size (Power-up passt auchnoch daneben)
                distance_from_right_side = 125
            # Waffe zeichnen
            if isinstance(BULLET_IMGES[lehrer], type(dict)):
                surf.blit(pygame.transform.scale(BULLET_IMGES[lehrer][list(BULLET_IMGES[lehrer])[0]], (end_breite, end_hoehe)), (lehrer_asuwahl_breite - distance_from_right_side - 15 - 49 - 10 - 49 - 20 - 25, 22))
            else:
                surf.blit(pygame.transform.scale(BULLET_IMGES[lehrer], (end_breite, end_hoehe)), (lehrer_asuwahl_breite - distance_from_right_side - 15 - 49 - 10 - 49 - 20 - 25, 22))
            draw_text(surf, "Waffe: " + str(LEHRER[lehrer]["weapon_name"]), game.SMALL_TEXT, lehrer_asuwahl_breite - distance_from_right_side - 15 - 49 - 10 - 49 - 20 - 25 - 5, 22, rect_place="oben_rechts", font_name=ARIAL_FONT, color=AUSWAHL_TEXT_COLOR)
            # Neutrales Objekt zeichnen
            surf.blit(PEROSNEN_OBJECT_IMGES[lehrer]["icon"], (lehrer_asuwahl_breite - distance_from_right_side - 15 - 49, 12))
            # Schlechtes Objekt zeichnen
            surf.blit(PERSONEN_OBSTACLE_IMGES[lehrer]["icon"], (lehrer_asuwahl_breite - distance_from_right_side - 15 - 49 - 10 - 49, 12))
        else:  # Bilder muessen drunter gezeichnet werden
            kleine_bilder_tiefer = True
            # Waffe zeichnen
            if isinstance(BULLET_IMGES[lehrer], type(dict)):
                surf.blit(pygame.transform.scale(BULLET_IMGES[lehrer][list(BULLET_IMGES[lehrer])[0]], (end_breite, end_hoehe)), (15, 22 + max([game.HUGE_TEXT + 10, 50])))
            else:
                surf.blit(pygame.transform.scale(BULLET_IMGES[lehrer], (end_breite, end_hoehe)), (15, 22 + max([game.HUGE_TEXT + 10, 50])))
            draw_text(surf, "Waffe: " + str(LEHRER[lehrer]["weapon_name"]), game.SMALL_TEXT, 15 + 25 + 5, 22 + max([game.HUGE_TEXT + 10, 50]), rect_place="oben_links", font_name=ARIAL_FONT, color=AUSWAHL_TEXT_COLOR)
            # Neutrales Objekt zeichnen
            surf.blit(PEROSNEN_OBJECT_IMGES[lehrer]["icon"], (15 + 25 + 5 + game.longest_weapon_name + 20, 12 + max([game.HUGE_TEXT + 10, 50])))
            # Schlechtes Objekt zeichnen
            surf.blit(PERSONEN_OBSTACLE_IMGES[lehrer]["icon"], (15 + 25 + 5 + game.longest_weapon_name + 20 + 49 + 10, 12 + max([game.HUGE_TEXT + 10, 50])))

        # Power-Up
        if game.longest_lehrer_name + 30 + 49 + 35 + total_width + 122 < lehrer_asuwahl_breite:  # normal size -> power_up oben rechts
            power_up_img_oben = True
            surf.blit(PERSONEN_POWER_UP_ICONS[lehrer], (lehrer_asuwahl_breite - 125, 15))
        else:  # power_up 50 pixel weiter unten rechts
            power_up_img_oben = False
            surf.blit(PERSONEN_POWER_UP_ICONS[lehrer], (lehrer_asuwahl_breite - 125, 15 + max([game.HUGE_TEXT + 10, 50])))

        # Beschreibung
        # herausfinden wie viele Zeichen noch vor das Power-Up Bild passen
        lehrer_beschreibung = LEHRER[lehrer]["personen_beschreibung"]
        platz_fuer_beschreibung = lehrer_asuwahl_breite - 125
        # umbrechen
        letzter_umbruch = 0
        einzelne_texte = []
        for letter_count, letter in enumerate(lehrer_beschreibung):
            if get_text_rect(lehrer_beschreibung[letzter_umbruch:letter_count], game.SMALL_TEXT).width > platz_fuer_beschreibung:
                einzelne_texte.append(lehrer_beschreibung[letzter_umbruch:letter_count])
                letzter_umbruch = letter_count
        einzelne_texte.append(lehrer_beschreibung[letzter_umbruch:len(lehrer_beschreibung)])
        # ausgeben
        unteres_ende_beschreibung = 0
        for text_count, text in enumerate(einzelne_texte):
            if not kleine_bilder_tiefer:
                rect = draw_text(surf, text, game.SMALL_TEXT, 15, 15 + game.HUGE_TEXT + 10 + text_count * (game.SMALL_TEXT + 5), rect_place="oben_links", font_name=ARIAL_FONT, color=AUSWAHL_TEXT_COLOR)
            else:
                rect = draw_text(surf, text, game.SMALL_TEXT, 15, 15 + game.HUGE_TEXT + 10 + max([game.HUGE_TEXT + 10, 50]) + text_count * (game.SMALL_TEXT + 5), rect_place="oben_links", font_name=ARIAL_FONT, color=AUSWAHL_TEXT_COLOR)
            unteres_ende_beschreibung = rect.bottom

        # Kurzinfo
        game.screen.blit(SMALL_HEART_IMG, (15, unteres_ende_beschreibung + 16))
        infotexte = [str(LEHRER[lehrer]["player_health"]), "Geschw:" + str(LEHRER[lehrer]["player_speed"]), "Powerup zeit:" + str(round(LEHRER[lehrer]["power_up_time"] / 1000, 1)), "Nachladezeit:" + str(LEHRER[lehrer]["weapon_rate"]), "Ungenauigkeit:" + str(LEHRER[lehrer]["weapon_spread"]),
                     "Schussweite:" + str(round((LEHRER[lehrer]["weapon_bullet_speed"] * LEHRER[lehrer]["weapon_lifetime"]) / 1000)), "Schaden:" + str(LEHRER[lehrer]["weapon_damage"])]
        rechte_kante_letzter_text = 28
        zeile = 0
        unteres_ende = 0
        for text in infotexte:
            if rechte_kante_letzter_text + 7 + get_text_rect(text, game.SMALL_TEXT, ARIAL_FONT).width > platz_fuer_beschreibung:
                zeile += 1
                rechte_kante_letzter_text = 8
            rect = draw_text(surf, text, game.SMALL_TEXT, rechte_kante_letzter_text + 7, unteres_ende_beschreibung + 25 + (game.SMALL_TEXT + 5) * zeile, rect_place="mitte_links", font_name=ARIAL_FONT, color=AUSWAHL_TEXT_COLOR)
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
        game.lehrer_selection_surfaces[lehrer] = cropped