# entities/projectiles.py

import pygame
from data.settings import *
from data.assets import load_image
from entities.base_sprite import BaseSprite


class Bracket(BaseSprite):
    def __init__(self, x, y, groups, damage, image):
        super().__init__(groups)
        self.damage = damage
        self.image = image
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = BRACKET_PROJECTILE_SPEED
        self.target_type = 'enemy'

    def update(self, *args, **kwargs):
        self.rect.x += self.speed
        if self.rect.left > SCREEN_WIDTH:
            self.kill()


class PaintSplat(Bracket):
    def __init__(self, x, y, groups, damage, artist):
        splat_image = load_image('projectiles/paint_splat.png', DEFAULT_COLORS['paint_splat'], (30, 30))
        super().__init__(x, y, groups, damage, splat_image)
        self.artist = artist


class SoundWave(BaseSprite):
    def __init__(self, center, groups, damage, row_y, speed=SOUNDWAVE_PROJECTILE_SPEED):
        super().__init__(groups)
        self.damage = damage
        self.image = load_image('projectiles/sound_wave.png', DEFAULT_COLORS['sound_wave'], (40, CELL_SIZE_H - 10))
        self.rect = self.image.get_rect(center=center)
        self.row_y = row_y
        self.speed = speed
        self.hit_enemies = set()
        self.spawn_time = pygame.time.get_ticks()
        self.lifetime = SOUNDWAVE_LIFETIME

    def update(self, **kwargs):
        self.rect.x += self.speed
        if pygame.time.get_ticks() - self.spawn_time > self.lifetime or self.rect.left > SCREEN_WIDTH:
            self.kill()


class Integral(Bracket):
    def __init__(self, x, y, groups, damage, image):
        super().__init__(x, y, groups, damage, image)
        self.speed = INTEGRAL_PROJECTILE_SPEED
        self.target_type = 'defender'

    def update(self, *args, **kwargs):
        self.rect.x += self.speed
        if self.rect.right < 0:
            self.kill()