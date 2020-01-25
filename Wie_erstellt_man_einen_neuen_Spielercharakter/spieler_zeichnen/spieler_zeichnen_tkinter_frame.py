## Zeichne einen Spielcharakter in einem Tkinter Frame
# Mit den Reglern kannst du Farben und mit den Auswahlknöpfen Frisur und Haltung verändern
# Drücke auf speichern und der neue Spieler wird als neuer_lehrer im img/player/Lehrer Ordner gespeichert
# !! tkinter und PIL müssen eventuell nachinstalliert werden !!
from tkinter import *
from PIL import Image, ImageTk
from pygame import Color,image
import os
from spieler_zeichnen import draw_player

root = Tk()
frame = Frame(root)
frame.pack()

### Nur verändern wenn Speichernort nicht standartmäßig ist
lehrer_file_name = "neuer_lehrer"
current_path = os.path.dirname(__file__)
game_folder = os.path.split(os.path.split(current_path)[0])[0]
img_folder = os.path.join(os.path.join(os.path.join(game_folder, 'img'),'Player'),'Lehrer')
print(img_folder)
if not os.path.exists(img_folder):
    raise Exception("Ort zum Speichern der Datei nicht gefunden ("+img_folder+")")


def update_img(event=None,draw=True):
    shirt_farbe = Color(shirt_farbe_r.get(), shirt_farbe_g.get(), shirt_farbe_b.get())
    hautfarbe_hand = Color(hautfarbe_hand_r.get(), hautfarbe_hand_g.get(), hautfarbe_hand_b.get())
    hautfarbe_gesicht = Color(hautfarbe_gesicht_r.get(), hautfarbe_gesicht_g.get(), hautfarbe_gesicht_b.get())
    haarfarbe = Color(haarfarbe_r.get(), haarfarbe_g.get(), haarfarbe_b.get())
    bild = draw_player(shirt_farbe=shirt_farbe,
                       hautfarbe_hand=hautfarbe_hand,
                       hautfarbe_gesicht=hautfarbe_gesicht,
                       haarfarbe=haarfarbe,
                       frisur=frisur.get(),
                       einhaendig=einhaendig.get(),
                       background=Color(255,255,255,255),
                       size = (147,129))
    image.save(bild, "player_currently_drawing.jpg")
    if draw:
        bild = ImageTk.PhotoImage(Image.open("player_currently_drawing.jpg"))
        vorschau.config(image = bild)
        vorschau.image = bild
def save_img():
    shirt_farbe = Color(shirt_farbe_r.get(), shirt_farbe_g.get(), shirt_farbe_b.get())
    hautfarbe_hand = Color(hautfarbe_hand_r.get(), hautfarbe_hand_g.get(), hautfarbe_hand_b.get())
    hautfarbe_gesicht = Color(hautfarbe_gesicht_r.get(), hautfarbe_gesicht_g.get(), hautfarbe_gesicht_b.get())
    haarfarbe = Color(haarfarbe_r.get(), haarfarbe_g.get(), haarfarbe_b.get())
    bild = draw_player(shirt_farbe=shirt_farbe,
                       hautfarbe_hand=hautfarbe_hand,
                       hautfarbe_gesicht=hautfarbe_gesicht,
                       haarfarbe=haarfarbe,
                       frisur=frisur.get(),
                       einhaendig=einhaendig.get())
    image.save(bild, os.path.join(img_folder, "player_" + lehrer_file_name + ".png"))
    root.destroy()

def reset_hautfarbe_hand():
    hautfarbe_hand_r.set(220)
    hautfarbe_hand_g.set(180)
    hautfarbe_hand_b.set(140)
def reset_hautfarbe_gesicht():
    hautfarbe_gesicht_r.set(230)
    hautfarbe_gesicht_g.set(180)
    hautfarbe_gesicht_b.set(125)

Label(frame,text="Shirt Farbe").grid(row=0,column=0)
shirt_farbe_r = Scale(frame, from_=0, to=255, orient=HORIZONTAL, command=update_img)
shirt_farbe_r.grid(row=0,column=1)
shirt_farbe_r.set(47)
shirt_farbe_g=Scale(frame, from_=0, to=255, orient=HORIZONTAL, command=update_img)
shirt_farbe_g.grid(row=0,column=2)
shirt_farbe_g.set(149)
shirt_farbe_b=Scale(frame, from_=0, to=255, orient=HORIZONTAL, command=update_img)
shirt_farbe_b.grid(row=0,column=3)
shirt_farbe_b.set(208)
Label(frame,text="Hautfarbe Hand").grid(row=1,column=0)
hautfarbe_hand_r = Scale(frame, from_=0, to=255, orient=HORIZONTAL, command=update_img)
hautfarbe_hand_r.grid(row=1,column=1)
hautfarbe_hand_r.set(220)
hautfarbe_hand_g=Scale(frame, from_=0, to=255, orient=HORIZONTAL, command=update_img)
hautfarbe_hand_g.grid(row=1,column=2)
hautfarbe_hand_g.set(180)
hautfarbe_hand_b=Scale(frame, from_=0, to=255, orient=HORIZONTAL, command=update_img)
hautfarbe_hand_b.grid(row=1,column=3)
hautfarbe_hand_b.set(140)
Button(frame,text="reset",command=reset_hautfarbe_hand).grid(row=1,column=4)
Label(frame,text="Hautfarbe Gesicht").grid(row=2,column=0)
hautfarbe_gesicht_r = Scale(frame, from_=0, to=255, orient=HORIZONTAL, command=update_img)
hautfarbe_gesicht_r.grid(row=2,column=1)
hautfarbe_gesicht_r.set(230)
hautfarbe_gesicht_g=Scale(frame, from_=0, to=255, orient=HORIZONTAL, command=update_img)
hautfarbe_gesicht_g.grid(row=2,column=2)
hautfarbe_gesicht_g.set(180)
hautfarbe_gesicht_b=Scale(frame, from_=0, to=255, orient=HORIZONTAL, command=update_img)
hautfarbe_gesicht_b.grid(row=2,column=3)
hautfarbe_gesicht_b.set(125)
Button(frame,text="reset",command=reset_hautfarbe_gesicht).grid(row=2,column=4)
Label(frame,text="Haarfarbe").grid(row=3,column=0)
haarfarbe_r = Scale(frame, from_=0, to=255, orient=HORIZONTAL, command=update_img)
haarfarbe_r.grid(row=3,column=1)
haarfarbe_r.set(51)
haarfarbe_g=Scale(frame, from_=0, to=255, orient=HORIZONTAL, command=update_img)
haarfarbe_g.grid(row=3,column=2)
haarfarbe_g.set(51)
haarfarbe_b=Scale(frame, from_=0, to=255, orient=HORIZONTAL, command=update_img)
haarfarbe_b.grid(row=3,column=3)
haarfarbe_b.set(51)
frisur = StringVar()
frisur.set("normal")
Radiobutton(frame, text="Lange Frisur", variable=frisur, value="lang", command=update_img).grid(row=5,column=0)
Radiobutton(frame, text="Glatze", variable=frisur, value="glatze", command=update_img).grid(row=5,column=1)
Radiobutton(frame, text="Normale Frisur", variable=frisur, value="normal", command=update_img).grid(row=5,column=2)
einhaendig = StringVar()
einhaendig.set("rechts")
Radiobutton(frame, text="Zweihändig", variable=einhaendig, value="beide", command=update_img).grid(row=6,column=0)
Radiobutton(frame, text="Rechtshänig", variable=einhaendig, value="rechts", command=update_img).grid(row=6,column=1)
Radiobutton(frame, text="Linkshändig", variable=einhaendig, value="links", command=update_img).grid(row=6,column=2)
Radiobutton(frame, text="Ohne Hände", variable=einhaendig, value="keine", command=update_img).grid(row=6,column=3)

update_img(draw=False)
bild = ImageTk.PhotoImage(Image.open("player_currently_drawing.jpg"))
vorschau = Label(frame, image=bild)
vorschau.grid(row=10, column=0, columnspan=5)

Button(frame,text="save",command=save_img).grid(row=12,column=4)

root.mainloop()