import pygame
from random import uniform, choice, randint, random, randrange
from constants import *
from tilemap import collide_hit_rect
import pytweening as tween
from itertools import chain
from time import time
from math import sin, sqrt
vec = pygame.math.Vector2

def collide_with_obstacles(sprite, group, dir):
    if dir == 'x':
        hits = pygame.sprite.spritecollide(sprite, group, False, collide_hit_rect)
        if hits:
            if hits[0].rect.centerx > sprite.hit_rect.centerx:
                sprite.pos.x = hits[0].rect.left - sprite.hit_rect.width / 2
            if hits[0].rect.centerx < sprite.hit_rect.centerx:
                sprite.pos.x = hits[0].rect.right + sprite.hit_rect.width / 2
            try:
                sprite.vel.x = 0
            except AttributeError:
                pass
            sprite.hit_rect.centerx = sprite.pos.x
            return True
    if dir == 'y':
        hits = pygame.sprite.spritecollide(sprite, group, False, collide_hit_rect)
        if hits:
            if hits[0].rect.centery > sprite.hit_rect.centery:
                sprite.pos.y = hits[0].rect.top - sprite.hit_rect.height / 2
            if hits[0].rect.centery < sprite.hit_rect.centery:
                sprite.pos.y = hits[0].rect.bottom + sprite.hit_rect.height / 2
            try:
                sprite.vel.y = 0
            except AttributeError:
                pass
            sprite.hit_rect.centery = sprite.pos.y
            return True
    return False

class Player(pygame.sprite.Sprite):
    def __init__(self, game, x, y, lehrer_name, player_num):
        self._layer = PLAYER_LAYER
        self.groups = game.all_sprites
        pygame.sprite.Sprite.__init__(self, self.groups)
        self.name = "Player"
        self.lehrer_name = lehrer_name
        self.game = game
        self.player_num = player_num
        self.orig_image = PLAYER_IMGES[self.lehrer_name]
        self.image = self.orig_image
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.hit_rect = pygame.Rect(LEHRER[self.lehrer_name]["player_hit_rect"])
        self.hit_rect.center = self.rect.center
        self.vel = vec(0, 0)
        self.pos = vec(x, y)
        self.rot = 0
        self.last_shot = 0
        self.weapon_upgrade_unlocked = False
        self.health = LEHRER[self.lehrer_name]["player_health"]
        self.damaged = False
        self.image_change_start_time = time() * 1000
        self.image_change_duration_time = 0
        self.in_other_image = False
        self.image_on_player_start_time = time() * 1000
        self.image_on_player_duration_time = 0
        self.image_to_place_on = pygame.Surface((10, 10))
        self.image_verschiebung = (0,0)
        self.in_image_on_player = False

    def move_player(self):
        if self.game.with_maussteuerung:
            maus_pos = pygame.mouse.get_pos()
            mitte = vec(self.pos.x - self.game.camera[self.player_num].inverted.x, self.pos.y - self.game.camera[self.player_num].inverted.y)

            if pygame.key.get_pressed()[pygame.K_LSHIFT] or pygame.mouse.get_pressed()[1]:
                richtung = 0
                winkel_diff = (maus_pos - mitte).angle_to(vec(1,0).rotate(-self.rot))
                if winkel_diff < 0:
                    winkel_diff += 360
                if winkel_diff <= 90 or winkel_diff >= 270:
                    richtung = 1
                else:
                    richtung = -0.3

                distance = (maus_pos - mitte).length()
                if distance < self.game.maussteuerung_circle_radius/4:
                    self.vel = vec(0,0)
                elif distance < self.game.maussteuerung_circle_radius:
                    self.vel = vec(richtung*(distance / self.game.maussteuerung_circle_radius * (LEHRER[self.lehrer_name]["player_speed"]-40)),0).rotate(-self.rot)
                else:
                    self.vel = vec(richtung*(LEHRER[self.lehrer_name]["player_speed"]-40),0).rotate(-self.rot)

                self.pos += self.vel * self.game.dt

            else:
                desired = (maus_pos - mitte).normalize()
                distance = (maus_pos - mitte).length()
                if distance < self.game.maussteuerung_circle_radius:
                    desired *= distance / self.game.maussteuerung_circle_radius * (LEHRER[self.lehrer_name]["player_speed"]-40)
                else:
                    desired *= (LEHRER[self.lehrer_name]["player_speed"]-40)
                steer = (desired - self.vel)
                if steer.length() > (LEHRER[self.lehrer_name]["player_rot_speed"]/10):
                    steer.scale_to_length((LEHRER[self.lehrer_name]["player_rot_speed"]/10))

                self.vel += steer

                if self.vel.length() > (LEHRER[self.lehrer_name]["player_speed"]-40):
                    self.vel.scale_to_length((LEHRER[self.lehrer_name]["player_speed"]-40))

                self.rot = -self.vel.as_polar()[1]

                if not distance < self.game.maussteuerung_circle_radius / 4:
                    self.pos += self.vel * self.game.dt

        else:
            self.rot_speed = 0
            self.vel = vec(0, 0)
            if pygame.key.get_pressed()[pygame.K_LEFT]:
                self.rot_speed = LEHRER[self.lehrer_name]["player_rot_speed"]
            if pygame.key.get_pressed()[pygame.K_RIGHT]:
                self.rot_speed = -LEHRER[self.lehrer_name]["player_rot_speed"]
            if pygame.key.get_pressed()[pygame.K_UP]:
                self.vel = vec(LEHRER[self.lehrer_name]["player_speed"], 0).rotate(-self.rot)
            if pygame.key.get_pressed()[pygame.K_DOWN]:
                self.vel = vec((-LEHRER[self.lehrer_name]["player_speed"]) / 2, 0).rotate(-self.rot)

            self.rot = (self.rot + self.rot_speed * self.game.dt) % 360

            self.pos += self.vel * self.game.dt

    def shoot(self):
        now = pygame.time.get_ticks()
        weapon_rate = LEHRER[self.lehrer_name]["weapon_rate"]
        if self.weapon_upgrade_unlocked:
            weapon_rate = LEHRER[self.lehrer_name]["weapon_upgrade"]["weapon_rate"]
        if now - self.last_shot > weapon_rate:
            self.last_shot = now
            self.game.werte_since_last_lehrer_change[self]["shoots"] += 1
            dir = vec(1, 0).rotate(-self.rot)
            pos = self.pos + vec(*LEHRER[self.lehrer_name]["weapon_barrel_offset"]).rotate(-self.rot)
            bullet_count = LEHRER[self.lehrer_name]["bullet_count"]
            if self.weapon_upgrade_unlocked:
                bullet_count = LEHRER[self.lehrer_name]['weapon_upgrade']["bullet_count"]
            for i in range(bullet_count):
                if self.weapon_upgrade_unlocked:
                    spread = uniform(-LEHRER[self.lehrer_name]['weapon_upgrade']["weapon_spread"], LEHRER[self.lehrer_name]['weapon_upgrade']["weapon_spread"])
                else:
                    spread = uniform(-LEHRER[self.lehrer_name]["weapon_spread"], LEHRER[self.lehrer_name]["weapon_spread"])
                damage = LEHRER[self.lehrer_name]["weapon_damage"]
                if self.weapon_upgrade_unlocked:
                    damage =LEHRER[self.lehrer_name]["weapon_upgrade"]["weapon_damage"]
                Bullet(self.game, pos, dir.rotate(spread), damage,self.rot, self)
                snd = WEAPON_WAVS[self.lehrer_name]
                if snd.get_num_channels() > 2:
                    snd.stop()
                snd.play()

    def hit(self):
        self.damaged = True
        self.damage_alpha = chain(DAMAGE_ALPHA * 4)

    def update(self):
        self.move_player()
        self.image = pygame.transform.rotate(self.orig_image, self.rot)
        if self.damaged:
            try:
                self.image.fill((255, 255, 255, next(self.damage_alpha)), special_flags=pygame.BLEND_RGBA_MULT)
            except:
                self.damaged = False
        self.rect = self.image.get_rect()
        self.rect.center = self.pos
        self.hit_rect.centerx = self.pos.x
        collide_with_obstacles(self, self.game.obstacles, 'x')
        self.hit_rect.centery = self.pos.y
        collide_with_obstacles(self, self.game.obstacles, 'y')
        self.rect.center = self.hit_rect.center
        if self.image_change_start_time + self.image_change_duration_time <= time()*1000 and self.in_other_image:
            self.update_image()
            self.in_other_image = False
        if self.image_on_player_start_time + self.image_on_player_duration_time <= time()*1000 and self.in_image_on_player:
            self.update_image()
            self.in_image_on_player = False
            # Das auf den Spieler zu zeichnende Bild wird nach zeichnen der Karte und Figuren in der Funktion draw_display im main.py auf den screen gezeichnet

    def add_health(self, amount):
        self.health += amount
        if self.health > LEHRER[self.lehrer_name]["player_health"]:
            self.health = LEHRER[self.lehrer_name]["player_health"]

    def update_image(self):
        if self.weapon_upgrade_unlocked:
            if isinstance(UPGRADE_PLAYER_IMGES[self.lehrer_name],type(dict)):
                self.orig_image = UPGRADE_PLAYER_IMGES[self.lehrer_name][list(UPGRADE_PLAYER_IMGES[self.lehrer_name])[0]]
            else:
                self.orig_image = UPGRADE_PLAYER_IMGES[self.lehrer_name]
        else:
            self.orig_image = PLAYER_IMGES[self.lehrer_name]
        self.image = self.orig_image
        self.rect = self.image.get_rect()
        self.rect.center = self.hit_rect.center

    def change_img_for_given_time(self, image, time_in_millis):
        self.orig_image = image
        self.image = self.orig_image
        self.rect = self.image.get_rect()
        self.rect.center = self.hit_rect.center
        self.image_change_start_time = time() * 1000
        self.image_change_duration_time = time_in_millis
        self.in_other_image = True

    def place_img_on_player_for_given_time(self,img,time_in_millis,x_verschiebung=0,y_verschiebung=0):
        self.image_to_place_on = img
        self.image_verschiebung = (x_verschiebung, y_verschiebung)
        self.image_on_player_start_time = time() * 1000
        self.image_on_player_duration_time = time_in_millis
        self.in_image_on_player = True

class Bullet(pygame.sprite.Sprite):
    def __init__(self, game, pos, dir, damage, rot, player):
        self._layer = BULLET_LAYER
        self.groups = game.all_sprites, game.bullets
        pygame.sprite.Sprite.__init__(self, self.groups)
        self.name = "Bullet"
        self.game = game
        self.player = player
        if player.weapon_upgrade_unlocked:
            bullet_image = UPGRADE_BULLET_IMGES[player.lehrer_name]
        else:
            bullet_image = BULLET_IMGES[player.lehrer_name]
        if isinstance(bullet_image, type(dict)):
            self.image = bullet_image[choice(list(bullet_image))]
        else:
            self.image = bullet_image
        self.image = pygame.transform.rotate(self.image,rot)
        self.rect = self.image.get_rect()
        self.hit_rect = self.rect
        self.pos = vec(pos)
        self.rect.center = pos
        #spread = uniform(-GUN_SPREAD, GUN_SPREAD)
        if player.weapon_upgrade_unlocked:
            self.vel = dir * LEHRER[player.lehrer_name]['weapon_upgrade']['weapon_bullet_speed'] * uniform(0.9, 1.1)
        else:
            self.vel = dir * LEHRER[player.lehrer_name]['weapon_bullet_speed'] * uniform(0.9, 1.1)
        self.spawn_time = pygame.time.get_ticks()
        self.damage = damage

    def update(self):
        self.pos += self.vel * self.game.dt
        self.rect.center = self.pos
        if pygame.sprite.spritecollideany(self, self.game.obstacles):
            self.kill()
        if self.player.weapon_upgrade_unlocked:
            if pygame.time.get_ticks() - self.spawn_time > LEHRER[self.player.lehrer_name]['weapon_upgrade']['weapon_lifetime']:
                self.kill()
        else:
            if pygame.time.get_ticks() - self.spawn_time > LEHRER[self.player.lehrer_name]['weapon_lifetime']:
                self.kill()

class Grab(pygame.sprite.Sprite):
    def __init__(self, game, x, y, time_until_getting_zombie = 6000):
        self._layer = 2
        self.groups = game.all_sprites
        self.game = game
        pygame.sprite.Sprite.__init__(self, self.groups)
        self.image = GRAB_IMG
        self.rect = self.image.get_rect()
        self.rect.center = (x,y)
        self.spawn_time = time() * 1000
        self.time_until_zombie = time_until_getting_zombie

    def update(self):
        if time()*1000 - self.spawn_time > self.time_until_zombie:
            self.kill()
            Mob(self.game, self.rect.centerx,self.rect.centery)

class Mob(pygame.sprite.Sprite):
    def __init__(self, game, x, y, health = MOB_HEALTH, from_endgegner = False):
        self._layer = MOB_LAYER
        if from_endgegner:
            self.groups = game.all_sprites, game.zombies, game.endgegner_zombies
        else:
            self.groups = game.all_sprites, game.zombies
        pygame.sprite.Sprite.__init__(self, self.groups)
        self.name = "Mob"
        self.game = game
        self.from_endgegner = from_endgegner
        self.image = []
        for count,player in enumerate(self.game.players):
            if LEHRER[player.lehrer_name]["is_lehrer"] or from_endgegner:
                self.image.append(MOB_IMG.copy())
            else:
                self.image.append(choice(list(LEHRER_IMGES.values())).copy())
        self.orig_image = []
        self.do_not_change_image = []
        for count,image in enumerate(self.image):
            self.orig_image.append(image)
            self.do_not_change_image.append(image)
            self.image[count] = pygame.transform.rotate(image, 0)
        self.rect = self.image[0].get_rect()
        self.rect.center = (x, y)
        self.hit_rect = MOB_HIT_RECT.copy()
        self.hit_rect.center = self.rect.center
        self.pos = vec(x, y)
        self.vel = vec(0, 0)
        self.acc = vec(0, 0)
        self.rect.center = self.pos
        self.rot = 0
        self.start_health = health
        self.health = health
        self.speed = choice(MOB_SPEEDS)
        if from_endgegner:
            self.detect_radius = self.game.map.width
        else:
            self.detect_radius = DETECT_RADIUS
        if self.game.multiplayer:
            self.target = None
        else:
            self.target = self.game.players[0]
        self.last_traget_change = 0
        self.image_change_start_time = time()*1000
        self.image_change_duration_time = 0
        self.in_other_image = False
        self.stand_still_during_time = False
        self.damage_during_time = 0
        self.damage_so_far = 0
        self.image_on_player_start_time = time() * 1000
        self.image_on_player_duration_time = 0
        self.image_to_place_on = pygame.Surface((10, 10))
        self.image_verschiebung = (0, 0)
        self.in_image_on_mob = False

    def avoid_mobs(self):
        for mob in self.game.zombies:
            if mob != self:
                dist = self.pos - mob.pos
                if 0 < dist.length() < AVOID_RADIUS:
                    self.acc += dist.normalize()

    def update(self):
        if False in self.game.paused:
            if self.in_other_image and self.damage_during_time > 0:
                 damage = int((((time()*1000 - self.image_change_start_time) / self.image_change_duration_time) * self.damage_during_time) - self.damage_so_far)
                 self.damage_so_far += damage
                 self.health -= damage
            if ((self.stand_still_during_time and not self.in_other_image) or not self.stand_still_during_time):
                if self.target != None:
                    target_dist = self.target.pos - self.pos
                    if target_dist.length_squared() < self.detect_radius**2:
                            # In Richtung target laufen
                            if random() < 0.002:
                                choice(ZOMBIE_WAVS).play()
                            self.rot = target_dist.angle_to(vec(1, 0))
                            for count,player in enumerate(self.game.players):
                                self.image[count] = pygame.transform.rotate(self.orig_image[count], self.rot)
                            self.rect.center = self.pos
                            self.acc = vec(1, 0).rotate(-self.rot)
                            self.avoid_mobs()
                            try:
                                self.acc.scale_to_length(self.speed)
                            except ValueError:
                                self.acc = vec(1, 0).rotate(-self.rot)
                                self.acc.scale_to_length(self.speed)
                            if not (self.game.spielmodus == TUTORIAL and (self.game.game_status == TUTORIAL_WALK or self.game.game_status == TUTORIAL_COLLECT or self.game.game_status == TUTORIAL_SHOOT)):
                                # bewegen
                                self.acc += self.vel * -1
                                self.vel += self.acc * self.game.dt
                                self.pos += self.vel * self.game.dt + 0.5 * self.acc * self.game.dt ** 2
                                self.hit_rect.centerx = self.pos.x
                                collide_with_obstacles(self, self.game.obstacles, 'x')
                                self.hit_rect.centery = self.pos.y
                                collide_with_obstacles(self, self.game.obstacles, 'y')
                                self.rect.center = self.hit_rect.center
                    else:
                        # target nichtmehr in der Naehe, neues target wird gesucht
                        if self.game.multiplayer:
                            self.target = None
                    if time() - self.last_traget_change > TARGET_CHANGE_TIME:
                        # Zeit abgelaufen, neu suchen, wenn anderer Spieler naeher dran ist, dieses verfolgen
                        if self.game.multiplayer:
                            self.target = None
                else:
                    # Nach target suchen
                    last_entfernung = 100000000
                    for player in self.game.players:
                        target_dist = (player.pos - self.pos).length_squared()
                        if target_dist < self.detect_radius ** 2:
                            if target_dist < last_entfernung:
                                last_entfernung = target_dist
                                self.target = player
                    self.last_traget_change = time() + randrange(-TARGET_CHANGE_TIME_RANDOM,TARGET_CHANGE_TIME_RANDOM)
            if self.health <= 0:
                choice(ZOMBIE_HIT_WAVS).play()
                self.kill()
                if self.game.multiplayer:
                    self.game.map_img.blit(SPLAT, self.pos - vec(32, 32))
                else:
                    if LEHRER[self.game.players[0].lehrer_name]['is_lehrer']:
                        self.game.map_img.blit(SPLAT, self.pos - vec(32, 32))
                    else:
                        self.game.map_img.blit(RED_SPLAT, self.pos - vec(32, 32))
        if self.image_change_start_time + self.image_change_duration_time <= time()*1000 and self.in_other_image:
            self.update_image(True)
            self.in_other_image = False
        if self.image_on_player_start_time + self.image_on_player_duration_time <= time()*1000 and self.in_image_on_mob:
            self.update_image(True)
            self.in_image_on_mob = False
            # Das auf den Zombie zu zeichnende Bild wird nach zeichnen der Karte und Figuren in der Funktion draw_display im main.py auf den screen gezeichnet

    def draw_health(self):
        for count in range(0,len(self.game.players)):
            if self.in_other_image and self.stand_still_during_time:
                self.image[count] = pygame.transform.rotate(self.orig_image[count], self.rot)
            self.rect.center = self.hit_rect.center
            if self.health > self.stand_still_during_time * 0.6:
                col = LEBENSANZEIGE_GRUEN
            elif self.health > self.start_health * 0.3:
                col = LEBENSANZEIGE_GELB
            else:
                col = LEBENSANZEIGE_ROT
            width = int(self.rect.width * self.health / self.start_health)
            self.health_bar = pygame.Rect(0, 0, width, 7)
            if self.health < self.start_health:
                pygame.draw.rect(self.image[count], col, self.health_bar)

    def update_image(self, bleibe_der_selbe_lehrer = False):
        for count,player in enumerate(self.game.players):
            if LEHRER[player.lehrer_name]["is_lehrer"] or self.from_endgegner:
                self.image[count] = MOB_IMG.copy()
                self.orig_image[count] = self.image[count]
                self.do_not_change_image[count] = self.image[count]
                self.rect = self.image[count].get_rect()
            else:
                if bleibe_der_selbe_lehrer:
                    self.image[count] = self.do_not_change_image[count]
                else:
                    self.image[count] = choice(list(LEHRER_IMGES.values())).copy()
                self.do_not_change_image[count] = self.image[count]
                self.orig_image[count] = self.image[count]
                self.rect = self.image[count].get_rect()
            self.image[count] = pygame.transform.rotate(self.orig_image[count], self.rot)
            self.rect.center = self.hit_rect.center

    def change_img_for_given_time(self,image=None,time_is_millis=0, stand_still_during_time=False,damge_during_time = 0):
        for player_num in range(0,len(self.game.players)):
            if image != None:
                self.image[player_num] = image
                self.orig_image[player_num] = self.image[player_num]
                self.rect = self.image[player_num].get_rect()
                self.image[player_num] = pygame.transform.rotate(self.orig_image[player_num], self.rot)
                self.rect.center = self.hit_rect.center
            self.image_change_start_time = time() * 1000
            self.image_change_duration_time = time_is_millis
            self.stand_still_during_time = stand_still_during_time
            self.damage_during_time = damge_during_time
            self.damage_so_far = 0
            self.in_other_image = True

    def place_img_on_zombie_for_given_time(self,img,time_in_millis,x_verschiebung=0,y_verschiebung=0):
        self.image_to_place_on = img
        self.image_verschiebung = (x_verschiebung, y_verschiebung)
        self.image_on_player_start_time = time() * 1000
        self.image_on_player_duration_time = time_in_millis
        self.in_image_on_mob = True

class End_Gegner(pygame.sprite.Sprite):
    def __init__(self, game):
        self.groups = game.all_sprites
        pygame.sprite.Sprite.__init__(self, self.groups)
        self.name = "End Gegner"
        self.game = game
        # Bild und Position
        self.image = ENDGEGNER_GRUBE
        self.orig_image = self.image
        self.rect = self.image.get_rect()
        self.hit_rect = self.rect
        self.pos = self.game.endgegner_pos
        self.rect.center = self.pos
        self.rot = 0
        # Leben
        if self.game.multiplayer:
            self.health = ENDGEGNER_HEALTH_MULTIPLAYER[self.game.schwierigkeit-1]
        else:
            self.health = ENDGEGNER_HEALTH[self.game.schwierigkeit-1]
        self.alive = True
        # Am Anfang den 5 sekunden countdown abwarten
        self.spawn_time = time()
        # Modus zwischen Waffe und Zombie
        self.modus = None
        self.modus_index = -1
        self.last_modus_wechsel = 0
        # Waffe
        self.last_shot = 0
        # Zombies endsenden
        self.last_zombie = 0
        self.num_zomies = 0
        self.zombie_rate = (ENDGEGNER_MOUDS_TIMES[ZOMBIE]/(ENDGEGNER_NUM_ZOMBIES-1)) - 150
        # Laufen und springen
        self.last_jump = 0
        self.next_pos = choice(self.game.endgegner_jump_points)

    def update(self):
        if time() - self.spawn_time > 6:
            self.change_modus()
            self.make_modus_event()
            self.image = pygame.transform.rotate(self.orig_image, self.rot)
            self.rect = self.image.get_rect()
            self.hit_rect = self.rect
            self.rect.center = self.pos
            if random() < 0.005 and len(self.game.zombies) < MAXIMAL_NUM_ENDGEGNER_ZOMBIES[self.game.schwierigkeit-1] + MAXIMAL_NUM_EXTRA_ZOMBIES - 1:
                zombie_orte = []
                for tile_object in self.game.map.tmxdata.objects:
                    obj_center = vec(tile_object.x + tile_object.width / 2,tile_object.y + tile_object.height / 2)
                    if tile_object.name == 'zombie':
                        zombie_orte.append([obj_center.x, obj_center.y])
                random_ort = choice(zombie_orte)
                Grab(self.game,random_ort[0],random_ort[1],2500)

    def change_modus(self):
        now = time() * 1000
        if self.modus == None:
            if now - self.last_modus_wechsel > ENDGEGNER_MODUS_WECHSEL_TIME:
                self.last_modus_wechsel = time() * 1000
                self.modus = ENDGEGNER_MODUS_REIHENFOLGE[(self.modus_index + 1)%len(ENDGEGNER_MODUS_REIHENFOLGE)]
                self.modus_index += 1
                self.last_shot = 0
                self.last_zombie = 0
                self.num_zomies = 0
                self.orig_image = ENDGEGNER_IMGES[self.modus]
        else:
            if now - self.last_modus_wechsel > ENDGEGNER_MOUDS_TIMES[self.modus]:
                self.last_modus_wechsel = time() * 1000
                self.modus = None

    def make_modus_event(self):
        now = time() * 1000
        if self.modus == WEAPON:
            self.rot -= 2
            if now - self.last_shot > ENDGEGNER_SHOOT_RATE:
                self.last_shot = now
                dir = vec(1, 0).rotate(-self.rot)
                End_Gegner_Bullet(self.game, self.pos + ENDGEGNER_WEAPON_BARREL_OFFSET.rotate(-self.rot), dir, ENDGEGNER_WEAPON_DAMAGE[self.game.schwierigkeit-1], -self.rot)
                End_Gegner_Bullet(self.game, self.pos - ENDGEGNER_WEAPON_BARREL_OFFSET.rotate(-self.rot), dir.rotate(180), ENDGEGNER_WEAPON_DAMAGE[self.game.schwierigkeit-1], -self.rot)
        elif self.modus == ZOMBIE:
            if now - self.last_zombie > self.zombie_rate and self.num_zomies < ENDGEGNER_NUM_ZOMBIES:
                if len(self.game.endgegner_zombies) == MAXIMAL_NUM_ENDGEGNER_ZOMBIES[self.game.schwierigkeit-1]:
                    choice(list(self.game.endgegner_zombies)).kill()
                self.last_zombie = now
                self.num_zomies += 1
                Mob(self.game, self.pos.x, self.pos.y, int(MOB_HEALTH*0.85), True)
        elif self.modus == WALK_N_JUMP:
            if now - self.last_jump > ENDGEGNER_JUMP_TIME:
                for sprite in self.game.all_sprites:
                    if isinstance(sprite, End_Gegner_Grube):
                        sprite.kill()
                self.last_jump = now
                self.pos = self.next_pos
                while True:
                    self.next_pos = choice(self.game.endgegner_jump_points)
                    if self.next_pos != self.pos:
                        break
                least_entfernung = 100000000
                for player in self.game.players:
                    target_dist = (player.pos - self.pos).length_squared()
                    if target_dist < least_entfernung:
                        least_entfernung = target_dist
                        target = player
                vect = (self.pos - target.pos)
                self.rot = vect.angle_to(vec(-1, 0))
            else:
                # Grube zum anzeigen wo er als naechstes hinspringt
                if now - self.last_jump > ENDGEGNER_JUMP_TIME - ENDGEGNER_TIME_NEW_POS_SEEN_BEFORE_JUMP and now + ENDGEGNER_TIME_NEW_POS_SEEN_BEFORE_JUMP < self.last_modus_wechsel + ENDGEGNER_MOUDS_TIMES[
                    WALK_N_JUMP]:
                    gibt_bereits_eine_grube = False
                    for sprite in self.game.all_sprites:
                        if isinstance(sprite, End_Gegner_Grube):
                            gibt_bereits_eine_grube = True
                    if not gibt_bereits_eine_grube:
                        End_Gegner_Grube(self.game, self.next_pos)
                # bewegen
                if not pygame.sprite.spritecollide(self,self.game.obstacles,False,collide_hit_rect):
                    self.pos += ENDGEGNER_WALK_SPEED.rotate(-self.rot) * self.game.dt
                if now - self.last_shot > ENDGEGNER_WALK_WEAPON_RATE:
                    self.last_shot = now
                    End_Gegner_Bullet(self.game, self.pos + ENDGEGNER_WALK_SHOOT_OFFSET.rotate(-self.rot), vec(1, 0).rotate(-self.rot), ENDGEGNER_WEAPON_DAMAGE[self.game.schwierigkeit-1], self.rot)

class End_Gegner_Grube(pygame.sprite.Sprite):
    def __init__(self, game, pos):
        self._layer = 2
        self.groups = game.all_sprites
        pygame.sprite.Sprite.__init__(self, self.groups)
        self.name = "Endgegner Grube"
        self.image = ENDGEGNER_GRUBE
        self.rect = self.image.get_rect()
        self.hit_rect = self.rect
        self.rect.x = pos[0] - self.rect.width/2
        self.rect.y = pos[1] - self.rect.height/2

class End_Gegner_Bullet(pygame.sprite.Sprite):
    def __init__(self, game, pos, dir, damage, rot):
        self._layer = BULLET_LAYER
        self.groups = game.all_sprites, game.endgegner_bullets
        pygame.sprite.Sprite.__init__(self, self.groups)
        self.name = "Endgegner Bullet"
        self.game = game
        self.image = ENDGEGNER_BULLET
        self.image = pygame.transform.rotate(self.image,rot)
        self.rect = self.image.get_rect()
        self.hit_rect = self.rect
        self.pos = vec(pos)
        self.rect.center = pos
        self.vel = dir * ENDGEGNER_WEAPON_BULLET_SPEED
        self.spawn_time = pygame.time.get_ticks()
        self.damage = damage

    def update(self):
        self.pos += self.vel * self.game.dt
        self.rect.center = self.pos
        if pygame.sprite.spritecollideany(self, self.game.obstacles):
            self.kill()

class End_Gegner_Explosion(pygame.sprite.Sprite):
    # Explosionen in unterschiedlichen Groessen
    def __init__(self, game, center):
        self.groups = game.all_sprites
        pygame.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.image = ENDGEGNER_EXPLOSION_IMAGES[0]
        self.rect = self.image.get_rect()
        self.rect.center = center
        # In welchem BIld der Explosion bin ich
        self.frame = 0
        self.last_update = pygame.time.get_ticks()
        # Schnelligkeit der Explosion
        self.frame_rate = 75

    def update(self):
        now = pygame.time.get_ticks()
        if now - self.last_update > self.frame_rate:
            # naechstes Bild der Explosion anzeigen
            self.last_update = now
            self.frame += 1
            if self.frame == len(ENDGEGNER_EXPLOSION_IMAGES):
                self.kill()
            else:
                center = self.rect.center
                self.image = ENDGEGNER_EXPLOSION_IMAGES[self.frame]
                self.rect = self.image.get_rect()
                self.rect.center = center

class Obstacle(pygame.sprite.Sprite):
    def __init__(self, game, x, y, w, h):
        self.groups = game.obstacles
        pygame.sprite.Sprite.__init__(self, self.groups)
        self.name = "Obstacle"
        self.game = game
        self.rect = pygame.Rect(x, y, w, h)
        self.hit_rect = self.rect
        self.x = x
        self.y = y
        self.rect.x = x
        self.rect.y = y

class Personen_Obstacle(pygame.sprite.Sprite):
    def __init__(self, game, x, y, w, h, orientation=None, is_begin = False, is_end = False):
        self.groups = game.personen_obstacles, game.all_sprites
        pygame.sprite.Sprite.__init__(self, self.groups)
        self.name = "Personen Obstacle"
        self.game = game
        self.rect = pygame.Rect(x, y, w, h)
        self.hit_rect = self.rect
        self.x = x
        self.y = y
        self.rect.x = x
        self.rect.y = y
        self.orientation = orientation
        self.is_begin = is_begin
        self.is_end = is_end
        self.image = []
        for count,player in enumerate(self.game.players):
            if LEHRER[player.lehrer_name]["obstacle_richtungsabhaengig"]:
                richtung = orientation
                if is_begin:
                    richtung += "_begin"
                if is_end:
                    richtung += "_end"
                self.image.append(LEHRER[player.lehrer_name]["richtungsabhaengige_bilder"][richtung])
            else:
                self.image.append(PERSONEN_OBSTACLE_IMGES[player.lehrer_name]["img"])
            if LEHRER[player.lehrer_name]["obstacle_rotation"]:
                self.image[count] = pygame.transform.rotate(self.image[count], choice([0,90,180,270,360]))

    def update_image(self):
        for count,player in enumerate(self.game.players):
            if LEHRER[player.lehrer_name]["obstacle_richtungsabhaengig"]:
                richtung = self.orientation
                if self.is_begin:
                    richtung += "_begin"
                if self.is_end:
                    richtung += "_end"
                self.image[count] = LEHRER[player.lehrer_name]["richtungsabhaengige_bilder"][richtung]
            else:
                self.image[count] = PERSONEN_OBSTACLE_IMGES[player.lehrer_name]["img"]
            if LEHRER[player.lehrer_name]["obstacle_rotation"]:
                self.image[count] = pygame.transform.rotate(self.image[count], choice([0, 90, 180, 270, 360]))

class Personen_Object(pygame.sprite.Sprite):
    def __init__(self, game, x, y, w, h):
        self.groups = game.personen_objects, game.all_sprites
        pygame.sprite.Sprite.__init__(self, self.groups)
        self.name = "Personen Object"
        self.game = game
        self.rect = pygame.Rect(x, y, w, h)
        self.hit_rect = self.rect
        self.x = x
        self.y = y
        self.rect.x = x
        self.rect.y = y
        self.image = []
        for count,player in enumerate(self.game.players):
            self.image.append(PEROSNEN_OBJECT_IMGES[player.lehrer_name]["img"])
            if LEHRER[player.lehrer_name]["object_rotation"]:
                self.image[count] = pygame.transform.rotate(self.image[count], choice([0, 90, 180, 270, 360]))

    def update_image(self):
        for count,player in enumerate(self.game.players):
            self.image[count] = PEROSNEN_OBJECT_IMGES[player.lehrer_name]["img"]
            if LEHRER[player.lehrer_name]["object_rotation"]:
                self.image[count] = pygame.transform.rotate(self.image[count], choice([0, 90, 180, 270, 360]))

class Find_at_End(pygame.sprite.Sprite):
    def __init__(self, game, x, y):
        self.groups = game.all_sprites
        pygame.sprite.Sprite.__init__(self, self.groups)
        self.name = "Ding, das am Ende gefunden werden muss"
        self.game = game
        self.image = AT_END_IMG
        self.rect = self.image.get_rect()
        self.hit_rect = self.rect
        self.x = x
        self.y = y
        self.rect.centerx = self.x
        self.rect.centery = self.y
        self.last_width = self.rect.width
        self.getting_bigger = False  # False get smaller, true get bigger
        self.biggest = 1.25 * self.last_width
        self.smallest = 0.75 * self.last_width

        self.collected = False

    def update(self):
        if self.getting_bigger:
            new_width = self.last_width * 1.05
            if new_width > self.biggest:
                new_width = self.biggest
                self.getting_bigger = False
        else:
            new_width = self.last_width * 0.95
            if new_width < self.smallest:
                new_width = self.smallest
                self.getting_bigger = True
        self.image = pygame.transform.scale(AT_END_IMG, (int(new_width), int(new_width)))
        self.rect = self.image.get_rect()
        self.rect.centerx = self.x
        self.rect.centery = self.y
        self.last_width = new_width

class Health_Pack(pygame.sprite.Sprite):
    def __init__(self, game, pos):
        self._layer = ITEMS_LAYER
        self.groups = game.all_sprites, game.health_packs
        pygame.sprite.Sprite.__init__(self, self.groups)
        self.name = "Health Pack"
        self.game = game
        self.image = HEALTH_PACK_IMG
        self.rect = self.image.get_rect()
        self.pos = pos
        self.rect.center = pos
        self.tween = tween.easeInOutSine
        self.step = 0
        self.dir = 1

    def update(self):
        # hoch runter Bewegung
        offset = HEALTH_PACK_RANGE * (self.tween(self.step / HEALTH_PACK_RANGE) - 0.5)
        self.rect.centery = self.pos.y + offset * self.dir
        self.step += HEALTH_PACK_SPEED
        if self.step > HEALTH_PACK_RANGE:
            self.step = 0
            self.dir *= -1

class Gas_Wolke(pygame.sprite.Sprite):
    def __init__(self,game,image,start_size,end_size,pos,time_in_millis,time_stay_after_growing=0):
        self.groups = game.all_sprites
        self._layer = EFFECTS_LAYER
        pygame.sprite.Sprite.__init__(self, self.groups)
        self.name = "Gas Wolke"
        self.start_size = start_size
        self.orig_image = image
        self.image = pygame.transform.scale(image,start_size)
        self.rect = self.image.get_rect()
        self.rect.center = pos
        self.start_time = time() * 1000
        self.dauer = time_in_millis
        self.time_after_growing = time_stay_after_growing
        self.steigung_x = ((end_size[0] - start_size[0]) / (time_in_millis * 1.0))
        self.steigung_y = ((end_size[1] - start_size[1]) / (time_in_millis * 1.0))

    def update(self):
        zeit = time()*1000-self.start_time
        if zeit <= self.dauer:
            self.image = pygame.transform.scale(self.orig_image,(int(self.steigung_x*zeit+self.start_size[0]),int(self.steigung_y*zeit+self.start_size[1])))
            pos = self.rect.center
            self.rect = self.image.get_rect()
            self.rect.center = pos
        if zeit > self.dauer + self.time_after_growing:
            self.kill()

class Shaking_object(pygame.sprite.Sprite):
    def __init__(self,game,image,pos,time_in_millis):
        self.groups = game.all_sprites
        self._layer = WALL_LAYER
        pygame.sprite.Sprite.__init__(self, self.groups)
        self.name = "Shaking object"
        self.orig_image = image
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.center = pos
        self.start_time = time() * 1000
        self.dauer = time_in_millis

    def update(self):
        zeit = time()*1000-self.start_time
        self.image = pygame.transform.rotate(self.orig_image,18*sin(zeit/4))
        pos = self.rect.center
        self.rect = self.image.get_rect()
        self.rect.center = pos
        if zeit > self.dauer:
            self.kill()

class Spielhack(pygame.sprite.Sprite):
    def __init__(self,game,player,dauer_in_millis = 2000):
        self.groups = game.all_sprites
        self._layer = EFFECTS_LAYER
        pygame.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.name = "Spielhack"
        self.image = pygame.Surface((self.game.WIDTH,self.game.HEIGHT))
        self.image.set_colorkey(BLACK)
        self.image.convert()
        self.rect = self.image.get_rect()
        self.rect.center = player.pos
        self.start_time = time() * 1000
        self.dauer = dauer_in_millis

    def update(self):
        zeit = time() * 1000 - self.start_time
        if zeit%80 and int((zeit/self.dauer)*self.game.HEIGHT) <= self.game.HEIGHT:
            self.image.blit(LEHRER["Schüler"]["other_files"][choice(["eins","null"])],(randrange(0,self.game.WIDTH),int((zeit/self.dauer)*self.game.HEIGHT)))
        if int((zeit/self.dauer)*self.game.HEIGHT) > self.game.HEIGHT + 200:
            self.kill()