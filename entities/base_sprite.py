# entities/base_sprite.py

import pygame
from data.settings import *
from data.assets import load_image, SOUNDS


class BaseSprite(pygame.sprite.Sprite):
    def __init__(self, *groups):
        super().__init__(*groups)
        self.last_update = pygame.time.get_ticks()
        self._layer = self.rect.bottom if hasattr(self, 'rect') else 4

    def draw(self, surface):
        surface.blit(self.image, self.rect)


class ExplosionEffect(BaseSprite):
    def __init__(self, center, radius, *groups):
        super().__init__(*groups)
        self.radius = radius
        self.image = load_image('projectiles/explosion.png', DEFAULT_COLORS['explosion'], (self.radius * 2, self.radius * 2))
        self.rect = self.image.get_rect(center=center)
        self.spawn_time = pygame.time.get_ticks()
        self.lifetime = 300 # 300 миллисекунд

    def update(self, *args, **kwargs):
        if pygame.time.get_ticks() - self.spawn_time > self.lifetime:
            self.kill()


class BookAttackEffect(BaseSprite):
    def __init__(self, center_pos, groups, diameter):
        super().__init__(groups)
        self.image = load_image('projectiles/book_attack.png', DEFAULT_COLORS['book_attack'], (diameter, diameter))
        self.image.set_alpha(150)
        self.rect = self.image.get_rect(center=center_pos)
        self.spawn_time = pygame.time.get_ticks()
        self.lifetime = 200 # 200 миллисекунд

    def update(self, *args, **kwargs):
        if pygame.time.get_ticks() - self.spawn_time > self.lifetime:
            self.kill()