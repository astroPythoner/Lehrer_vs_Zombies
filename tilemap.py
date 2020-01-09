import pygame as pg
import pytmx
from constants import *

def collide_hit_rect(one, two):
    return one.hit_rect.colliderect(two.rect)

class Map:
    def __init__(self, filename):
        self.data = []
        with open(filename, 'rt') as f:
            for line in f:
                self.data.append(line.strip())

        self.tilewidth = len(self.data[0])
        self.tileheight = len(self.data)
        self.width = self.tilewidth * TILESIZE
        self.height = self.tileheight * TILESIZE

class TiledMap:
    def __init__(self, filename):
        tm = pytmx.load_pygame(filename, pixelalpha=True)
        self.width = tm.width * tm.tilewidth
        self.height = tm.height * tm.tileheight
        self.tmxdata = tm

    def render(self, surface):
        ti = self.tmxdata.get_tile_image_by_gid
        for layer in self.tmxdata.visible_layers:
            if isinstance(layer, pytmx.TiledTileLayer):
                for x, y, gid, in layer:
                    tile = ti(gid)
                    if tile:
                        surface.blit(tile, (x * self.tmxdata.tilewidth,
                                            y * self.tmxdata.tileheight))

    def make_map(self):
        temp_surface = pg.Surface((self.width, self.height))
        self.render(temp_surface)
        return temp_surface

class Camera:
    def __init__(self, map_width, map_height, game):
        self.camera = pg.Rect(0, 0, map_width, map_height)
        self.inverted = pg.Rect(0, 0, map_width, map_height)
        self.player_umgebung = pg.Rect(0, 0, map_width, map_height)
        self.map_width = map_width
        self.map_height = map_height
        self.game = game

    def apply(self, entity):
        return entity.rect.move(self.camera.topleft)

    def apply_rect(self, rect):
        return rect.move(self.camera.topleft)

    def update(self, target):
        x = -target.rect.centerx + int(self.game.WIDTH/len(self.game.players) / 2)
        y = -target.rect.centery + int(self.game.HEIGHT / 2)
        umgebung_x = -target.rect.centerx + int(self.game.small_map_sichtweite / 2)
        umgebung_y = -target.rect.centery + int(self.game.small_map_sichtweite / 2)

        # limit scrolling to map size
        x = min(0, x)  # left
        y = min(0, y)  # top
        x = max(-(self.map_width - self.game.WIDTH/len(self.game.players)), x)  # right
        y = max(-(self.map_height - self.game.HEIGHT), y)  # bottom
        umgebung_x = min(0, umgebung_x)  # left
        umgebung_y = min(0, umgebung_y)  # top
        umgebung_x = max(-(self.map_width - self.game.small_map_sichtweite), umgebung_x)  # right
        umgebung_y = max(-(self.map_height - self.game.small_map_sichtweite), umgebung_y)  # bottom

        # Rects
        self.camera = pg.Rect(x, y, self.map_width, self.map_height)
        self.inverted = pg.Rect(-x,-y, self.map_width, self.map_height)
        self.player_umgebung = pg.Rect(-umgebung_x,-umgebung_y, self.map_width, self.map_height)
