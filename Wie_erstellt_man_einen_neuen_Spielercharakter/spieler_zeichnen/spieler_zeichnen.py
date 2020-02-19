import pygame
import os

### Hier anpassen
shirt_farbe = pygame.Color(47,149,208,255)
hautfarbe_hand = pygame.Color(220,180,140,255)
hautfarbe_gesicht = pygame.Color(220,160,100,255)
haarfarbe = pygame.Color(51,51,51,255)
frisur = "lang"  # lang,glatze,normal
einhaendig = "beide"  #links,rechts,keine,beide
lehrer_file_name = "test"
### Ab hier nur verändern wenn Speichernort nicht standartmäßig ist
current_path = os.path.dirname(__file__)
game_folder = os.path.split(os.path.split(current_path)[0])[0]
img_folder = os.path.join(os.path.join(os.path.join(game_folder, 'img'),'Player'),'Lehrer')
print(img_folder)
if not os.path.exists(img_folder):
    raise Exception("Ort zum Speichern der Datei nicht gefunden ("+img_folder+")")
### Ab hier nichts mehr verändern

def img_into_array(file_name,normal_color,flip=False):
    bild = pygame.image.load(os.path.join(current_path,file_name))
    if flip:
        bild = pygame.transform.flip(bild,False,True)
    array = []
    for x in range(49):
        teil = []
        for y in range(43):
            color = bild.get_at((x,y))
            if color == normal_color:
                teil.append("normal")
            elif color != pygame.Color(0,0,0,0):
                teil.append((normal_color.r-color.r,normal_color.g-color.g,normal_color.b-color.b,normal_color.a-color.a))
            else:
                teil.append((0,0,0,0))
        array.append(teil)
    return array
def set_img_at(img,color,normal_color,x,y):
    if color == "normal":
        img.set_at((x, y), normal_color)
    elif color == (0, 0, 0, 0):
        pass
    else:
        color_tuple = (abs(min([normal_color.r - color[0],255])), abs(min([normal_color.g - color[1],255])), abs(min([normal_color.b - color[2],255])), abs(min([normal_color.a - color[3],255])))
        color_to_set = pygame.Color(*color_tuple)
        img.set_at((x, y), color_to_set)

def draw_player(shirt_farbe=shirt_farbe,hautfarbe_hand=hautfarbe_hand,hautfarbe_gesicht=hautfarbe_gesicht,haarfarbe=haarfarbe,frisur=frisur,einhaendig=einhaendig,background=pygame.Color(0,0,0,0),size=(49,43)):

    # Schatten
    schatten_img = pygame.Surface((49,43),pygame.SRCALPHA)
    schatten_hand = pygame.image.load(os.path.join(current_path,'schatten_mit_hand.png'))
    schatten_shirt = pygame.image.load(os.path.join(current_path,'schatten_ohne_hand.png'))
    if einhaendig == "links":
        schatten_img.blit(pygame.transform.flip(schatten_hand, False, True),(0,0))
        schatten_img.blit(schatten_shirt,(0,0),special_flags=pygame.BLEND_RGBA_MAX)
    elif einhaendig == "rechts":
        schatten_img.blit(pygame.transform.flip(schatten_shirt, False, True),(0,0))
        schatten_img.blit(schatten_hand,(0,0),special_flags=pygame.BLEND_RGBA_MAX)
    elif einhaendig == "keine":
        schatten_img.blit(pygame.transform.flip(schatten_shirt, False, True),(0,0))
        schatten_img.blit(schatten_shirt,(0,0),special_flags=pygame.BLEND_RGBA_MAX)
    elif einhaendig == "beide":
        schatten_img.blit(pygame.transform.flip(schatten_hand, False, True), (0, 0))
        schatten_img.blit(schatten_hand, (0, 0),special_flags=pygame.BLEND_RGBA_MAX)

    # Shirt
    shirt_img = pygame.Surface((49,43),pygame.SRCALPHA)
    pixel_shirt = img_into_array("shirt.png",pygame.Color(47,149,208,255))
    pixel_hand_rechts = img_into_array("shirt_hand.png",pygame.Color(47,149,208,255))
    pixel_hand_links = img_into_array("shirt_hand.png",pygame.Color(47,149,208,255),flip=True)
    for x in range(49):
        for y in range(43):
            shirt_color = pixel_shirt[x][y]
            left_hand_color = pixel_hand_links[x][y]
            right_hand_color = pixel_hand_rechts[x][y]
            set_img_at(shirt_img, shirt_color,shirt_farbe,x,y)
            if einhaendig == "links" or einhaendig == "beide":
                set_img_at(shirt_img, left_hand_color, shirt_farbe,x,y)
            if einhaendig == "rechts" or einhaendig == "beide":
                set_img_at(shirt_img, right_hand_color, shirt_farbe,x,y)

    # Hand/Haende
    hand_img = pygame.Surface((49,43),pygame.SRCALPHA)
    pixel_right_hand = img_into_array("hand.png",pygame.Color(255,208,163,255))
    pixel_left_hand = img_into_array("hand.png",pygame.Color(255,208,163,255),flip=True)
    for x in range(49):
        for y in range(43):
            hand_left_color = pixel_left_hand[x][y]
            hand_right_color = pixel_right_hand[x][y]
            if einhaendig == "links" or einhaendig == "beide":
                set_img_at(hand_img,hand_left_color,hautfarbe_hand,x,y)
            if einhaendig == "rechts" or einhaendig == "beide":
                set_img_at(hand_img,hand_right_color,hautfarbe_hand,x,y)

    # Gesicht
    face_img = pygame.Surface((49,43),pygame.SRCALPHA)
    pixel_face = img_into_array("gesicht.png",pygame.Color(196,134,71,255))
    for x in range(49):
        for y in range(43):
            face_color = pixel_face[x][y]
            set_img_at(face_img,face_color,hautfarbe_gesicht,x,y)

    # Frisur
    hair_img = pygame.Surface((49,43),pygame.SRCALPHA)
    if frisur == "lang":
        pixel_hair = img_into_array("lange_frisur.png",pygame.Color(51,51,51,255))
    elif frisur == "glatze":
        pixel_hair = img_into_array("glatze.png",pygame.Color(51,51,51,255))
    else:
        pixel_hair = img_into_array("frisur.png", pygame.Color(51, 51, 51, 255))
    for x in range(49):
        for y in range(43):
            hair_color = pixel_hair[x][y]
            set_img_at(hair_img,hair_color,haarfarbe,x,y)



    bild = pygame.Surface((49,43),pygame.SRCALPHA)
    bild.fill(background)
    bild.blit(schatten_img,(0,0))
    bild.blit(hand_img,(0,0))
    bild.blit(shirt_img,(0,0))
    bild.blit(face_img,(0,0))
    bild.blit(hair_img,(0,0))
    bild = pygame.transform.scale(bild,size)

    return bild


if __name__ == '__main__':
    pygame.image.save(draw_player(),os.path.join(img_folder,"player_"+lehrer_file_name+".png"))