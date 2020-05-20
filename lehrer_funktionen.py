# Diese Funktioen werden aufgerufen, wenn das entsprechende Eregniss im Spiel passiert.
# Sollte beim hinzufuegen eines neuen Lehrers vergessen werden die Funktionen in dieser Datei hinzuzufuegen werden sie in constants.py automatisch erstellt
from constants import *


def is_zombie_close_to_player(zombie, player_pos, area_radius=250):
    if zombie.pos.x < player_pos.x + area_radius and zombie.pos.x > player_pos.x - area_radius and zombie.pos.y < player_pos.y + area_radius and zombie.pos.y > player_pos.y - area_radius:
        return True


def power_up_nomagic(game, player, test=False):
    if not test:
        for zombie in game.zombies:
            if is_zombie_close_to_player(zombie, player.pos):
                zombie.change_img_for_given_time(LEHRER["nomagic"]["other_files"]["frozen_zombie"], 3000, stand_still_during_time=True)


def object_collect_nomagic(game, player, test=False):
    if not test:
        if player.weapon_upgrade_unlocked:
            player.change_img_for_given_time(LEHRER["nomagic"]["other_files"]["big_eyes_schwamm"], 2200)
        else:
            player.change_img_for_given_time(LEHRER["nomagic"]["other_files"]["big_eyes"], 2000)


def obstacle_nomagic(game, player, test=False):
    if not test:
        player.place_img_on_player_for_given_time(LEHRER["nomagic"]["other_files"]["aua"], 1500, 30, 0)


def health_pack_nomagic(game, player, test=False):
    if not test:
        pass


def power_up_ecoltes(game, player, test=False):
    if not test:
        for zombie in game.zombies:
            if is_zombie_close_to_player(zombie, player.pos):
                zombie.change_img_for_given_time(LEHRER["ecoltes"]["other_files"]["zombie_ohren_zu"], 3000, damge_during_time=MOB_HEALTH * 3 / 4)
                zombie.place_img_on_zombie_for_given_time(LEHRER["ecoltes"]["other_files"]["aua"], 3000, 20, -5)
        player.place_img_on_player_for_given_time(LEHRER["ecoltes"]["other_files"]["bonjour"], 3000, 20, -10)


def object_collect_ecoltes(game, player, test=False):
    if not test:
        if player.weapon_upgrade_unlocked:
            player.change_img_for_given_time(LEHRER["ecoltes"]["other_files"]["player_pfandflasche_marmelade"], 2000)
        else:
            player.change_img_for_given_time(LEHRER["ecoltes"]["other_files"]["player_pfandflasche"], 2000)


def obstacle_ecoltes(game, player, test=False):
    if not test:
        player.place_img_on_player_for_given_time(LEHRER["ecoltes"]["other_files"]["zut"], 1500, 30, 0)


def health_pack_ecoltes(game, player, test=False):
    if not test:
        pass


def power_up_gnatrium(game, player, test=False):
    if not test:
        for zombie in game.zombies:
            if is_zombie_close_to_player(zombie, player.pos):
                zombie.change_img_for_given_time(LEHRER["gnatrium"]["other_files"]["blumen_zombie"], 3000, damge_during_time=MOB_HEALTH * 2 / 3)
        Gas_Wolke(game, LEHRER["gnatrium"]["other_files"]["gaswolke"], (50, 50), (500, 500), player.pos, 1000, 2000)


def object_collect_gnatrium(game, player, test=False):
    if not test:
        player.place_img_on_player_for_given_time(PEROSNEN_OBJECT_IMGES["gnatrium"]["img"], 1500, 30, -20)


def obstacle_gnatrium(game, player, test=False):
    if not test:
        player.place_img_on_player_for_given_time(LEHRER["gnatrium"]["other_files"]["aua"], 1500, 30, 0)


def health_pack_gnatrium(game, player, test=False):
    if not test:
        pass


def power_up_windmauer(game, player, test=False):
    if not test:
        for zombie in game.zombies:
            if is_zombie_close_to_player(zombie, player.pos):
                zombie.change_img_for_given_time(None, 3000, stand_still_during_time=True)
                zombie.place_img_on_zombie_for_given_time(LEHRER["windmauer"]["other_files"]["zzz"], 3000, 30, -30)
        player.place_img_on_player_for_given_time(LEHRER["windmauer"]["other_files"]["bla bla bla"], 2000, 30, -10)


def object_collect_windmauer(game, player, test=False):
    if not test:
        player.place_img_on_player_for_given_time(LEHRER["windmauer"]["other_files"]["abikorrektur"], 1500, 30, -10)


def obstacle_windmauer(game, player, test=False):
    if not test:
        player.place_img_on_player_for_given_time(LEHRER["windmauer"]["other_files"]["kommatest"], 1500, 30, -10)


def health_pack_windmauer(game, player, test=False):
    if not test:
        pass


def power_up_honyoung(game, player, test=False):
    if not test:
        player.place_img_on_player_for_given_time(LEHRER["honyoung"]["other_files"]["be quiet"], 2500, 30, 0)
        for zombie in game.zombies:
            if is_zombie_close_to_player(zombie, player.pos):
                zombie.change_img_for_given_time(None, 4000, stand_still_during_time=True)


def object_collect_honyoung(game, player, test=False):
    if not test:
        player.place_img_on_player_for_given_time(LEHRER["honyoung"]["other_files"]["I love that sentence"], 1500, 30, 0)


def obstacle_honyoung(game, player, test=False):
    if not test:
        player.place_img_on_player_for_given_time(LEHRER["honyoung"]["other_files"]["fisch"], 1500, 30, 0)


def health_pack_honyoung(game, player, test=False):
    if not test:
        pass


def power_up_wolkenstaedtle(game, player, test=False):
    if not test:
        player.change_img_for_given_time(image=LEHRER["wolkenstaedtle"]["other_files"]["Pferd"], time_in_millis=3500)
        nahe_zombies = []
        for zombie in game.zombies:
            if is_zombie_close_to_player(zombie, player.pos):
                nahe_zombies.append(zombie)
        for number, zombie in enumerate(nahe_zombies):
            zombie.place_img_on_zombie_for_given_time([LEHRER["wolkenstaedtle"]["other_files"]["Name?"], LEHRER["wolkenstaedtle"]["other_files"]["Lenard?"]][number % 2], 3250, 30, 5)
            zombie.change_img_for_given_time(None, 3500, stand_still_during_time=True)


def object_collect_wolkenstaedtle(game, player, test=False):
    if not test:
        player.change_img_for_given_time(image=LEHRER["wolkenstaedtle"]["other_files"]["sitzen"], time_in_millis=2500)


def obstacle_wolkenstaedtle(game, player, test=False):
    if not test:
        pass


def health_pack_wolkenstaedtle(game, player, test=False):
    if not test:
        pass


def power_up_tomathely(game, player, test=False):
    if not test:
        player.place_img_on_player_for_given_time(LEHRER["tomathely"]["other_files"]["noch nicht abschreiben"], 3250, 30, -20)
        for zombie in game.zombies:
            if is_zombie_close_to_player(zombie, player.pos):
                zombie.change_img_for_given_time(None, 3500, stand_still_during_time=True)


def object_collect_tomathely(game, player, test=False):
    if not test:
        player.place_img_on_player_for_given_time(LEHRER["tomathely"]["other_files"]["Michel"], 1500, 30, 0)


def obstacle_tomathely(game, player, test=False):
    if not test:
        player.place_img_on_player_for_given_time(LEHRER["tomathely"]["other_files"]["umstellen"], 3250, 30, -5)


def health_pack_tomathely(game, player, test=False):
    if not test:
        pass


def power_up_gruss(game, player, test=False):
    if not test:
        player.place_img_on_player_for_given_time(LEHRER["gruss"]["other_files"]["Das haengt von der Definition ab"], 4250, 30, -50)
        first = True
        for zombie in game.zombies:
            if is_zombie_close_to_player(zombie, player.pos):
                zombie.change_img_for_given_time(LEHRER["gruss"]["other_files"]["anderer_zombie"], 4000, damge_during_time=MOB_HEALTH * 1 / 2)
                if first:
                    zombie.place_img_on_zombie_for_given_time(LEHRER["gruss"]["other_files"]["sind wir zombies"], 4000, 30, -30)
                    first = False


def object_collect_gruss(game, player, test=False):
    if not test:
        player.place_img_on_player_for_given_time(LEHRER["gruss"]["other_files"]["bewiesen"], 1500, 35, -25)


def obstacle_gruss(game, player, test=False):
    if not test:
        player.place_img_on_player_for_given_time(LEHRER["gruss"]["other_files"]["warum laedt des nicht"], 1500, 40, -35)


def health_pack_gruss(game, player, test=False):
    if not test:
        pass


def power_up_hozler(game, player, test=False):
    if not test:
        for zombie in game.zombies:
            if is_zombie_close_to_player(zombie, player.pos):
                zombie.change_img_for_given_time(None, 3000, stand_still_during_time=True,
                                                 damge_during_time=MOB_HEALTH / 2)
        Shaking_object(game, PERSONEN_POWER_UP_ICONS["hozler"], player.pos, 3000)


def object_collect_hozler(game, player, test=False):
    if not test:
        player.health += 15
        if player.health > LEHRER["hozler"]["player_health"]:
            player.health = LEHRER["hozler"]["player_health"]


def obstacle_hozler(game, player, test=False):
    if not test:
        pass


def health_pack_hozler(game, player, test=False):
    if not test:
        pass


def power_up_schueler(game, player, test=False):
    if not test:
        for zombie in game.zombies:
            if is_zombie_close_to_player(zombie, player.pos):
                zombie.change_img_for_given_time(None, 3000, stand_still_during_time=True, damge_during_time=MOB_HEALTH * 2 / 3)
        Shaking_object(game, PERSONEN_POWER_UP_ICONS["schueler"], player.pos, 3000)


def object_collect_schueler(game, player, test=False):
    if not test:
        Spielhack(game, player)


def obstacle_schueler(game, player, test=False):
    if not test:
        player.place_img_on_player_for_given_time(LEHRER["schueler"]["other_files"]["unnoetig"], 1500, 30, 0)


def health_pack_schueler(game, player, test=False):
    if not test:
        pass
