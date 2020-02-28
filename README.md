# Lehrer vs. Zombies
Ein Top view game entwickelt mit pygame in python

## Ausführen
```
python3 main.py
```

# Notwendige Bibliotheken
- pygame
- pytmx
- pytweening
- Für Multiplayer: [joystickpins](https://github.com/astroPythoner/joystickpins) (Mehr dazu weiter unten)

***

# Das Spiel
### So spielst du
Wenn du die Datei main.py ausführst startet das Spiel. Im Menu das du jetzt siehst kannst du die Schwierigkeit und den Spielmodus auswählen. Unten kannst du noch eine Karte auswählen. Oben rechts ist eine Hilfe, oben links kannst du noch zwischen schöner und flüssiger Grafik auswählen. Und die Steuerungsart auswählen:

## Ziel des Spiels
Versuche die Zombies mit deinem PowerUp und deiner Waffe zu töten. Sammle die Healthpacks um dein Leben wieder aufzufüllen.
Trete nicht auf die Hindernisse und sammle die Objekte deiner Person. Ist der Balken unten voll musst du nurnoch die Butter finden.

## Spielmodi
Im Arena Modus musst du drei Zombie Wellen überleben, in der dritten erwartet dich ein Endgegner. Du kannst auswählen ob die nächste Zombiewelle nach einer gewissen Zeit oder nach töten aller Zombies kommen soll. 

Im Zombie Map Modus musst je nach Einstellung lang genug auf der Karte überleben oder alle Zombies töten. Am Ende des Spiels gilt es immer die Butter zu finden.

## Steuerungen

#### Tastatursteuerung mit Maus
Bei der Steuerung mit der Maus läuft der Spieler der Maus hinterher. Schießen kannst du mit der linken Maustaste oder der Leertaste. Das PowerUp benutzt du mit der rechten Maustaste oder mit X bzw. Y

Mit der Entertaste kommst du in die Spielerauswahl scrollen kannst du mit dem Mausrad oder den Pfeiltasten. Klicke mit der Maus auf den Spieler mit dem du spielen willst. Mit der Löschtaste kommst du zurück ins Hauptmenü und mit escape beendest du das Spiel.

#### Tastatursteureung mit Pfeiltasten
Bei der Tastatursteuerung bewegst du den Spieler mit den Pfeiltasten. Vor und zurück zum bewegen und links und rechts zum drehen. Wie bei der Maussteuerung schießt du mit Leertaste und benutzt dein PowerUp mit X bzw. Y

Genau wie bei der Maussteureung kannst du mit Enter in die Lehrerauswahl gelangen, mit der Löschtaste zum Hauptmenü und mit Escape beendest du das Spiel.

#### Kontrollersteurung

Die Kontrollersteurung ist ähnlich wie die Steuerung mit Pfeiltasten. Mit den links/rechts Tasten oder dem Joystick (je nach Kontroller) drehst du dich und mit vor und zurück bewegst du dich. Du schießt mit A oder dem Kreuz (je nach Kontroller). Mit B oder dem Kreis benutzt du dein Power-Up. In die Lehrerauswahl kommst du mit Select, in der du mit A oder Kreuz dein Lehrer auswählst. Mit start kommst du zurück ins Hauptmenü. In den Menüs kannst du mit dem Joystick oder links/rechts/hoch/runter Tasten den in blau gezeichneten Menupunkt bewegen und mit A oder Kreuz auswählen.

## Multiplayer

Um das Spiel im Multiplayer zu Spielen musst du mein [joystickpins projekt](https://github.com/astroPythoner/joystickpins) runterladen. Schließe dann ein Kontroller an (wenn er nicht aufgenommen ist lese dir das Erstellen neuer Kontrollermappings in dem joystickspins Projekt durch) und aktiviere ihn in den Einstellungen.
Der Multiplayer ist in einem Splitscreen gemacht, die beiden Spieler spielen also nebeneinander, es ist daher empfehlenswert das Fanster etwas breiter zu ziehen.

## Einstellungen

Drücke im Hauptmenü auf Einstellungen. Hier kannst du oben die Grafikeinstellungen zwischen schöner und flüssiger Grafik wechseln. Darunter kannst du die Musik und Sound Lautstärke ändern, in dem du auf das Plus und Minus neben den Balken klickst. Ganz unten kannst du auswählen welche Kontroller mitspielen sollen und bei der Tastatur zusätzlich auswählen ob per Maus oder Pfeiltasten gesteuert werden soll.

![Image could not be loaded](https://raw.githubusercontent.com/astroPythoner/Lehrer_vs_Zombies/master/img/erklaerung_mit_hintergrund.png)

## Erweitere das Spiel

Du willst andere Charaktere oder coolere Karten. Kein Problem, lese dir die Anleitungen in diesem Wiki oder als txt Datei durch. Du kannst eigene Charaktere und Karten erstellen und mit deinem Spielers spielen. Viel Spaß!

Links: [Karten erstellen Wiki](https://github.com/astroPythoner/Lehrer_vs_Zombies/wiki/Wie-erstelle-ich-eine-neue-Karte), [Charaktere hinzufügen Wiki](https://github.com/astroPythoner/Lehrer_vs_Zombies/wiki/Wie-erstelle-ich-neue-Charaktere), [Karten erstellen Datei](https://github.com/astroPythoner/Lehrer_vs_Zombies/blob/master/Wie%20erstellt%20man%20eine%20neue%20Karte/Anleitung.txt), [Charaktere hinzufügen Datei](https://github.com/astroPythoner/Lehrer_vs_Zombies/blob/master/Wie%20erstellt%20man%20einen%20neuen%20Spielercharakter/Anleitung.txt)

![image not found](https://raw.githubusercontent.com/astroPythoner/Lehrer_vs_Zombies/master/img/screenshot1.png)
![](https://raw.githubusercontent.com/astroPythoner/Lehrer_vs_Zombies/master/img/screenshot2.png)
![](https://raw.githubusercontent.com/astroPythoner/Lehrer_vs_Zombies/master/img/screenshot3.png)

***

# Copyright/Attribution Notice:

## This game was developed based on KidCanCode's Tile-based game
Webside: http://kidscancode.org/lessons/

GitHub: https://github.com/kidscancode/pygame_tutorials/tree/master/tilemap

Youtube: https://www.youtube.com/watch?v=VO8rTszcW4s&list=PLsk-HSGFjnaH5yghzu7PcOzm9NhsW0Urw

Thank you for the great tutorial lesson's even though not much of the original code is left. You really were a great      help and I learned a lot. Great videos!

## Map:
Thanks to Kenney from "www.kenney.nl".

"topdown shooter" art by Kenney.nl

https://opengameart.org/content/topdown-shooter

made with Tiled (https://www.mapeditor.org)

## Weapon pickup:
Guns by Gary <http://fossilrecords.net/> licensed under CC-BY-SA 3.0 <http://creativecommons.org/licenses/by-sa/3.0/>

"espionage.ogg" by http://opengameart.org/users/haeldb

## Some of the sounds:
made with bfxr (https://www.bfxr.net)
