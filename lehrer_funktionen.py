# Diese Funktioen werden aufgerufen, wenn das entsprechende Eregniss im Spiel passiert.
# Sollte beim hinzufügen eines neuen Lehrers vergessen werden die Funktionen in dieser Datei hinzuzufügen werden sie in constants.py automatisch erstellt
from constants import *
from sprites import *

def is_zombie_close_to_player(zombie, player_pos, area_radius=250):
    if zombie.pos.x < player_pos.x + area_radius and zombie.pos.x > player_pos.x - area_radius and zombie.pos.y < player_pos.y + area_radius and zombie.pos.y > player_pos.y - area_radius:
        return True

def power_up_No_Magic(game, player, test=False):
    if not test:
        for zombie in game.zombies:
            if is_zombie_close_to_player(zombie, player.pos):
                zombie.change_img_for_given_time(LEHRER["No Magic"]["other_files"]["frozen_zombie"],3000,stand_still_during_time=True)

def object_collect_No_Magic(game, player, test = False):
    if not test:
        if player.weapon_upgrade_unlocked:
            player.change_img_for_given_time(LEHRER["No Magic"]["other_files"]["big_eyes_schwamm"],2200)
        else:
            player.change_img_for_given_time(LEHRER["No Magic"]["other_files"]["big_eyes"],2000)

def obstacle_No_Magic(game, player, test = False):
    if not test:
        player.place_img_on_player_for_given_time(LEHRER["No Magic"]["other_files"]["aua"], 1500, 30, 0)

def health_pack_No_Magic(game, player, test = False):
    if not test:
        pass

def power_up_Écoltes(game, player, test = False):
    if not test:
        for zombie in game.zombies:
            if is_zombie_close_to_player(zombie, player.pos):
                zombie.change_img_for_given_time(LEHRER["Écoltes"]["other_files"]["zombie_ohren_zu"],3000,damge_during_time=MOB_HEALTH*3/4)
                zombie.place_img_on_zombie_for_given_time(LEHRER["Écoltes"]["other_files"]["aua"], 3000, 20, -5)
        player.place_img_on_player_for_given_time(LEHRER["Écoltes"]["other_files"]["bonjour"],3000,20,-10)

def object_collect_Écoltes(game, player, test = False):
    if not test:
        if player.weapon_upgrade_unlocked:
            player.change_img_for_given_time(LEHRER["Écoltes"]["other_files"]["player_pfandflasche_marmelade"], 2000)
        else:
            player.change_img_for_given_time(LEHRER["Écoltes"]["other_files"]["player_pfandflasche"], 2000)

def obstacle_Écoltes(game, player, test = False):
    if not test:
        player.place_img_on_player_for_given_time(LEHRER["Écoltes"]["other_files"]["zut"], 1500, 30, 0)

def health_pack_Écoltes(game, player, test = False):
    if not test:
        pass

def power_up_Gnatrium(game, player, test = False):
    if not test:
        for zombie in game.zombies:
            if is_zombie_close_to_player(zombie, player.pos):
                zombie.change_img_for_given_time(LEHRER["Gnatrium"]["other_files"]["blumen_zombie"],3000,damge_during_time=MOB_HEALTH*2/3)
        Gas_Wolke(game,LEHRER["Gnatrium"]["other_files"]["gaswolke"],(50,50),(500,500),player.pos,1000,2000)

def object_collect_Gnatrium(game, player, test = False):
    if not test:
        player.place_img_on_player_for_given_time(PEROSNEN_OBJECT_IMGES["Gnatrium"]["img"], 1500, 30, -20)

def obstacle_Gnatrium(game, player, test = False):
    if not test:
        player.place_img_on_player_for_given_time(LEHRER["Gnatrium"]["other_files"]["aua"], 1500, 30, 0)

def health_pack_Gnatrium(game, player, test = False):
    if not test:
        pass

def power_up_Windmauer(game, player, test = False):
    if not test:
        for zombie in game.zombies:
            if is_zombie_close_to_player(zombie, player.pos):
                zombie.change_img_for_given_time(None,3000,stand_still_during_time=True)
                zombie.place_img_on_zombie_for_given_time(LEHRER["Windmauer"]["other_files"]["zzz"],3000,30,-30)
        player.place_img_on_player_for_given_time(LEHRER["Windmauer"]["other_files"]["bla bla bla"], 2000, 30, -10)

def object_collect_Windmauer(game, player, test = False):
    if not test:
        player.place_img_on_player_for_given_time(LEHRER["Windmauer"]["other_files"]["abikorrektur"], 1500, 30, -10)

def obstacle_Windmauer(game, player, test = False):
    if not test:
        player.place_img_on_player_for_given_time(LEHRER["Windmauer"]["other_files"]["kommatest"], 1500, 30, -10)

def health_pack_Windmauer(game, player, test = False):
    if not test:
        pass

def power_up_Hoyoung(game, player, test = False):
    if not test:
        player.place_img_on_player_for_given_time(LEHRER["Hoyoung"]["other_files"]["be quiet"], 2500, 30, 0)
        for zombie in game.zombies:
            if is_zombie_close_to_player(zombie, player.pos):
                zombie.change_img_for_given_time(None,4000,stand_still_during_time=True)

def object_collect_Hoyoung(game, player, test = False):
    if not test:
        player.place_img_on_player_for_given_time(LEHRER["Hoyoung"]["other_files"]["I love that sentence"], 1500, 30, 0)

def obstacle_Hoyoung(game, player, test = False):
    if not test:
        player.place_img_on_player_for_given_time(LEHRER["Hoyoung"]["other_files"]["fisch"], 1500, 30, 0)

def health_pack_Hoyoung(game, player, test = False):
    if not test:
        pass

def power_up_Wolkenstädle(game, player, test = False):
    if not test:
        player.change_img_for_given_time(image=LEHRER["Wolkenstädle"]["other_files"]["Pferd"],time_in_millis=3500)
        nahe_zombies = []
        for zombie in game.zombies:
            if is_zombie_close_to_player(zombie, player.pos):
                nahe_zombies.append(zombie)
        for number,zombie in enumerate(nahe_zombies):
            zombie.place_img_on_zombie_for_given_time([LEHRER["Wolkenstädle"]["other_files"]["Name?"],LEHRER["Wolkenstädle"]["other_files"]["Lenard?"]][number%2],3250,30,5)
            zombie.change_img_for_given_time(None,3500,stand_still_during_time=True)

def object_collect_Wolkenstädle(game, player, test = False):
    if not test:
        player.change_img_for_given_time(image=LEHRER["Wolkenstädle"]["other_files"]["sitzen"], time_in_millis=2500)

def obstacle_Wolkenstädle(game, player, test = False):
    if not test:
        pass

def health_pack_Wolkenstädle(game, player, test = False):
    if not test:
        pass

def power_up_To_Mathely(game, player, test = False):
    if not test:
        player.place_img_on_player_for_given_time(LEHRER["To Mathely"]["other_files"]["noch nicht abschreiben"], 3250, 30, -20)
        for zombie in game.zombies:
            if is_zombie_close_to_player(zombie, player.pos):
                zombie.change_img_for_given_time(None,3500,stand_still_during_time=True)

def object_collect_To_Mathely(game, player, test = False):
    if not test:
        player.place_img_on_player_for_given_time(LEHRER["To Mathely"]["other_files"]["Michel"], 1500, 30, 0)

def obstacle_To_Mathely(game, player, test = False):
    if not test:
        player.place_img_on_player_for_given_time(LEHRER["To Mathely"]["other_files"]["umstellen"], 3250, 30, -5)

def health_pack_To_Mathely(game, player, test = False):
    if not test:
        pass

def power_up_Hozler(game, player, test = False):
    if not test:
        for zombie in game.zombies:
            if is_zombie_close_to_player(zombie, player.pos):
                zombie.change_img_for_given_time(None, 3000, stand_still_during_time=True,
                                                 damge_during_time=MOB_HEALTH/2)
        Shaking_object(game, PERSONEN_POWER_UP_ICONS["Hozler"], player.pos, 3000)

def object_collect_Hozler(game, player, test = False):
    if not test:
        player.health += 15
        if player.health > LEHRER["Hozler"]["player_health"]:
            player.health = LEHRER["Hozler"]["player_health"]

def obstacle_Hozler(game, player, test = False):
    if not test:
        pass
def health_pack_Hozler(game, player, test = False):
    if not test:
        pass