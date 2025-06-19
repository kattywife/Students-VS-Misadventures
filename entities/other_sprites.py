# entities/other_sprites.py

import pygame
import os
from data.settings import *
from data.assets import load_image
from entities.base_sprite import BaseSprite


class CoffeeBean(BaseSprite):
    """
    Класс для спрайта кофейного зерна.
    Зерна создаются Кофемашиной, их можно собирать кликом мыши,
    чтобы получить ресурс "кофе". Исчезают со временем.
    """
    def __init__(self, x, y, groups, value):
        """
        Инициализирует кофейное зерно.

        Args:
            x (int): Начальная координата X.
            y (int): Начальная координата Y.
            groups (tuple): Группы спрайтов для добавления.
            value (int): Количество кофе, которое дает зерно при сборе.
        """
        super().__init__(groups)
        self.value = value
        path_to_image = os.path.join('resources', 'coffee_bean.png')
        self.image = load_image(path_to_image, DEFAULT_COLORS['coffee_bean'], (40, 40))
        self.rect = self.image.get_rect(center=(x, y))
        self._layer = self.rect.bottom + 1 # Рисуется поверх большинства спрайтов
        self.spawn_time = pygame.time.get_ticks()
        self.lifetime = COFFEE_BEAN_LIFETIME

    def update(self, *args, **kwargs):
        """Обновляет состояние зерна. Если время жизни истекло, уничтожает спрайт."""
        if pygame.time.get_ticks() - self.spawn_time > self.lifetime:
            self.kill()


class AuraEffect(BaseSprite):
    """
    Визуальный эффект ауры, привязанный к родительскому спрайту.
    Используется Активистом для отображения радиуса действия его способности.
    """
    def __init__(self, groups, parent):
        """
        Инициализирует эффект ауры.

        Args:
            groups (tuple): Группы спрайтов для добавления.
            parent (pygame.sprite.Sprite): Спрайт-носитель ауры (например, Активист).
        """
        super().__init__()
        self.parent = parent
        self.groups_tuple = groups
        self.radius = self.parent.data['radius']
        self.animations = []
        self.load_animations()
        self.frame_index = 0
        self.image = self.animations[0] if self.animations else pygame.Surface((0, 0))
        self.rect = self.image.get_rect(center=self.parent.rect.center)
        self.anim_speed = AURA_ANIMATION_SPEED
        self.last_anim_update = pygame.time.get_ticks()
        self._layer = self.parent._layer - 1 # Рисуется под своим родителем
        self.add(self.groups_tuple)

    def load_animations(self):
        """Загружает анимированные кадры ауры."""
        pixel_radius = self.radius * CELL_SIZE_W
        size = (pixel_radius * 2, pixel_radius * 2)
        path = os.path.join(IMAGES_DIR, 'effects', 'activist_aura')
        if os.path.exists(path):
            filenames = sorted([f for f in os.listdir(path) if f.startswith('aura_') and f.endswith('.png')])
            for filename in filenames:
                img_path = os.path.join('effects', 'activist_aura', filename)
                self.animations.append(load_image(img_path, (0, 0, 0, 0), size))
        # Резервный вариант, если анимации не найдены
        if not self.animations:
            fallback_surface = pygame.Surface(size, pygame.SRCALPHA)
            fallback_surface.fill((0, 0, 0, 0))
            self.animations.append(fallback_surface)

    def update(self, *args, **kwargs):
        """Обновляет состояние ауры: следует за родителем и анимируется."""
        # Если родительский спрайт уничтожен, аура тоже уничтожается
        if not self.parent.alive():
            self.kill()
            return

        if not self.animations:
            return

        # Анимация
        now = pygame.time.get_ticks()
        if now - self.last_anim_update > self.anim_speed * 1000:
            self.last_anim_update = now
            self.frame_index = (self.frame_index + 1) % len(self.animations)
            self.image = self.animations[self.frame_index]

        # Синхронизация позиции и слоя с родителем
        self.rect.center = self.parent.rect.center
        new_layer = self.parent._layer - 1
        if self._layer != new_layer:
            # Передобавление в группу для обновления слоя в LayeredUpdates
            self.remove(self.groups_tuple)
            self._layer = new_layer
            self.add(self.groups_tuple)


class CalamityAuraEffect(BaseSprite):
    """
    Визуальный эффект ауры, который появляется у врагов во время "напастей".
    Это статичный спрайт, который следует за своим родителем.
    """
    def __init__(self, groups, parent, calamity_type):
        """
        Инициализирует ауру напасти.

        Args:
            groups (tuple): Группы спрайтов для добавления.
            parent (Enemy): Спрайт врага-носителя ауры.
            calamity_type (str): Тип напасти для загрузки соответствующей картинки.
        """
        super().__init__()
        self.parent = parent
        self.groups_tuple = groups
        path = os.path.join('effects', f'{calamity_type}_aura.png')
        size = (CELL_SIZE_W + 10, CELL_SIZE_H + 20)
        self.image = load_image(path, (0, 0, 0, 0), size)
        self.rect = self.image.get_rect(center=self.parent.rect.center)
        self._layer = self.parent._layer - 1 # Рисуется под родителем
        self.add(self.groups_tuple)

    def update(self, *args, **kwargs):
        """Обновляет состояние ауры, следуя за родителем."""
        if not self.parent.alive():
            self.kill()
            return
        # Синхронизация позиции и слоя
        self.rect.center = self.parent.rect.center
        new_layer = self.parent._layer - 1
        if self._layer != new_layer:
            self.remove(self.groups_tuple)
            self._layer = new_layer
            self.add(self.groups_tuple)


class NeuroMower(BaseSprite):
    """
    Класс для "газонокосилок" - нейросетей последнего рубежа обороны.
    Размещаются на экране подготовки, активируются при контакте с врагом.
    """
    def __init__(self, row, groups, mower_type, sound_manager):
        """
        Инициализирует нейросеть.

        Args:
            row (int): Ряд, на котором размещена нейросеть.
            groups (tuple): Группы спрайтов для добавления.
            mower_type (str): Тип нейросети ('chat_gpt', 'deepseek', 'gemini').
            sound_manager (SoundManager): Менеджер звуков.
        """
        super().__init__(groups)
        self.sound_manager = sound_manager
        self.mower_type = mower_type
        self.data = NEURO_MOWERS_DATA[mower_type]
        self.image = load_image(f'systems/{mower_type}.png', DEFAULT_COLORS[mower_type],
                                (CELL_SIZE_W - 20, CELL_SIZE_H - 20))
        y = GRID_START_Y + row * CELL_SIZE_H + CELL_SIZE_H / 2
        # Размещается слева от игровой сетки
        self.rect = self.image.get_rect(center=(GRID_START_X - CELL_SIZE_W / 2, y))
        self.is_active = False
        self.speed = NEURO_MOWER_CHAT_GPT_SPEED

    def activate(self, enemies_group, activator):
        """
        Активирует нейросеть. Логика зависит от типа.

        Args:
            enemies_group (pygame.sprite.Group): Группа всех врагов на поле.
            activator (Enemy): Враг, который вызвал активацию.
        """
        if self.is_active: return
        self.is_active = True
        self.sound_manager.play_sfx('tuning')

        # Нейросети с мгновенным эффектом
        if self.mower_type == 'deepseek':
            # Находит 3 самых близких к базе врагов и уничтожает их
            targets = sorted(list(enemies_group), key=lambda e: e.rect.left)[:NEURO_MOWER_DEEPSEEK_TARGET_COUNT]
            for enemy in targets:
                enemy.kill()
        elif self.mower_type == 'gemini':
            # Находит 4 самых "жирных" врагов и уничтожает их
            targets = sorted(list(enemies_group), key=lambda e: e.health, reverse=True)[
                      :NEURO_MOWER_GEMINI_TARGET_COUNT]
            for enemy in targets:
                enemy.kill()

        # Уничтожаем врага, который активировал нейросеть
        if activator.alive():
            activator.kill()

    def update(self, *args, **kwargs):
        """Обновляет состояние нейросети. Логика зависит от типа."""
        # 'chat_gpt' движется вправо после активации, уничтожая врагов на пути
        if self.is_active and self.mower_type == 'chat_gpt':
            self.rect.x += self.speed
            if self.rect.left > SCREEN_WIDTH:
                self.kill()

            enemies_on_line = kwargs.get('enemies_group')
            if enemies_on_line:
                # Уничтожаем всех врагов, с которыми столкнулись
                pygame.sprite.spritecollide(self, enemies_on_line, True)

        # Другие типы нейросетей уничтожаются сразу после активации
        elif self.is_active and self.mower_type != 'chat_gpt':
            self.kill()