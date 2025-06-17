# entities/other_sprites.py

import pygame
from data.settings import *
from data.assets import load_image
from entities.base_sprite import BaseSprite
import os


class CoffeeBean(BaseSprite):
    def __init__(self, x, y, groups, value):
        super().__init__(groups)
        self.value = value
        path_to_image = os.path.join('resources', 'coffee_bean.png')
        self.image = load_image(path_to_image, DEFAULT_COLORS['coffee_bean'], (40, 40))
        self.rect = self.image.get_rect(center=(x, y))
        self._layer = self.rect.bottom + 1
        self.spawn_time = pygame.time.get_ticks()
        self.lifetime = 8000

    def update(self, *args, **kwargs):
        if pygame.time.get_ticks() - self.spawn_time > self.lifetime:
            self.kill()


class AuraEffect(BaseSprite):
    def __init__(self, groups, parent):
        super().__init__(groups)
        self.parent = parent
        self.radius = self.parent.data['radius']

        self.animations = []
        self.load_animations()

        self.frame_index = 0
        self.image = self.animations[0]
        self.rect = self.image.get_rect(center=self.parent.rect.center)

        self.anim_speed = 0.1  # Скорость анимации
        self.last_anim_update = pygame.time.get_ticks()
        self._layer = self.parent._layer - 1  # Рисуем ауру под родителем

    def load_animations(self):
        size = (self.radius * 2, self.radius * 2)
        # Предполагаем, что есть 3 кадра анимации. Если у тебя больше/меньше, измени цифру в range(3)
        for i in range(3):
            path = os.path.join('effects', 'activist_aura', f'aura_{i}.png')
            img = load_image(path, (0, 0, 0, 0), size)
            self.animations.append(img)

    def update(self, *args, **kwargs):
        # Если родитель (Активист) исчез, аура тоже исчезает
        if not self.parent.alive():
            self.kill()
            return

        # Анимация
        now = pygame.time.get_ticks()
        if now - self.last_anim_update > self.anim_speed * 1000:
            self.last_anim_update = now
            self.frame_index = (self.frame_index + 1) % len(self.animations)
            self.image = self.animations[self.frame_index]

        # Аура всегда следует за своим родителем
        self.rect.center = self.parent.rect.center


class NeuroMower(BaseSprite):
    def __init__(self, row, groups, mower_type):
        super().__init__(groups)
        self.mower_type = mower_type
        self.data = NEURO_MOWERS_DATA[mower_type]
        self.image = load_image(f'systems/{mower_type}.png', DEFAULT_COLORS[mower_type],
                                (CELL_SIZE_W - 20, CELL_SIZE_H - 20))
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