# entities/other_sprites.py

import pygame
from data.settings import *
from data.assets import load_image
from entities.base_sprite import BaseSprite


class CoffeeBean(BaseSprite):
    def __init__(self, x, y, groups, value):
        super().__init__(groups)
        self.value = value
        self.image = load_image('coffee_bean.png', DEFAULT_COLORS['coffee_bean'], (40, 40))
        self.rect = self.image.get_rect(center=(x, y))
        self.spawn_time = pygame.time.get_ticks()
        self.lifetime = 8000

    def update(self, *args, **kwargs):
        if pygame.time.get_ticks() - self.spawn_time > self.lifetime:
            self.kill()


class NeuroMower(BaseSprite):
    def __init__(self, row, groups, mower_type):
        super().__init__(groups)
        self.mower_type = mower_type
        self.data = NEURO_MOWERS_DATA[mower_type]
        self.image = load_image(f'{mower_type}.png', DEFAULT_COLORS[mower_type], (CELL_SIZE_W - 20, CELL_SIZE_H - 20))
        y = GRID_START_Y + row * CELL_SIZE_H + CELL_SIZE_H / 2
        self.rect = self.image.get_rect(center=(GRID_START_X - CELL_SIZE_W / 2, y))
        self.is_active = False
        self.speed = 12

    def activate(self, enemies_group):
        if self.is_active: return
        self.is_active = True

        if self.mower_type == 'deepseek':
            for enemy in sorted(list(enemies_group), key=lambda e: e.rect.left)[:3]:
                enemy.kill()
        elif self.mower_type == 'gemini':
            for enemy in sorted(list(enemies_group), key=lambda e: e.health, reverse=True)[:4]:
                enemy.kill()

    def update(self, *args, **kwargs):
        if self.is_active and self.mower_type == 'chat_gpt':
            self.rect.x += self.speed
            if self.rect.left > SCREEN_WIDTH:
                self.kill()

            enemies_on_line = kwargs.get('enemies_group')
            if enemies_on_line:
                pygame.sprite.spritecollide(self, enemies_on_line, True)

        elif self.is_active and self.mower_type != 'chat_gpt':
            self.kill()