from constants import *
from window_resize import *
from time import time
from drawing import draw_text

# Hauptbildschirm
def draw_start_game_screen(game, cursor_pos, loading=False):
    return_dict = {}

    # Hintergrund
    game.screen.blit(game.background, game.background_rect)

    # Einstellungen
    if cursor_pos[0] == 0 and cursor_pos[1] <= int(max([len(MAP_NAMES) - 1, 4]) / 2):
        return_dict["Einstellungen"] = draw_text(game.screen, "Einstellungen", game.NORMAL_TEXT, 10, 10, rect_place="oben_links", color=AUSWAHL_TEXT_SELECTED)
    else:
        return_dict["Einstellungen"] = draw_text(game.screen, "Einstellungen", game.NORMAL_TEXT, 10, 10, rect_place="oben_links", color=AUSWAHL_TEXT_COLOR)

    # Spielerkaerung
    if cursor_pos[0] == 0 and cursor_pos[1] > int(max([len(MAP_NAMES) - 1, 4]) / 2):
        return_dict["Hilfe"] = draw_text(game.screen, "Hilfe/Erklärung", game.NORMAL_TEXT, game.WIDTH - 10, 10, rect_place="oben_rechts", color=AUSWAHL_TEXT_SELECTED)
    else:
        return_dict["Hilfe"] = draw_text(game.screen, "Hilfe/Erklärung", game.NORMAL_TEXT, game.WIDTH - 10, 10, rect_place="oben_rechts", color=AUSWAHL_TEXT_COLOR)

    # Titel
    if game.game_status == PLAYER_DIED:
        draw_text(game.screen, "GAME OVER", game.GIANT_TEXT, int(game.WIDTH / 2), int(game.HEIGHT * 0.13), rect_place="mitte", color=AUSWAHL_TEXT_RED)
    elif game.game_status == WON_GAME:
        draw_text(game.screen, "YOU WON", game.GIANT_TEXT, int(game.WIDTH / 2), int(game.HEIGHT * 0.13), rect_place="mitte", color=AUSWAHL_TEXT_GREEN)
    else:
        draw_text(game.screen, "Zombie!", game.GIANT_TEXT, int(game.WIDTH / 2), int(game.HEIGHT * 0.13), rect_place="mitte", color=AUSWAHL_TEXT_COLOR)

    # Schwierigkeit
    circle_size = calculate_fit_size(game,0.026, 0.039)
    draw_text(game.screen, "Schwierigkeit", int(game.BIG_TEXT * 1.2), int(game.WIDTH / 2), int(game.HEIGHT * 0.25), color=AUSWAHL_TEXT_COLOR)
    pygame.draw.line(game.screen, AUSWAHL_TEXT_COLOR, (int(game.WIDTH * (1 / 6)), int(game.HEIGHT * 0.38)), (int(game.WIDTH * (5 / 6)), int(game.HEIGHT * 0.38)), 5)
    for schwierigkeitsstufe in range(1, 6):
        if game.schwierigkeit == schwierigkeitsstufe and not loading:
            if cursor_pos[0] == 1 and (cursor_pos[1] == schwierigkeitsstufe - 1 or schwierigkeitsstufe == 5 and cursor_pos[1] > 4):
                return_dict["Schwierigkeit_" + str(schwierigkeitsstufe)] = pygame.draw.circle(game.screen, AUSWAHL_TEXT_GREEN_SELECTED, (int(game.WIDTH * (schwierigkeitsstufe / 6)), int(game.HEIGHT * 0.38)), circle_size, 0)
            else:
                return_dict["Schwierigkeit_" + str(schwierigkeitsstufe)] = pygame.draw.circle(game.screen, AUSWAHL_TEXT_GREEN, (int(game.WIDTH * (schwierigkeitsstufe / 6)), int(game.HEIGHT * 0.38)), circle_size, 0)
        elif cursor_pos[0] == 1 and (cursor_pos[1] == schwierigkeitsstufe - 1 or schwierigkeitsstufe == 5 and cursor_pos[1] > 4):
            return_dict["Schwierigkeit_" + str(schwierigkeitsstufe)] = pygame.draw.circle(game.screen, AUSWAHL_TEXT_SELECTED, (int(game.WIDTH * (schwierigkeitsstufe / 6)), int(game.HEIGHT * 0.38)), circle_size, 0)
        else:
            return_dict["Schwierigkeit_" + str(schwierigkeitsstufe)] = pygame.draw.circle(game.screen, AUSWAHL_TEXT_COLOR, (int(game.WIDTH * (schwierigkeitsstufe / 6)), int(game.HEIGHT * 0.38)), circle_size, 0)
        draw_text(game.screen, str(schwierigkeitsstufe), int(circle_size * 1.3), int(game.WIDTH * (schwierigkeitsstufe / 6)), int(game.HEIGHT * 0.38), color=BLACK, rect_place="mitte")

    # Spielmodus
    draw_text(game.screen, "SPIELMODUS", int(game.BIG_TEXT * 1.2), int(game.WIDTH / 2), int(game.HEIGHT * 0.47), color=AUSWAHL_TEXT_COLOR)
    if game.spielmodus == MAP_MODUS and not loading:
        if cursor_pos[0] == 2 and cursor_pos[1] > int(max([len(MAP_NAMES) - 1, 4]) / 2):
            spielmodus_rect = draw_text(game.screen, "Zombie Map", game.NORMAL_TEXT, int(game.WIDTH * 2 / 3), int(game.HEIGHT * 0.57), color=AUSWAHL_TEXT_GREEN_SELECTED, rect_place="mitte")
        else:
            spielmodus_rect = draw_text(game.screen, "Zombie Map", game.NORMAL_TEXT, int(game.WIDTH * 2 / 3), int(game.HEIGHT * 0.57), color=AUSWAHL_TEXT_GREEN, rect_place="mitte")
        return_dict[MAP_MODUS] = spielmodus_rect
    elif cursor_pos[0] == 2 and cursor_pos[1] > int(max([len(MAP_NAMES) - 1, 4]) / 2):
        rect = draw_text(game.screen, "Zombie Map", game.NORMAL_TEXT, int(game.WIDTH * 2 / 3), int(game.HEIGHT * 0.57), color=AUSWAHL_TEXT_SELECTED, rect_place="mitte")
        return_dict[MAP_MODUS] = rect
    elif game.spielmodus != MAP_MODUS or loading:
        return_dict[MAP_MODUS] = draw_text(game.screen, "Zombie Map", game.NORMAL_TEXT, int(game.WIDTH * 2 / 3), int(game.HEIGHT * 0.57), color=AUSWAHL_TEXT_COLOR, rect_place="mitte")
        if loading and game.spielmodus == MAP_MODUS:
            spielmodus_rect = return_dict[MAP_MODUS]
    if game.spielmodus == ARENA_MODUS and not loading:
        if cursor_pos[0] == 2 and cursor_pos[1] <= int(max([len(MAP_NAMES) - 1, 4]) / 2):
            spielmodus_rect = draw_text(game.screen, "Arena Modus", game.NORMAL_TEXT, int(game.WIDTH * 1 / 3), int(game.HEIGHT * 0.57), color=AUSWAHL_TEXT_GREEN_SELECTED, rect_place="mitte")
        else:
            spielmodus_rect = draw_text(game.screen, "Arena Modus", game.NORMAL_TEXT, int(game.WIDTH * 1 / 3), int(game.HEIGHT * 0.57), color=AUSWAHL_TEXT_GREEN, rect_place="mitte")
        return_dict[ARENA_MODUS] = spielmodus_rect
    elif cursor_pos[0] == 2 and cursor_pos[1] <= int(max([len(MAP_NAMES) - 1, 4]) / 2):
        rect = draw_text(game.screen, "Arena Modus", game.NORMAL_TEXT, int(game.WIDTH * 1 / 3), int(game.HEIGHT * 0.57), color=AUSWAHL_TEXT_SELECTED, rect_place="mitte")
        return_dict[ARENA_MODUS] = rect
    elif game.spielmodus != ARENA_MODUS or loading:
        return_dict[ARENA_MODUS] = draw_text(game.screen, "Arena Modus", game.NORMAL_TEXT, int(game.WIDTH * 1 / 3), int(game.HEIGHT * 0.57), color=AUSWAHL_TEXT_COLOR, rect_place="mitte")
        if loading and game.spielmodus == ARENA_MODUS:
            spielmodus_rect = return_dict[ARENA_MODUS]
    # weitere Spielmodus einstellung
    if game.spielmodus == MAP_MODUS:
        pygame.draw.line(game.screen, AUSWAHL_TEXT_COLOR, spielmodus_rect.midbottom, (int(game.WIDTH * 2 / 4), int(game.HEIGHT * 0.62)), 3)
        pygame.draw.line(game.screen, AUSWAHL_TEXT_COLOR, spielmodus_rect.midbottom, (int(game.WIDTH * 3 / 4), int(game.HEIGHT * 0.62)), 3)
        if game.genauerer_spielmodus == AFTER_TIME and not loading:
            if cursor_pos[0] == 3 and cursor_pos[1] <= int(max([len(MAP_NAMES) - 1, 4]) / 2):
                return_dict[AFTER_TIME + "0"] = draw_text(game.screen, "Gewonnen nach", game.NORMAL_TEXT, int(game.WIDTH * 2 / 4), int(game.HEIGHT * 0.62), color=AUSWAHL_TEXT_GREEN_SELECTED, rect_place="oben_mitte")
                return_dict[AFTER_TIME + "1"] = draw_text(game.screen, "Zeit", game.NORMAL_TEXT, int(game.WIDTH * 2 / 4), int(game.HEIGHT * 0.62) + game.NORMAL_TEXT + 5, color=AUSWAHL_TEXT_GREEN_SELECTED, rect_place="oben_mitte")
            else:
                return_dict[AFTER_TIME + "0"] = draw_text(game.screen, "Gewonnen nach", game.NORMAL_TEXT, int(game.WIDTH * 2 / 4), int(game.HEIGHT * 0.62), color=AUSWAHL_TEXT_GREEN, rect_place="oben_mitte")
                return_dict[AFTER_TIME + "1"] = draw_text(game.screen, "Zeit", game.NORMAL_TEXT, int(game.WIDTH * 2 / 4), int(game.HEIGHT * 0.62) + game.NORMAL_TEXT + 5, color=AUSWAHL_TEXT_GREEN, rect_place="oben_mitte")
        elif cursor_pos[0] == 3 and cursor_pos[1] <= int(max([len(MAP_NAMES) - 1, 4]) / 2):
            return_dict[AFTER_TIME + "0"] = draw_text(game.screen, "Gewonnen nach", game.NORMAL_TEXT, int(game.WIDTH * 2 / 4), int(game.HEIGHT * 0.62), color=AUSWAHL_TEXT_SELECTED, rect_place="oben_mitte")
            return_dict[AFTER_TIME + "1"] = draw_text(game.screen, "Zeit", game.NORMAL_TEXT, int(game.WIDTH * 2 / 4), int(game.HEIGHT * 0.62) + game.NORMAL_TEXT + 5, color=AUSWAHL_TEXT_SELECTED, rect_place="oben_mitte")
        else:
            return_dict[AFTER_TIME + "0"] = draw_text(game.screen, "Gewonnen nach", game.NORMAL_TEXT, int(game.WIDTH * 2 / 4), int(game.HEIGHT * 0.62), color=AUSWAHL_TEXT_COLOR, rect_place="oben_mitte")
            return_dict[AFTER_TIME + "1"] = draw_text(game.screen, "Zeit", game.NORMAL_TEXT, int(game.WIDTH * 2 / 4), int(game.HEIGHT * 0.62) + game.NORMAL_TEXT + 5, color=AUSWAHL_TEXT_COLOR, rect_place="oben_mitte")
        if game.genauerer_spielmodus == AFTER_KILLED and not loading:
            if cursor_pos[0] == 3 and cursor_pos[1] > int(max([len(MAP_NAMES) - 1, 4]) / 2):
                return_dict[AFTER_KILLED + "0"] = draw_text(game.screen, "Gewonnen nach", game.NORMAL_TEXT, int(game.WIDTH * 3 / 4), int(game.HEIGHT * 0.62), color=AUSWAHL_TEXT_GREEN_SELECTED, rect_place="oben_mitte")
                return_dict[AFTER_KILLED + "1"] = draw_text(game.screen, "töten aller Zombies", game.NORMAL_TEXT, int(game.WIDTH * 3 / 4), int(game.HEIGHT * 0.62) + game.NORMAL_TEXT + 5, color=AUSWAHL_TEXT_GREEN_SELECTED, rect_place="oben_mitte")
            else:
                return_dict[AFTER_KILLED + "0"] = draw_text(game.screen, "Gewonnen nach", game.NORMAL_TEXT, int(game.WIDTH * 3 / 4), int(game.HEIGHT * 0.62), color=AUSWAHL_TEXT_GREEN, rect_place="oben_mitte")
                return_dict[AFTER_KILLED + "1"] = draw_text(game.screen, "töten aller Zombies", game.NORMAL_TEXT, int(game.WIDTH * 3 / 4), int(game.HEIGHT * 0.62) + game.NORMAL_TEXT + 5, color=AUSWAHL_TEXT_GREEN, rect_place="oben_mitte")
        elif cursor_pos[0] == 3 and cursor_pos[1] > int(max([len(MAP_NAMES) - 1, 4]) / 2):
            return_dict[AFTER_KILLED + "0"] = draw_text(game.screen, "Gewonnen nach", game.NORMAL_TEXT, int(game.WIDTH * 3 / 4), int(game.HEIGHT * 0.62), color=AUSWAHL_TEXT_SELECTED, rect_place="oben_mitte")
            return_dict[AFTER_KILLED + "1"] = draw_text(game.screen, "töten aller Zombies", game.NORMAL_TEXT, int(game.WIDTH * 3 / 4), int(game.HEIGHT * 0.62) + game.NORMAL_TEXT + 5, color=AUSWAHL_TEXT_SELECTED, rect_place="oben_mitte")
        else:
            return_dict[AFTER_KILLED + "0"] = draw_text(game.screen, "Gewonnen nach", game.NORMAL_TEXT, int(game.WIDTH * 3 / 4), int(game.HEIGHT * 0.62), color=AUSWAHL_TEXT_COLOR, rect_place="oben_mitte")
            return_dict[AFTER_KILLED + "1"] = draw_text(game.screen, "töten aller Zombies", game.NORMAL_TEXT, int(game.WIDTH * 3 / 4), int(game.HEIGHT * 0.62) + game.NORMAL_TEXT + 5, color=AUSWAHL_TEXT_COLOR, rect_place="oben_mitte")
    elif game.spielmodus == ARENA_MODUS:
        pygame.draw.line(game.screen, AUSWAHL_TEXT_COLOR, spielmodus_rect.midbottom, (int(game.WIDTH * 1 / 4), int(game.HEIGHT * 0.62)), 3)
        pygame.draw.line(game.screen, AUSWAHL_TEXT_COLOR, spielmodus_rect.midbottom, (int(game.WIDTH * 2 / 4), int(game.HEIGHT * 0.62)), 3)
        if game.genauerer_spielmodus == AFTER_TIME and not loading:
            if cursor_pos[0] == 3 and cursor_pos[1] <= int(max([len(MAP_NAMES) - 1, 4]) / 2):
                return_dict[AFTER_TIME + "0"] = draw_text(game.screen, "Zombiewelle nach", game.NORMAL_TEXT, int(game.WIDTH * 1 / 4), int(game.HEIGHT * 0.62), color=AUSWAHL_TEXT_GREEN_SELECTED, rect_place="oben_mitte")
                return_dict[AFTER_TIME + "1"] = draw_text(game.screen, "Zeit", game.NORMAL_TEXT, int(game.WIDTH * 1 / 4), int(game.HEIGHT * 0.62) + game.NORMAL_TEXT + 5, color=AUSWAHL_TEXT_GREEN_SELECTED, rect_place="oben_mitte")
            else:
                return_dict[AFTER_TIME + "0"] = draw_text(game.screen, "Zombiewelle nach", game.NORMAL_TEXT, int(game.WIDTH * 1 / 4), int(game.HEIGHT * 0.62), color=AUSWAHL_TEXT_GREEN, rect_place="oben_mitte")
                return_dict[AFTER_TIME + "1"] = draw_text(game.screen, "Zeit", game.NORMAL_TEXT, int(game.WIDTH * 1 / 4), int(game.HEIGHT * 0.62) + game.NORMAL_TEXT + 5, color=AUSWAHL_TEXT_GREEN, rect_place="oben_mitte")
        elif cursor_pos[0] == 3 and cursor_pos[1] <= int(max([len(MAP_NAMES) - 1, 4]) / 2):
            return_dict[AFTER_TIME + "0"] = draw_text(game.screen, "Zombiewelle nach", game.NORMAL_TEXT, int(game.WIDTH * 1 / 4), int(game.HEIGHT * 0.62), color=AUSWAHL_TEXT_SELECTED, rect_place="oben_mitte")
            return_dict[AFTER_TIME + "1"] = draw_text(game.screen, "Zeit", game.NORMAL_TEXT, int(game.WIDTH * 1 / 4), int(game.HEIGHT * 0.62) + game.NORMAL_TEXT + 5, color=AUSWAHL_TEXT_SELECTED, rect_place="oben_mitte")
        else:
            return_dict[AFTER_TIME + "0"] = draw_text(game.screen, "Zombiewelle nach", game.NORMAL_TEXT, int(game.WIDTH * 1 / 4), int(game.HEIGHT * 0.62), color=AUSWAHL_TEXT_COLOR, rect_place="oben_mitte")
            return_dict[AFTER_TIME + "1"] = draw_text(game.screen, "Zeit", game.NORMAL_TEXT, int(game.WIDTH * 1 / 4), int(game.HEIGHT * 0.62) + game.NORMAL_TEXT + 5, color=AUSWAHL_TEXT_COLOR, rect_place="oben_mitte")
        if game.genauerer_spielmodus == AFTER_KILLED and not loading:
            if cursor_pos[0] == 3 and cursor_pos[1] > int(max([len(MAP_NAMES) - 1, 4]) / 2):
                return_dict[AFTER_KILLED + "0"] = draw_text(game.screen, "Zombiewelle nach", game.NORMAL_TEXT, int(game.WIDTH * 2 / 4), int(game.HEIGHT * 0.62), color=AUSWAHL_TEXT_GREEN_SELECTED, rect_place="oben_mitte")
                return_dict[AFTER_KILLED + "1"] = draw_text(game.screen, "töten aller Zombies", game.NORMAL_TEXT, int(game.WIDTH * 2 / 4), int(game.HEIGHT * 0.62) + game.NORMAL_TEXT + 5, color=AUSWAHL_TEXT_GREEN_SELECTED, rect_place="oben_mitte")
            else:
                return_dict[AFTER_KILLED + "0"] = draw_text(game.screen, "Zombiewelle nach", game.NORMAL_TEXT, int(game.WIDTH * 2 / 4), int(game.HEIGHT * 0.62), color=AUSWAHL_TEXT_GREEN, rect_place="oben_mitte")
                return_dict[AFTER_KILLED + "1"] = draw_text(game.screen, "töten aller Zombies", game.NORMAL_TEXT, int(game.WIDTH * 2 / 4), int(game.HEIGHT * 0.62) + game.NORMAL_TEXT + 5, color=AUSWAHL_TEXT_GREEN, rect_place="oben_mitte")
        elif cursor_pos[0] == 3 and cursor_pos[1] > int(max([len(MAP_NAMES) - 1, 4]) / 2):
            return_dict[AFTER_KILLED + "0"] = draw_text(game.screen, "Zombiewelle nach", game.NORMAL_TEXT, int(game.WIDTH * 2 / 4), int(game.HEIGHT * 0.62), color=AUSWAHL_TEXT_SELECTED, rect_place="oben_mitte")
            return_dict[AFTER_KILLED + "1"] = draw_text(game.screen, "töten aller Zombies", game.NORMAL_TEXT, int(game.WIDTH * 2 / 4), int(game.HEIGHT * 0.62) + game.NORMAL_TEXT + 5, color=AUSWAHL_TEXT_SELECTED, rect_place="oben_mitte")
        else:
            return_dict[AFTER_KILLED + "0"] = draw_text(game.screen, "Zombiewelle nach", game.NORMAL_TEXT, int(game.WIDTH * 2 / 4), int(game.HEIGHT * 0.62), color=AUSWAHL_TEXT_COLOR, rect_place="oben_mitte")
            return_dict[AFTER_KILLED + "1"] = draw_text(game.screen, "töten aller Zombies", game.NORMAL_TEXT, int(game.WIDTH * 2 / 4), int(game.HEIGHT * 0.62) + game.NORMAL_TEXT + 5, color=AUSWAHL_TEXT_COLOR, rect_place="oben_mitte")

    # Karte
    draw_text(game.screen, "KARTE", int(game.BIG_TEXT * 1.2), int(game.WIDTH / 2), int(game.HEIGHT * 0.74), color=AUSWAHL_TEXT_COLOR)
    for map_count, karten_name in enumerate(MAP_NAMES):
        if game.map_name == karten_name and not loading:
            if cursor_pos[0] == 4 and (cursor_pos[1] == map_count or map_count == len(MAP_NAMES) - 1 and cursor_pos[1] > len(MAP_NAMES) - 1):
                return_dict["Map" + str(map_count)] = draw_text(game.screen, karten_name, game.NORMAL_TEXT, int(game.WIDTH * (map_count + 1) / (len(MAP_NAMES) + 1)), int(game.HEIGHT * 0.84), color=AUSWAHL_TEXT_GREEN_SELECTED, rect_place="mitte")
            else:
                return_dict["Map" + str(map_count)] = draw_text(game.screen, karten_name, game.NORMAL_TEXT, int(game.WIDTH * (map_count + 1) / (len(MAP_NAMES) + 1)), int(game.HEIGHT * 0.84), color=AUSWAHL_TEXT_GREEN, rect_place="mitte")
        elif cursor_pos[0] == 4 and (cursor_pos[1] == map_count or map_count == len(MAP_NAMES) - 1 and cursor_pos[1] > len(MAP_NAMES) - 1):
            return_dict["Map" + str(map_count)] = draw_text(game.screen, karten_name, game.NORMAL_TEXT, int(game.WIDTH * (map_count + 1) / (len(MAP_NAMES) + 1)), int(game.HEIGHT * 0.84), color=AUSWAHL_TEXT_SELECTED, rect_place="mitte")
        else:
            return_dict["Map" + str(map_count)] = draw_text(game.screen, karten_name, game.NORMAL_TEXT, int(game.WIDTH * (map_count + 1) / (len(MAP_NAMES) + 1)), int(game.HEIGHT * 0.84), color=AUSWAHL_TEXT_COLOR, rect_place="mitte")

    if loading:
        draw_text(game.screen, "Lädt ...", game.HUGE_TEXT, int(game.WIDTH / 2), int(game.HEIGHT * 0.94), rect_place="mitte", color=AUSWAHL_TEXT_RED)
    else:
        return_dict["Spielen"] = draw_text(game.screen, "Spielen", game.HUGE_TEXT, int(game.WIDTH / 2), int(game.HEIGHT * 0.94), rect_place="mitte", color=AUSWAHL_TEXT_COLOR)
    pygame.display.flip()

    return return_dict

def make_start_game_selection(game):
    cursor_pos = [1, 0]
    time_last_cursor_change = time()
    while True:
        game.clock.tick(FPS)
        maus_rects = draw_start_game_screen(game,cursor_pos)

        pressed = game.check_key_or_mouse_pressed([pygame.K_SPACE, pygame.K_UP, pygame.K_DOWN, pygame.K_LEFT, pygame.K_RIGHT, pygame.K_s, pygame.K_d])

        if MAUS_LEFT in pressed["Tastatur"]:
            if game.check_maus_pos_on_rect(pressed["Tastatur"][MAUS_LEFT], maus_rects["Hilfe"]):
                make_spielerklaerung(game)

            if game.check_maus_pos_on_rect(pressed["Tastatur"][MAUS_LEFT], maus_rects["Einstellungen"]):
                make_einstellungen(game)

            for schwierigkeitsstufe in range(1, 6):
                if game.check_maus_pos_on_rect(pressed["Tastatur"][MAUS_LEFT], maus_rects["Schwierigkeit_" + str(schwierigkeitsstufe)]):
                    game.schwierigkeit = schwierigkeitsstufe

            if game.check_maus_pos_on_rect(pressed["Tastatur"][MAUS_LEFT], maus_rects[MAP_MODUS]):
                game.spielmodus = MAP_MODUS

            if game.check_maus_pos_on_rect(pressed["Tastatur"][MAUS_LEFT], maus_rects[ARENA_MODUS]):
                game.spielmodus = ARENA_MODUS

            if game.check_maus_pos_on_rect(pressed["Tastatur"][MAUS_LEFT], maus_rects[AFTER_TIME + "0"]) or game.check_maus_pos_on_rect(pressed["Tastatur"][MAUS_LEFT], maus_rects[AFTER_TIME + "1"]):
                game.genauerer_spielmodus = AFTER_TIME

            if game.check_maus_pos_on_rect(pressed["Tastatur"][MAUS_LEFT], maus_rects[AFTER_KILLED + "0"]) or game.check_maus_pos_on_rect(pressed["Tastatur"][MAUS_LEFT], maus_rects[AFTER_KILLED + "1"]):
                game.genauerer_spielmodus = AFTER_KILLED

            for map_count, karten_name in enumerate(MAP_NAMES):
                if game.check_maus_pos_on_rect(pressed["Tastatur"][MAUS_LEFT], maus_rects["Map" + str(map_count)]):
                    game.map_name = karten_name

        if game.check_key_in_pressed(MAUS_ROLL_UP, pressed) and time() - time_last_cursor_change > 0.8:
            time_last_cursor_change = time()
            game.schwierigkeit += 1
            if game.schwierigkeit > 5:
                game.schwierigkeit = 5

        if game.check_key_in_pressed(MAUS_ROLL_DOWN, pressed) and time() - time_last_cursor_change > 0.8:
            time_last_cursor_change = time()
            game.schwierigkeit -= 1
            if game.schwierigkeit < 1:
                game.schwierigkeit = 1

        if game.check_key_in_pressed(pygame.K_UP, pressed) and time() - time_last_cursor_change > 0.8:
            time_last_cursor_change = time()
            cursor_pos[0] = max([cursor_pos[0] - 1, 0])

        if game.check_key_in_pressed(pygame.K_DOWN, pressed) and time() - time_last_cursor_change > 0.8:
            time_last_cursor_change = time()
            cursor_pos[0] = min([cursor_pos[0] + 1, 4])

        if game.check_key_in_pressed(pygame.K_LEFT, pressed) and time() - time_last_cursor_change > 0.8:
            time_last_cursor_change = time()
            if cursor_pos[0] == 0 or cursor_pos[0] == 2 or cursor_pos[0] == 3:
                cursor_pos[1] = 0
            else:
                cursor_pos[1] = max([cursor_pos[1] - 1, 0])

        if game.check_key_in_pressed(pygame.K_RIGHT, pressed) and time() - time_last_cursor_change > 0.8:
            time_last_cursor_change = time()
            if cursor_pos[0] == 0 or cursor_pos[0] == 2 or cursor_pos[0] == 3:
                cursor_pos[1] = max([len(MAP_NAMES) - 1, 4])
            else:
                cursor_pos[1] = min([cursor_pos[1] + 1, max([len(MAP_NAMES) - 1, 4])])

        if game.check_key_in_pressed(pygame.K_s, pressed) or game.check_key_in_pressed(pygame.K_d, pressed) and time() - time_last_cursor_change > 0.8:
            time_last_cursor_change = time()
            if cursor_pos[0] == 0:
                if cursor_pos[1] > int(max([len(MAP_NAMES) - 1, 4]) / 2):
                    make_spielerklaerung(game)
                else:
                    make_einstellungen(game)
            if cursor_pos[0] == 1:
                game.schwierigkeit = min([cursor_pos[1] + 1, 5])
            if cursor_pos[0] == 2:
                if cursor_pos[1] > int(max([len(MAP_NAMES) - 1, 4]) / 2):
                    game.spielmodus = MAP_MODUS
                else:
                    game.spielmodus = ARENA_MODUS
            if cursor_pos[0] == 3:
                if cursor_pos[1] > int(max([len(MAP_NAMES) - 1, 4]) / 2):
                    game.genauerer_spielmodus = AFTER_KILLED
                else:
                    game.genauerer_spielmodus = AFTER_TIME
            if cursor_pos[0] == 4:
                game.map_name = MAP_NAMES[min([cursor_pos[1], len(MAP_NAMES) - 1])]

        if (MAUS_LEFT in pressed["Tastatur"] and game.check_maus_pos_on_rect(pressed["Tastatur"][MAUS_LEFT], maus_rects["Spielen"])) or game.check_key_in_pressed(pygame.K_SPACE, pressed):
            for player_num in range(len(game.players)):
                game.paused[player_num] = False
            game.clock.tick(FPS)
            draw_start_game_screen(game,[-1,-1],True)
            game.check_key_or_mouse_pressed()
            if game.map_name == "Toturial":
                game.spielmodus = TUTORIAL
            break

# Lehrerauswahl
def draw_lehrer_selection(game, surf, selected, player_num, such_text=""):
    return_dict = {}

    if game.multiplayer:
        linker_rand = int(game.WIDTH / len(game.players) * player_num)
        lehrer_asuwahl_breite = int(game.WIDTH / len(game.players))
    else:
        linker_rand = 0
        lehrer_asuwahl_breite = game.WIDTH

    subsurface = game.background.subsurface((linker_rand, 0, int(game.WIDTH / len(game.players)), game.HEIGHT))
    subsurface_rect = subsurface.get_rect()
    surf.blit(subsurface, (subsurface_rect.x + linker_rand, subsurface_rect.y))

    if such_text == "":
        untere_kante_letzter_lehrer = 0
    else:
        draw_text(surf, "Suche: " + such_text, game.BIG_TEXT, linker_rand + 10, 10, rect_place="oben_links", color=AUSWAHL_TEXT_COLOR)
        pygame.draw.line(surf, LEHRER_AUSWAHL_LINE_COLOR, (linker_rand, game.BIG_TEXT + 20), (linker_rand + lehrer_asuwahl_breite, game.BIG_TEXT + 20), 3)
        untere_kante_letzter_lehrer = game.BIG_TEXT + 20

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
        if game.multiplayer:
            for count, player in enumerate(game.players):
                if player.lehrer_name == name and count != player_num:
                    anderer_spieler_hat_schon_diese_person = True
        if LEHRER[name]["bedingungen_fuer_unlock"] != None:
            unlocked = name in game.lehrer_unlocked_sofar
        if such_text != "":
            if not such_text.lower() in name.lower():
                passt_zu_suche = False
        if anderer_spieler_hat_schon_diese_person == False and unlocked == True and passt_zu_suche == True:
            is_there_a_match = True
    if not is_there_a_match:
        draw_text(surf, "kein Suchergebnis", game.BIG_TEXT, linker_rand + 10, untere_kante_letzter_lehrer + 20, rect_place="oben_links", color=AUSWAHL_TEXT_COLOR)
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
            if game.multiplayer:
                for count, player in enumerate(game.players):
                    if player.lehrer_name == lehrer and count != player_num:
                        anderer_spieler_hat_schon_diese_person = True
            if LEHRER[lehrer]["bedingungen_fuer_unlock"] != None:
                unlocked = lehrer in game.lehrer_unlocked_sofar
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

            game.screen.blit(game.lehrer_selection_surfaces[lehrer], (linker_rand, start_hoehe_dieses_lehrer))

            untere_kante_letzter_lehrer = start_hoehe_dieses_lehrer + game.lehrer_selection_surfaces[lehrer].get_height()
            untere_kante_letzter_lehrer += 10
            if untere_kante_letzter_lehrer >= game.HEIGHT:
                break

            return_dict[(start_hoehe_dieses_lehrer, untere_kante_letzter_lehrer)] = lehrer

            # Linie
            pygame.draw.line(surf, LEHRER_AUSWAHL_LINE_COLOR, (linker_rand, untere_kante_letzter_lehrer), (linker_rand + lehrer_asuwahl_breite, untere_kante_letzter_lehrer), 2)

        else:
            break

    pygame.display.flip()

    return return_dict

def make_lehrer_selection(game, surf, player_num):
    draw_lehrer_selection(game,surf, None, player_num)
    alter_lehrer = game.players[player_num].lehrer_name
    selected_lehrer_num = list(LEHRER).index(alter_lehrer)
    draw_lehrer_selection(game,surf, list(LEHRER)[selected_lehrer_num], player_num)
    last_selection_change = time()
    such_text = ""
    while True:
        lehrer_y_positions = draw_lehrer_selection(game, surf, list(LEHRER)[selected_lehrer_num], player_num, such_text)

        pressed = game.check_key_or_mouse_pressed([pygame.K_RETURN, pygame.K_s, pygame.K_d, pygame.K_a, pygame.K_DOWN, pygame.K_UP, pygame.K_BACKSPACE, "text"])

        # Auswahl aendern
        if (game.check_key_in_pressed(pygame.K_UP, pressed) or MAUS_ROLL_UP in pressed["Tastatur"]) and time() - last_selection_change > 0.2 and lehrer_y_positions != []:
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
                if game.multiplayer:
                    for count, player in enumerate(game.players):
                        if player.lehrer_name == LEHRER_NAMEN[selected_lehrer_num] and count != player_num:
                            anderer_spieler_hat_schon_diese_person = True
                if LEHRER[LEHRER_NAMEN[selected_lehrer_num]]["bedingungen_fuer_unlock"] != None:
                    unlocked = LEHRER_NAMEN[selected_lehrer_num] in game.lehrer_unlocked_sofar
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

        if (game.check_key_in_pressed(pygame.K_DOWN, pressed) or MAUS_ROLL_DOWN in pressed["Tastatur"]) and time() - last_selection_change > 0.2 and lehrer_y_positions != []:
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
                if game.multiplayer:
                    for count, player in enumerate(game.players):
                        if player.lehrer_name == LEHRER_NAMEN[selected_lehrer_num] and count != player_num:
                            anderer_spieler_hat_schon_diese_person = True
                if LEHRER[LEHRER_NAMEN[selected_lehrer_num]]["bedingungen_fuer_unlock"] != None:
                    unlocked = LEHRER_NAMEN[selected_lehrer_num] in game.lehrer_unlocked_sofar
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
        if pressed["Tastatur"]["text"] != False:
            such_text += pressed["Tastatur"]["text"]
        if pressed["Tastatur"][pygame.K_BACKSPACE]:
            such_text = such_text[:-2]

        # Auswaehlen
        if MAUS_LEFT in pressed["Tastatur"]:
            for lehrer_y_position in lehrer_y_positions:
                if pressed["Tastatur"][MAUS_LEFT][1] < lehrer_y_position[1] and pressed["Tastatur"][MAUS_LEFT][1] > lehrer_y_position[0]:
                    change_to_other_lehrer(game,lehrer_y_positions[lehrer_y_position], alter_lehrer, game.players[player_num])
                    game.paused[player_num] = False
                    return
        elif game.check_key_in_pressed(pygame.K_s, pressed) or game.check_key_in_pressed(pygame.K_d, pressed):
            change_to_other_lehrer(game,LEHRER_NAMEN[selected_lehrer_num], alter_lehrer, game.players[player_num])
            game.paused[player_num] = False
            return

        # Zurueck
        if game.check_key_in_pressed(pygame.K_a, pressed):
            game.paused[player_num] = False
            return

def change_to_other_lehrer(game, lehrer_name, alter_lehrer, player):
    game.werte_since_last_lehrer_change[player] = {"shoots": 0, "treffer": 0, "collected_objects": 0, "num_obstacles_stept_on": 0, "time_lehrer_change": time(), "zombies_killed": 0, "collected_health_packs": 0, "num_power_ups": 0}
    player.lehrer_name = lehrer_name
    player.weapon_upgrade_unlocked = False
    player.update_image()
    if player.health / LEHRER[alter_lehrer]["player_health"] * LEHRER[player.lehrer_name]["player_health"] > LEHRER[player.lehrer_name]["player_health"]:
        player.health = LEHRER[player.lehrer_name]["player_health"]
    else:
        player.health = player.health / LEHRER[alter_lehrer]["player_health"] * LEHRER[player.lehrer_name]["player_health"]
    for obstacle in game.personen_obstacles:
        obstacle.update_image()
    for object in game.personen_objects:
        object.update_image()
    for zombie in game.zombies:
        zombie.update_image()
    update_live_bar_image(game,player, game.players.index(player))
    update_forground_text_img(game)

# Einstellungen
def draw_einstellungen(game, cursor_pos):
    return_dict = {}

    game.screen.blit(game.background, (0, 0))

    # Einstellungen
    draw_text(game.screen, "Einstellungen", game.GIANT_TEXT, int(game.WIDTH / 2), int(game.HEIGHT * 0.13), rect_place="mitte", color=AUSWAHL_TEXT_COLOR)

    # Schoene oder fluessige Grafik
    if game.schoene_grafik:
        if cursor_pos[0] == 0:
            return_dict["Grafik"] = draw_text(game.screen, "schöne Grafik", game.NORMAL_TEXT, int(game.WIDTH / 2), int(game.HEIGHT * 0.25), rect_place="oben_mitte", color=AUSWAHL_TEXT_SELECTED)
        else:
            return_dict["Grafik"] = draw_text(game.screen, "schöne Grafik", game.NORMAL_TEXT, int(game.WIDTH / 2), int(game.HEIGHT * 0.25), rect_place="oben_mitte", color=AUSWAHL_TEXT_COLOR)
    else:
        if cursor_pos[0] == 0:
            return_dict["Grafik"] = draw_text(game.screen, "flüssige Grafik", game.NORMAL_TEXT, int(game.WIDTH / 2), int(game.HEIGHT * 0.25), rect_place="oben_mitte", color=AUSWAHL_TEXT_SELECTED)
        else:
            return_dict["Grafik"] = draw_text(game.screen, "flüssige Grafik", game.NORMAL_TEXT, int(game.WIDTH / 2), int(game.HEIGHT * 0.25), rect_place="oben_mitte", color=AUSWAHL_TEXT_COLOR)

    # Lautsaerke
    draw_text(game.screen, "Musik             ", game.NORMAL_TEXT, int(game.WIDTH / 4), int(game.HEIGHT * 0.38), rect_place="mitte_rechts", color=AUSWAHL_TEXT_COLOR)
    pygame.draw.line(game.screen, AUSWAHL_TEXT_COLOR, (int(game.WIDTH/4), int(game.HEIGHT*0.38)), (int(game.WIDTH*(3/4)),int(game.HEIGHT*0.38)), 5)
    pygame.draw.circle(game.screen,AUSWAHL_TEXT_GREEN,(int(game.WIDTH/4+(game.WIDTH/2)*game.music_volume),int(game.HEIGHT * 0.38)),10)
    draw_text(game.screen, "Sounds             ", game.NORMAL_TEXT, int(game.WIDTH / 4), int(game.HEIGHT * 0.43), rect_place="mitte_rechts", color=AUSWAHL_TEXT_COLOR)
    pygame.draw.line(game.screen, AUSWAHL_TEXT_COLOR, (int(game.WIDTH/4), int(game.HEIGHT*0.43)), (int(game.WIDTH*(3/4)),int(game.HEIGHT*0.43)), 5)
    pygame.draw.circle(game.screen,AUSWAHL_TEXT_GREEN,(int(game.WIDTH/4+(game.WIDTH/2)*game.sound_volume),int(game.HEIGHT * 0.43)),10)
    if cursor_pos[0] == 1 and cursor_pos[1] == 0:
        return_dict["Musik -"] = draw_text(game.screen, "-    ", game.NORMAL_TEXT, int(game.WIDTH / 4), int(game.HEIGHT * 0.38), rect_place="mitte_rechts", color=AUSWAHL_TEXT_SELECTED)
    else:
        return_dict["Musik -"] = draw_text(game.screen, "-    ", game.NORMAL_TEXT, int(game.WIDTH / 4), int(game.HEIGHT * 0.38), rect_place="mitte_rechts", color=AUSWAHL_TEXT_COLOR)
    if cursor_pos[0] == 1 and cursor_pos[1] == 1:
        return_dict["Musik +"] = draw_text(game.screen, "    +", game.NORMAL_TEXT, int(game.WIDTH*(3/4)), int(game.HEIGHT * 0.38), rect_place="mitte_links", color=AUSWAHL_TEXT_SELECTED)
    else:
        return_dict["Musik +"] = draw_text(game.screen, "    +", game.NORMAL_TEXT, int(game.WIDTH*(3/4)), int(game.HEIGHT * 0.38), rect_place="mitte_links", color=AUSWAHL_TEXT_COLOR)

    if cursor_pos[0] == 2 and cursor_pos[1] == 0:
        return_dict["Sounds -"] = draw_text(game.screen, "-    ", game.NORMAL_TEXT, int(game.WIDTH / 4), int(game.HEIGHT * 0.43), rect_place="mitte_rechts", color=AUSWAHL_TEXT_SELECTED)
    else:
        return_dict["Sounds -"] = draw_text(game.screen, "-    ", game.NORMAL_TEXT, int(game.WIDTH / 4), int(game.HEIGHT * 0.43), rect_place="mitte_rechts", color=AUSWAHL_TEXT_COLOR)
    if cursor_pos[0] == 2 and cursor_pos[1] == 1:
        return_dict["Sounds +"] = draw_text(game.screen, "    +", game.NORMAL_TEXT, int(game.WIDTH*(3/4)), int(game.HEIGHT * 0.43), rect_place="mitte_links", color=AUSWAHL_TEXT_SELECTED)
    else:
        return_dict["Sounds +"] = draw_text(game.screen, "    +", game.NORMAL_TEXT, int(game.WIDTH*(3/4)), int(game.HEIGHT * 0.43), rect_place="mitte_links", color=AUSWAHL_TEXT_COLOR)

    # Tastatur und Maus
    if game.use_tastatur and len(game.all_joysticks) > 0:
        if cursor_pos[0] == 3 and cursor_pos[1] == 0:
            return_dict["Tastatur"] = draw_text(game.screen, "Tastatur ", game.NORMAL_TEXT, int(game.WIDTH / 2), int(game.HEIGHT * 0.55), rect_place="oben_rechts", color=AUSWAHL_TEXT_GREEN_SELECTED)
        else:
            return_dict["Tastatur"] = draw_text(game.screen, "Tastatur ", game.NORMAL_TEXT, int(game.WIDTH / 2), int(game.HEIGHT * 0.55), rect_place="oben_rechts", color=AUSWAHL_TEXT_GREEN)
    else:
        if cursor_pos[0] == 3 and cursor_pos[1] == 0 and len(game.all_joysticks) > 0:
            return_dict["Tastatur"] = draw_text(game.screen, "Tastatur ", game.NORMAL_TEXT, int(game.WIDTH / 2), int(game.HEIGHT * 0.55), rect_place="oben_rechts", color=AUSWAHL_TEXT_SELECTED)
        else:
            return_dict["Tastatur"] = draw_text(game.screen, "Tastatur ", game.NORMAL_TEXT, int(game.WIDTH / 2), int(game.HEIGHT * 0.55), rect_place="oben_rechts", color=AUSWAHL_TEXT_COLOR)
    if game.with_maussteuerung:
        if cursor_pos[0] == 3 and (cursor_pos[1] == 1 or len(game.all_joysticks) == 0):
            return_dict["Maus"] = draw_text(game.screen, "  Maussteuerung", game.NORMAL_TEXT, int(game.WIDTH / 2), int(game.HEIGHT * 0.55), rect_place="oben_links", color=AUSWAHL_TEXT_SELECTED)
        else:
            return_dict["Maus"] = draw_text(game.screen, "  Maussteuerung", game.NORMAL_TEXT, int(game.WIDTH / 2), int(game.HEIGHT * 0.55), rect_place="oben_links", color=AUSWAHL_TEXT_COLOR)
    else:
        if cursor_pos[0] == 3 and (cursor_pos[1] == 1 or len(game.all_joysticks) == 0):
            return_dict["Maus"] = draw_text(game.screen, "  Tastatursteuerung", game.NORMAL_TEXT, int(game.WIDTH / 2), int(game.HEIGHT * 0.55), rect_place="oben_links", color=AUSWAHL_TEXT_SELECTED)
        else:
            return_dict["Maus"] = draw_text(game.screen, "  Tastatursteuerung", game.NORMAL_TEXT, int(game.WIDTH / 2), int(game.HEIGHT * 0.55), rect_place="oben_links", color=AUSWAHL_TEXT_COLOR)

    # Joysticks
    return_dict["Joystick"] = []
    for count, joystick in enumerate(game.all_joysticks):
        if joystick in game.used_joysticks:
            if cursor_pos[0] - 4 == count:
                return_dict["Joystick"].append(draw_text(game.screen, joystick.get_name(), game.NORMAL_TEXT, int(game.WIDTH / 2), int(game.HEIGHT * 0.55 + (count + 1) * (game.NORMAL_TEXT + 12)), rect_place="oben_mitte", color=AUSWAHL_TEXT_GREEN_SELECTED))
            else:
                return_dict["Joystick"].append(draw_text(game.screen, joystick.get_name(), game.NORMAL_TEXT, int(game.WIDTH / 2), int(game.HEIGHT * 0.55 + (count + 1) * (game.NORMAL_TEXT + 12)), rect_place="oben_mitte", color=AUSWAHL_TEXT_GREEN))
        elif cursor_pos[0] - 4 == count:
            return_dict["Joystick"].append(draw_text(game.screen, joystick.get_name(), game.NORMAL_TEXT, int(game.WIDTH / 2), int(game.HEIGHT * 0.55 + (count + 1) * (game.NORMAL_TEXT + 12)), rect_place="oben_mitte", color=AUSWAHL_TEXT_SELECTED))
        else:
            return_dict["Joystick"].append(draw_text(game.screen, joystick.get_name(), game.NORMAL_TEXT, int(game.WIDTH / 2), int(game.HEIGHT * 0.55 + (count + 1) * (game.NORMAL_TEXT + 12)), rect_place="oben_mitte", color=AUSWAHL_TEXT_COLOR))

    # Fentergroesse anpassen
    if cursor_pos[0] == len(game.all_joysticks) + 4:
        return_dict["Fenstergroesse"] = draw_text(game.screen, "Fenstergröße an Anzahl der Spieler anpassen", game.NORMAL_TEXT, int(game.WIDTH / 2), int(game.HEIGHT - 2 * game.NORMAL_TEXT - 20), rect_place="unten_mitte", color=AUSWAHL_TEXT_SELECTED)
    else:
        return_dict["Fenstergroesse"] = draw_text(game.screen, "Fenstergröße an Anzahl der Spieler anpassen", game.NORMAL_TEXT, int(game.WIDTH / 2), int(game.HEIGHT - 2 * game.NORMAL_TEXT - 20), rect_place="unten_mitte", color=AUSWAHL_TEXT_COLOR)

    # zurueck
    return_dict["zurueck"] = draw_text(game.screen, "zurück", game.NORMAL_TEXT, int(game.WIDTH / 2), int(game.HEIGHT - game.NORMAL_TEXT), rect_place="unten_mitte", color=AUSWAHL_TEXT_COLOR)

    pygame.display.flip()

    return return_dict

def make_einstellungen(game):
    def change_sound_volume(volume):
        for sound_name in WEAPON_WAVS:
            WEAPON_WAVS[sound_name].set_volume(volume)
        LEVEL_START_WAV.set_volume(volume)
        for sound in ZOMBIE_WAVS:
            sound.set_volume(volume)
        for sound in ZOMBIE_HIT_WAVS:
            sound.set_volume(volume)
        for sound in PLAYER_HIT_WAVS:
            sound.set_volume(volume)
    cursor_pos = [0, 0]
    time_last_cursor_change = time()
    while True:
        game.clock.tick(FPS)
        maus_rects = draw_einstellungen(game,cursor_pos)

        pressed = game.check_key_or_mouse_pressed([pygame.K_LEFT, pygame.K_RIGHT, pygame.K_UP, pygame.K_DOWN, pygame.K_RETURN, pygame.K_a, pygame.K_s, pygame.K_d])

        if MAUS_LEFT in pressed["Tastatur"]:
            if game.check_maus_pos_on_rect(pressed["Tastatur"][MAUS_LEFT], maus_rects["Grafik"]):
                if game.schoene_grafik:
                    game.schoene_grafik = False
                else:
                    game.schoene_grafik = True

            if game.check_maus_pos_on_rect(pressed["Tastatur"][MAUS_LEFT], maus_rects["Musik +"]):
                game.music_volume = round(min([game.music_volume + 0.1, 1]), 1)
                pygame.mixer.music.set_volume(game.music_volume)
            if game.check_maus_pos_on_rect(pressed["Tastatur"][MAUS_LEFT], maus_rects["Musik -"]):
                game.music_volume = round(max([game.music_volume - 0.1, 0]), 1)
                pygame.mixer.music.set_volume(game.music_volume)
            if game.check_maus_pos_on_rect(pressed["Tastatur"][MAUS_LEFT], maus_rects["Sounds +"]):
                game.sound_volume = round(min([game.sound_volume + 0.1, 1]), 1)
                change_sound_volume(game.sound_volume)
            if game.check_maus_pos_on_rect(pressed["Tastatur"][MAUS_LEFT], maus_rects["Sounds -"]):
                game.sound_volume = round(max([game.sound_volume - 0.1, 0]), 1)
                change_sound_volume(game.sound_volume)
            if game.check_maus_pos_on_rect(pressed["Tastatur"][MAUS_LEFT], maus_rects["Tastatur"]):
                if game.use_tastatur and len(game.all_joysticks) > 0:
                    game.use_tastatur = False
                else:
                    game.use_tastatur = True

            if game.check_maus_pos_on_rect(pressed["Tastatur"][MAUS_LEFT], maus_rects["Maus"]):
                if game.with_maussteuerung:
                    game.with_maussteuerung = False
                else:
                    game.with_maussteuerung = True

            for count, joystick in enumerate(maus_rects["Joystick"]):
                if game.check_maus_pos_on_rect(pressed["Tastatur"][MAUS_LEFT], joystick):
                    if game.all_joysticks[count] in game.used_joysticks:
                        del game.used_joysticks[game.used_joysticks.index(game.all_joysticks[count])]
                    else:
                        game.used_joysticks.append(game.all_joysticks[count])

            if game.check_maus_pos_on_rect(pressed["Tastatur"][MAUS_LEFT], maus_rects["Fenstergroesse"]):
                anz_players = len(game.used_joysticks)
                if game.use_tastatur:
                    anz_players += 1
                if anz_players >= 1:
                    game.window_resize(anz_players * 960, 640)

            if game.check_maus_pos_on_rect(pressed["Tastatur"][MAUS_LEFT], maus_rects["zurueck"]):
                if game.use_tastatur or len(game.used_joysticks) >= 1:
                    anz_players = len(game.used_joysticks)
                    if game.use_tastatur:
                        anz_players += 1
                    if anz_players > 1:
                        game.multiplayer = True
                        game.num_players_in_multiplayer = anz_players
                    else:
                        game.multiplayer = False
                    break

        if game.check_key_in_pressed(pygame.K_UP, pressed) and time() - time_last_cursor_change > 0.4:
            time_last_cursor_change = time()
            cursor_pos[0] = max([cursor_pos[0] - 1, 0])

        if game.check_key_in_pressed(pygame.K_DOWN, pressed) and time() - time_last_cursor_change > 0.4:
            time_last_cursor_change = time()
            cursor_pos[0] = min([cursor_pos[0] + 1, len(game.all_joysticks) + 4])

        if game.check_key_in_pressed(pygame.K_LEFT, pressed) and time() - time_last_cursor_change > 0.4:
            time_last_cursor_change = time()
            cursor_pos[1] = max([cursor_pos[1] - 1, 0])

        if game.check_key_in_pressed(pygame.K_RIGHT, pressed) and time() - time_last_cursor_change > 0.4:
            time_last_cursor_change = time()
            cursor_pos[1] = min([cursor_pos[1] + 1, 1])

        if (game.check_key_in_pressed(pygame.K_s, pressed) or game.check_key_in_pressed(pygame.K_d, pressed)) and time() - time_last_cursor_change > 0.4:
            time_last_cursor_change = time()
            if cursor_pos[0] == 0:
                if game.schoene_grafik:
                    game.schoene_grafik = False
                else:
                    game.schoene_grafik = True
            elif cursor_pos[0] == 1:
                if cursor_pos[1] == 0:
                    game.music_volume = round(max([game.music_volume - 0.1,0]),1)
                else:
                    game.music_volume = round(min([game.music_volume + 0.1, 1]),1)
                pygame.mixer.music.set_volume(game.music_volume)
            elif cursor_pos[0] == 2:
                if cursor_pos[1] == 0:
                    game.sound_volume = round(max([game.sound_volume - 0.1, 0]), 1)
                else:
                    game.sound_volume = round(min([game.sound_volume + 0.1, 1]), 1)
                change_sound_volume(game.sound_volume)
            elif cursor_pos[0] == 3:
                if cursor_pos[1] == 0 and len(game.all_joysticks) > 0:
                    if game.use_tastatur:
                        game.use_tastatur = False
                    else:
                        game.use_tastatur = True
                if cursor_pos[1] == 1 or len(game.all_joysticks) == 0:
                    if game.with_maussteuerung:
                        game.with_maussteuerung = False
                    else:
                        game.with_maussteuerung = True
            elif cursor_pos[0] == len(game.all_joysticks) + 4:
                anz_players = len(game.used_joysticks)
                if game.use_tastatur:
                    anz_players += 1
                if 1 <= anz_players <= 4:
                    if game.WIDTH != [960, 1300, 2200, 3500, 4000][anz_players - 1] or game.HEIGHT != 640:
                        game.window_resize([960, 1500, 2800, 4500, 7000][anz_players - 1], 640)
            else:
                if game.all_joysticks[cursor_pos[0] - 4] in game.used_joysticks:
                    del game.used_joysticks[game.used_joysticks.index(game.all_joysticks[cursor_pos[0] - 4])]
                else:
                    game.used_joysticks.append(game.all_joysticks[cursor_pos[0] - 4])

        if game.check_key_in_pressed(pygame.K_RETURN, pressed) or game.check_key_in_pressed(pygame.K_a, pressed):
            if game.use_tastatur or len(game.used_joysticks) >= 1:
                anz_players = len(game.used_joysticks)
                if game.use_tastatur:
                    anz_players += 1
                if anz_players > 1:
                    game.multiplayer = True
                    game.num_players_in_multiplayer = anz_players
                else:
                    game.multiplayer = False
                break

# Spielerklaerung
def make_spielerklaerung(game):

    while True:
        game.screen.blit(game.background, (0, 0))
        orig_width = ERKLAERUNG.get_width()
        orig_height = ERKLAERUNG.get_height()
        width = int(game.WIDTH)
        if orig_width / width < orig_height / game.HEIGHT:
            height = int(game.HEIGHT)
            width = int(orig_width * (game.HEIGHT / orig_height))
            pos = (int((game.WIDTH - width) / 2), 0)
            game.screen.blit(pygame.transform.scale(ERKLAERUNG, (width, height)), pos)
        else:
            height = int(orig_height * (width / orig_width))
            pos = (0, int((game.HEIGHT - height) / 2))
            game.screen.blit(pygame.transform.scale(ERKLAERUNG, (width, height)), pos)
        pygame.display.flip()

        game.clock.tick(FPS)
        pressed = game.check_key_or_mouse_pressed([pygame.K_RETURN, pygame.K_a])

        if game.check_key_in_pressed(pygame.K_RETURN, pressed) or game.check_key_in_pressed(pygame.K_a, pressed):
            break
        if MAUS_LEFT in pressed["Tastatur"]:
            if game.check_maus_pos_on_rect(pressed["Tastatur"][MAUS_LEFT], pygame.Rect((int(pos[0] + (width / 2) - (0.3 * width)), int(pos[1] + height - 0.3 * height)), (int(0.6 * width), int(0.6 * height)))):
                break
        for joystick in game.all_joysticks:
            if joystick.get_A() or joystick.get_Y() or joystick.get_select() or joystick.get_start() or joystick.get_shoulder_left() or joystick.get_shoulder_right() or joystick.get_axis_left() or joystick.get_axis_right():
                break