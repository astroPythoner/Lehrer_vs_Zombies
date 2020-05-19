import pygame
from os import path, listdir
import json

vec = pygame.math.Vector2

version = "3.2.0"

# Bildschrimgroesse
start_width = 960
start_height = 640
FPS = 60

# Pygame initialisieren und Fenster aufmachen
pygame.init()
pygame.mixer.init()
pygame.display.set_mode((start_width, start_height), pygame.RESIZABLE)

# Konstanten fuer Art des Spielendes und die Tastenarten
START_GAME = "start"
BEFORE_FIRST_GAME = "before first game"
PLAYING = "playing"
PLAYER_DIED = "player died"
COLLECTING_AT_END = "collecting at end"
WON_GAME = "won game"
TUTORIAL = "tutorial"
TUTORIAL_WALK = "walk"
TUTORIAL_COLLECT = "collect"
TUTORIAL_SHOOT = "shoot"
TUTORIAL_POWER_UP = "power up"

# Spielmodi
MAP_MODUS = "map modus"
ARENA_MODUS = "arena modus"
AFTER_TIME = "after time"
AFTER_KILLED = "after killed"

# Zeiten fuer den AFTER_TIME Modus (in sekunden)
TIME_MAP_LEVEL = 500  # Wie lange man auf der grossen Karte ueberleben muss
TIME_BETWEEN_ZOMBIE_WAVES = 150  # Wie Viel Zeit zwischen 2 Zombiewellen vergeht

# Schwierigkeiten
SCHWIERIGKEIT_ZOMBIE_KILLS = [0.3, 0.2, 0.1, 0.05, 0]  # Prozentualer Anteil der Zombies, die je nach Schwierigkeit weniger sind
SCHWIERIGKEIT_HEALTH_KILLS = [0, 0.05, 0.1, 0.15, 0.2]  # Prozentualer Anteil der Health Packs, die je nach Schwierigkeit weniger sind

# Dateienpfade herausfinden
game_folder = path.dirname(__file__)
img_folder = path.join(game_folder, 'img')
snd_folder = path.join(game_folder, 'snd')
music_folder = path.join(game_folder, 'music')
map_folder = path.join(game_folder, 'maps')

# Standartfarben
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
TEXT_COLOR = (170, 0, 0)  # sollte gut vor dem Hintergrund zu lesen sein
AUSWAHL_TEXT_COLOR = (215, 200, 200)
AUSWAHL_TEXT_RED = (255, 80, 80)
AUSWAHL_TEXT_GREEN = (50, 200, 50)
AUSWAHL_TEXT_SELECTED = (120, 120, 200)
AUSWAHL_TEXT_GREEN_SELECTED = (50, 200, 180)
LEHRER_UNLOCKED_TEXT_COLOR = (135, 120, 120)
LEBENSANZEIGE_GRUEN = (0, 200, 0)
LEBENSANZEIGE_ROT = (200, 0, 0)
LEBENSANZEIGE_GELB = (230, 210, 45)
POWER_UP_TIME_COLOR = (80, 100, 185)
LEVEL_FORTSCHRITTS_FARBE = (200, 50, 50)
BLIT_SCREEN_LINE_COLOR = BLACK
LEHRER_AUSWAHL_LINE_COLOR = BLACK

# Maustasten
MAUS_LEFT = "maus left"
MAUS_RIGHT = "maus right"
MAUS_ROLL_UP = "maus roll up"
MAUS_ROLL_DOWN = "maus roll down"

# Tilemap
TILESIZE = 64

# Grafik
WALL_LAYER = 1
PLAYER_LAYER = 3
BULLET_LAYER = 5
MOB_LAYER = 3
EFFECTS_LAYER = 7
ITEMS_LAYER = 1
# Karte der Umgebung
SMALL_MAP_SICHTWEITE_FAKTOR = 2
SMALL_MAP_ZOMBIE_COLOR = (200, 50, 50)
SMALL_MAP_PLAYER_COLOR = (50, 50, 200)
SMALL_MAP_ENDGEGNER_COLOR = (255, 80, 100)
# Himmelsrichtungen
NS = "NS"  # |
OW = "OW"  # -

# Lautstaerke
game_music_volume = 1
game_sound_volume = 0.5

AUTOMATISCH = "automatisch"

with open(path.join(path.dirname(path.realpath(__file__)),'players.json'), encoding='utf-8') as json_data:
    LEHRER = json.load(json_data)
    json_data.close()

LEHRER_NAMEN = list(LEHRER.keys())

# Maps  (Von jedem dieser Mapnamen muss im Ordner maps eine _big.tmx und _small.tmx datei liegen. Die kleine ist fuer den Arenamodus, die Groesse fuer den Karten modus)
# Auch 'Tutorial' (genau so) hier reinschreiben, allerdings nicht an erster Stelle, da diese Karte als Standartkarte genommen wird
MAP_NAMES = ["Stadt", "Schule", "Toturial"]

# Zombies
MOB_IMG = 'zombie.png'
MOB_SPEEDS = [150, 100, 75, 125]
MOB_HIT_RECT = pygame.Rect(0, 0, 30, 30)
MOB_HEALTH = 100
MOB_DAMAGE = [8, 9, 10, 11, 12]
MOB_KNOCKBACK = 20
AVOID_RADIUS = 50
DETECT_RADIUS = 400
TARGET_CHANGE_TIME = 5000
TARGET_CHANGE_TIME_RANDOM = 500

# Endgegner
ENDGEGNER_HEALTH = [100, 120, 140, 150, 160]  # Anzahl der Treffer je nach Schwierigkeit die gebraucht werden um Endgegner zu toeten
ENDGEGNER_HEALTH_MULTIPLAYER = [180, 200, 220, 230, 240]  # Im mulitplayer
MAXIMAL_NUM_ENDGEGNER_ZOMBIES = [6, 6, 7, 7, 8]  # Damit der Endgegner nicht endlos Zombies erstellt und diese irgendwann zu viele werden gibt es eine Grenze
MAXIMAL_NUM_EXTRA_ZOMBIES = 10
# Modus
ENDGEGNER_MODUS_WECHSEL_TIME = 1600  # Zeit zwischen den unterschiedlichen Modi
WEAPON = "weapon"
ZOMBIE = "zombie"
WALK_N_JUMP = "walk"
ENDGEGNER_MOUDS_TIMES = {WEAPON: 10000, ZOMBIE: 3500, WALK_N_JUMP: 9000}
ENDGEGNER_MODUS_REIHENFOLGE = [WEAPON, ZOMBIE, WALK_N_JUMP, WEAPON, WALK_N_JUMP, WEAPON, ZOMBIE, WALK_N_JUMP, ZOMBIE, WALK_N_JUMP, WEAPON, ZOMBIE, WALK_N_JUMP, WEAPON, ZOMBIE]
# Weapon Modus
ENDGEGNER_SHOOT_RATE = 350
ENDGEGNER_WEAPON_BARREL_OFFSET = vec(130, 0)
ENDGEGNER_WEAPON_DAMAGE = [9, 10, 10, 11, 11]  # Waffen Schaden je nach Schwierigkeit
ENDGEGNER_WEAPON_BULLET_SPEED = 500
# Zombie Modus
ENDGEGNER_NUM_ZOMBIES = 5
# Walk and Jump modus
ENDGEGNER_JUMP_TIME = 3500
ENDGEGNER_WALK_SPEED = vec(75, 0)
ENDGEGNER_WALK_WEAPON_RATE = 600
ENDGEGNER_WALK_SHOOT_OFFSET = vec(70, 0)
ENDGEGNER_TIME_NEW_POS_SEEN_BEFORE_JUMP = 2500

# Effekte
SPLAT = 'splat green.png'
RED_SPLAT = 'splat red.png'
DAMAGE_ALPHA = [i for i in range(0, 255, 55)]

# Health-pack hoch und runter bewegung
HEALTH_PACK_RANGE = 10  # Anzahl der Pixel hoch und runter
HEALTH_PACK_SPEED = 0.3  # Geschwindigkeit

# Sounds
BG_MUSIC = 'espionage.ogg'
PLAYER_HIT_SOUNDS = ['8.wav', '9.wav', '10.wav', '11.wav']
ZOMBIE_MOAN_SOUNDS = ['brains2.wav', 'brains3.wav', 'zombie-roar-1.wav', 'zombie-roar-2.wav', 'zombie-roar-3.wav', 'zombie-roar-5.wav', 'zombie-roar-6.wav', 'zombie-roar-7.wav']
ZOMBIE_HIT_SOUNDS = ['splat-15.wav']


def join_paths(array):
    return_pfad = array[0]
    for pfad in array[1:]:
        if isinstance(pfad, list):
            return_pfad = path.join(return_pfad, join_paths(pfad))
        else:
            return_pfad = path.join(return_pfad, pfad)
    return return_pfad


# Hintergund
background = pygame.image.load(path.join(img_folder, "background.png"))
background = pygame.transform.scale(background, (start_width, start_height))
background_rect = background.get_rect()

# Schriften
TITLE_FONT = join_paths([img_folder, "Fonts", 'ZOMBIE.TTF'])
HUD_FONT = join_paths([img_folder, "Fonts", 'Impacted2.0.ttf'])
ARIAL_FONT = pygame.font.match_font("arial")


# Bilder und Grafiken laden
def bilder_fuer_jeden_lehrer_laden(pfad, file_name_ohne_lehrer_name_hinten, dict_keys=[], convert_alpha=True, dict_with_img_and_icon=False, nur_von_is_lehrer=False, check_for_automatisch=""):
    return_dict = {}
    for lehrer in LEHRER:
        dict = LEHRER[lehrer]
        for dict_key in dict_keys:
            dict = dict[dict_key]
        if (nur_von_is_lehrer and dict["is_lehrer"]) or not nur_von_is_lehrer:
            if dict_with_img_and_icon:
                return_dict[lehrer] = {"img": pygame.image.load(path.join(pfad, file_name_ohne_lehrer_name_hinten + lehrer + ".png")).convert_alpha(),
                                       "icon": pygame.image.load(path.join(pfad, file_name_ohne_lehrer_name_hinten + "icon_" + lehrer + ".png")).convert_alpha()}
            else:
                if convert_alpha:
                    if check_for_automatisch != "":
                        if dict[check_for_automatisch] != AUTOMATISCH:
                            return_dict[lehrer] = {}
                            for element in dict[check_for_automatisch]:
                                return_dict[lehrer][element] = pygame.image.load(path.join(pfad, element)).convert_alpha()
                        else:
                            return_dict[lehrer] = pygame.image.load(path.join(pfad, file_name_ohne_lehrer_name_hinten + lehrer + ".png")).convert_alpha()
                    else:
                        return_dict[lehrer] = pygame.image.load(path.join(pfad, file_name_ohne_lehrer_name_hinten + lehrer + ".png")).convert_alpha()
                else:
                    return_dict[lehrer] = pygame.image.load(path.join(pfad, file_name_ohne_lehrer_name_hinten + lehrer + ".png"))
    return return_dict


PLAYER_IMGES = bilder_fuer_jeden_lehrer_laden(join_paths([img_folder, "Player", "Lehrer"]), "player_")
UPGRADE_PLAYER_IMGES = bilder_fuer_jeden_lehrer_laden(join_paths([img_folder, "Player", "Lehrer"]), "player_", dict_keys=["weapon_upgrade"], check_for_automatisch="player_image")
BULLET_IMGES = bilder_fuer_jeden_lehrer_laden(join_paths([img_folder, "Player", "Waffen"]), "bullet_", check_for_automatisch="weapon_bullets")
UPGRADE_BULLET_IMGES = bilder_fuer_jeden_lehrer_laden(join_paths([img_folder, "Player", "Waffen"]), "bullet_", dict_keys=["weapon_upgrade"], check_for_automatisch="weapon_image")
PEROSNEN_OBJECT_IMGES = bilder_fuer_jeden_lehrer_laden(join_paths([img_folder, "Objects", "Objects"]), "object_", dict_with_img_and_icon=True)
PERSONEN_OBSTACLE_IMGES = bilder_fuer_jeden_lehrer_laden(join_paths([img_folder, "Objects", "Obstacles"]), "obstacle_", dict_with_img_and_icon=True)
PERSONEN_POWER_UP_ICONS = bilder_fuer_jeden_lehrer_laden(join_paths([img_folder, "Objects", "PowerUp Icons"]), "powerup_icon_")

LIVE_BAR_IMG = pygame.image.load(path.join(img_folder, "livebar.png")).convert_alpha()

MOB_IMG = pygame.image.load(join_paths([img_folder, "Zombie", MOB_IMG])).convert_alpha()
GRAB_IMG = pygame.image.load(join_paths([img_folder, "Zombie", "zombie_grab.png"])).convert_alpha()
LEHRER_IMGES = bilder_fuer_jeden_lehrer_laden(join_paths([img_folder, "Player", "Lehrer"]), "player_", nur_von_is_lehrer=True)
SPLAT = pygame.image.load(join_paths([img_folder, "Zombie", SPLAT])).convert_alpha()
SPLAT = pygame.transform.scale(SPLAT, (64, 64))
RED_SPLAT = pygame.image.load(join_paths([img_folder, "Zombie", RED_SPLAT])).convert_alpha()
RED_SPLAT = pygame.transform.scale(RED_SPLAT, (64, 64))

HEALTH_PACK_IMG = pygame.image.load(join_paths([img_folder, "Objects", "health_pack.png"])).convert_alpha()
SMALL_HEART_IMG = pygame.image.load(join_paths([img_folder, "small_heart.png"])).convert_alpha()

ENDGEGNER_BULLET = pygame.image.load(join_paths([img_folder, "Endgegner", "bullet.png"])).convert_alpha()
ENDGEGNER_WALK_N_JUMP_IMG = pygame.image.load(join_paths([img_folder, "Endgegner", "endgegner_Walk_n_Jump.png"])).convert_alpha()
ENDGEGNER_SHOOT_IMG = pygame.image.load(join_paths([img_folder, "Endgegner", "endgegner_Shoot.png"])).convert_alpha()
ENDGEGNER_ZOMBIE_IMG = pygame.image.load(join_paths([img_folder, "Endgegner", "endgegner_Zombie.png"])).convert_alpha()
ENDGEGNER_IMGES = {WALK_N_JUMP: ENDGEGNER_WALK_N_JUMP_IMG, WEAPON: ENDGEGNER_SHOOT_IMG, ZOMBIE: ENDGEGNER_ZOMBIE_IMG}
ENDGEGNER_GRUBE = pygame.image.load(join_paths([img_folder, "Endgegner", "endgegner_Grube.png"])).convert_alpha()
ENDGEGNER_EXPLOSION_IMAGES = [pygame.image.load(join_paths([img_folder, "Endgegner", "Explosion", filename])).convert_alpha() for filename in listdir(join_paths([img_folder, "Endgegner", "Explosion"]))]

AT_END_IMG = pygame.image.load(path.join(img_folder, "Butter.png")).convert_alpha()
TEXT_FIND_AT_END = "Wo ist die Butter?"

ERKLAERUNG = (pygame.image.load(path.join(img_folder, "erklaerung.png")))

MAUS_IMG = pygame.image.load(join_paths([img_folder, "tasten", "maus.png"])).convert_alpha()
MAUS_RECHTS_IMG = pygame.image.load(join_paths([img_folder, "tasten", "maus_rechts.png"])).convert_alpha()
MAUS_LINKS_IMG = pygame.image.load(join_paths([img_folder, "tasten", "maus_links.png"])).convert_alpha()
PFEILTASTE_IMG = pygame.image.load(join_paths([img_folder, "tasten", "pfeiltasten.png"])).convert_alpha()
LEERTASTE_IMG = pygame.image.load(join_paths([img_folder, "tasten", "leertaste.png"])).convert_alpha()
X_Y_IMG = pygame.image.load(join_paths([img_folder, "tasten", "x_y_taste.png"])).convert_alpha()

# richtungsabhaengige hindernisse (z.b. Neutronenstrahl) bei allen lehrer, die das haben, laden
for lehrer in LEHRER:
    if LEHRER[lehrer]["obstacle_richtungsabhaengig"]:
        dict = {}
        for richtung in ["NS", "NS_begin", "NS_end", "OW", "OW_begin", "OW_end"]:
            dict[richtung] = pygame.image.load(join_paths([img_folder, "Objects", "Obstacles", "obstacle_" + lehrer + "_" + richtung + ".png"])).convert_alpha()
        LEHRER[lehrer]["richtungsabhaengige_bilder"] = dict

# restliche Dateien der einzelnen Lehrer laden
for lehrer in LEHRER:
    for file in LEHRER[lehrer]["other_files"]:
        LEHRER[lehrer]["other_files"][file] = pygame.image.load(join_paths([img_folder, LEHRER[lehrer]["other_files"][file]])).convert_alpha()

# Sounds laden
pygame.mixer.music.load(path.join(music_folder, BG_MUSIC))
pygame.mixer.music.set_volume(game_music_volume)


def sounds_fuer_jeden_lehrer_laden(pfad, file_name_ohne_lehrer_name_hinten, volume=game_sound_volume):
    return_dict = {}
    for lehrer in LEHRER:
        s = pygame.mixer.Sound(path.join(pfad, file_name_ohne_lehrer_name_hinten + lehrer + ".wav"))
        s.set_volume(volume)
        return_dict[lehrer] = s
    return return_dict


WEAPON_WAVS = sounds_fuer_jeden_lehrer_laden(path.join(snd_folder, "Waffen"), "shoot_")


def sounds_aus_array_laden(pfad, array, volume):
    return_array = []
    for snd in array:
        s = pygame.mixer.Sound(path.join(pfad, snd))
        s.set_volume(volume)
        return_array.append(s)
    return return_array


LEVEL_START_WAV = pygame.mixer.Sound(path.join(snd_folder, "level_start.wav"))
ZOMBIE_WAVS = sounds_aus_array_laden(path.join(snd_folder, "Zombies"), ZOMBIE_MOAN_SOUNDS, game_sound_volume)
ZOMBIE_HIT_WAVS = sounds_aus_array_laden(path.join(snd_folder, "Zombies"), ZOMBIE_HIT_SOUNDS, game_sound_volume)
PLAYER_HIT_WAVS = sounds_aus_array_laden(path.join(snd_folder, "pain"), PLAYER_HIT_SOUNDS, game_sound_volume)


def print_tabelle(zeige, zeige_upgrade, name, data):
    ### schreibt die im dict stehenden werte aus zeige und zeige_upgrade in zwei Zeilen fuer normale Werte mit Name vorne dran und upgrade werte
    # zwei Texte fuer upgrade und werte
    werte_text = name + " " * ((len("Voller Lehrername") + 1) - (len(name)))
    upgrade_text = "upgrade" + " " * ((len("Voller Lehrername") + 1) - 7)

    # alle zu zeigenden Werte durchgehen und zu werte bzw. upgrade text hinzufuegen
    for count, y in enumerate(zeige):
        werte_text += str(round(data[y], 2)) + " " * ((len(y) + 1) - (len(str(round(data[y], 2)))))
        if y in zeige_upgrade:
            upgrade_text += str(round(data["weapon_upgrade"][y], 2)) + " " * ((len(y) + 1) - (len(str(round(data["weapon_upgrade"][y], 2)))))
        else:
            upgrade_text += " " * (len(y) + 1)

    # Text schreiben
    print(werte_text)
    if with_upgrades:
        print(upgrade_text)


if __name__ == '__main__':
    # Werte zu den Lehrern als Tabelle zeigen
    zeige = ["player_health", "player_speed", "player_rot_speed", "power_up_time", "weapon_bullet_speed", "weapon_lifetime", "weapon_rate", "weapon_spread", "weapon_damage", "health_pack_amount", "obstacle_damage"]
    zeige_upgrade = ["weapon_bullet_speed", "weapon_lifetime", "weapon_rate", "weapon_spread", "weapon_damage", "bullet_count"]
    with_upgrades = True

    # Ueberschriften
    text = "Voller Lehrername "
    for y in zeige:
        text += y + " "
    print(text)

    avg = {'weapon_upgrade': {}}
    for x in LEHRER:
        print_tabelle(zeige, zeige_upgrade, x, LEHRER[x])
        for count, y in enumerate(zeige):
            avg[y] = (avg[y] * count + LEHRER[x][y]) / (count + 1) if y in avg else LEHRER[x][y]
            if y in zeige_upgrade:
                avg['weapon_upgrade'][y] = (avg[y] * count + LEHRER[x]["weapon_upgrade"][y]) / (count + 1) if y in avg else LEHRER[x]["weapon_upgrade"][y]
    print_tabelle(zeige, zeige_upgrade, "Schnitt", avg)
