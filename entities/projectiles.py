# entities/projectiles.py

import pygame
from data.settings import *
from data.assets import load_image
from entities.base_sprite import BaseSprite


class Bracket(BaseSprite):
    def __init__(self, x, y, groups, damage):
        super().__init__(groups)
        self.damage = damage
        self.image = load_image('bracket.png', DEFAULT_COLORS['bracket'], (30, 30))
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = 10

    def update(self, *args, **kwargs):
        self.rect.x += self.speed
        if self.rect.left > SCREEN_WIDTH:
            self.kill()


class PaintSplat(Bracket):
    def __init__(self, x, y, groups, damage, artist):
        super().__init__(x, y, groups, damage)
        self.artist = artist
        self.image = load_image('paint_splat.png', DEFAULT_COLORS['paint_splat'], (30, 30))


class SoundWave(BaseSprite):
    def __init__(self, center, groups, damage, row_y, speed=5):
        super().__init__(groups)
        self.damage = damage
        self.image = pygame.Surface((20, CELL_SIZE_H - 10), pygame.SRCALPHA)
        self.image.fill(DEFAULT_COLORS['sound_wave'])
        self.rect = self.image.get_rect(center=center)
        self.row_y = row_y
        self.speed = speed
        self.hit_enemies = set()
        self.spawn_time = pygame.time.get_ticks()
        self.lifetime = 2000

    def update(self, *args, **kwargs):
        self.rect.x += self.speed
        if pygame.time.get_ticks() - self.spawn_time > self.lifetime or self.rect.left > SCREEN_WIDTH:
            self.kill()


class Integral(Bracket):
    def __init__(self, x, y, groups, damage):
        super().__init__(x, y, groups, damage)
        self.image = load_image('integral.png', DEFAULT_COLORS['integral'], (30, 30))
        self.speed = -5