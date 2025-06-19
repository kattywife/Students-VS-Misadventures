# entities/projectiles.py

import pygame
from data.settings import *
from data.assets import load_image
from entities.base_sprite import BaseSprite


class Bracket(BaseSprite):
    """
    Базовый класс для простых, прямолинейно летящих снарядов.
    Изначально представляет снаряд Программиста.
    Движется слева направо.
    """
    def __init__(self, x, y, groups, damage, image):
        """
        Инициализирует снаряд.

        Args:
            x (int): Начальная координата X.
            y (int): Начальная координата Y.
            groups (tuple): Группы спрайтов для добавления.
            damage (int): Урон, наносимый снарядом.
            image (pygame.Surface): Изображение снаряда.
        """
        super().__init__(groups)
        self.damage = damage
        self.image = image
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = BRACKET_PROJECTILE_SPEED
        self.target_type = 'enemy' # Указывает, что цель - враг

    def update(self, *args, **kwargs):
        """Двигает снаряд вправо и уничтожает его за пределами экрана."""
        self.rect.x += self.speed
        if self.rect.left > SCREEN_WIDTH:
            self.kill()


class PaintSplat(Bracket):
    """
    Снаряд-клякса, выпускаемый Художницей.
    Наследуется от Bracket, но имеет особое изображение и несет в себе
    ссылку на своего создателя, чтобы применить эффект замедления.
    """
    def __init__(self, x, y, groups, damage, artist):
        """
        Инициализирует кляксу.

        Args:
            x (int): Начальная координата X.
            y (int): Начальная координата Y.
            groups (tuple): Группы спрайтов.
            damage (int): Урон.
            artist (Artist): Ссылка на спрайт Художницы, создавшей кляксу.
        """
        splat_image = load_image('projectiles/paint_splat.png', DEFAULT_COLORS['paint_splat'], (30, 30))
        super().__init__(x, y, groups, damage, splat_image)
        self.artist = artist


class SoundWave(BaseSprite):
    """
    Проникающий снаряд, выпускаемый Гитаристом.
    Не уничтожается при первом столкновении, а продолжает лететь,
    нанося урон всем врагам на своем пути.
    """
    def __init__(self, center, groups, damage, row_y, speed=SOUNDWAVE_PROJECTILE_SPEED):
        """
        Инициализирует звуковую волну.

        Args:
            center (tuple): Начальные координаты центра.
            groups (tuple): Группы спрайтов.
            damage (int): Урон.
            row_y (int): Y-координата центра линии, по которой летит волна.
            speed (int, optional): Скорость движения.
        """
        super().__init__(groups)
        self.damage = damage
        self.image = load_image('projectiles/sound_wave.png', DEFAULT_COLORS['sound_wave'], (40, CELL_SIZE_H - 10))
        self.rect = self.image.get_rect(center=center)
        self.row_y = row_y
        self.speed = speed
        # Множество для хранения врагов, которым уже был нанесен урон,
        # чтобы избежать повторного урона за один "пролет".
        self.hit_enemies = set()
        self.spawn_time = pygame.time.get_ticks()
        self.lifetime = SOUNDWAVE_LIFETIME

    def update(self, **kwargs):
        """Двигает волну и уничтожает ее по истечении времени жизни или за экраном."""
        self.rect.x += self.speed
        if pygame.time.get_ticks() - self.spawn_time > self.lifetime or self.rect.left > SCREEN_WIDTH:
            self.kill()


class Integral(Bracket):
    """
    Снаряд, выпускаемый врагом "Матанализ".
    Наследуется от Bracket, но движется справа налево и нацелен на защитников.
    """
    def __init__(self, x, y, groups, damage, image):
        """
        Инициализирует снаряд-интеграл.

        Args:
            x (int): Начальная координата X.
            y (int): Начальная координата Y.
            groups (tuple): Группы спрайтов.
            damage (int): Урон.
            image (pygame.Surface): Изображение снаряда.
        """
        super().__init__(x, y, groups, damage, image)
        self.speed = INTEGRAL_PROJECTILE_SPEED # Скорость отрицательная
        self.target_type = 'defender' # Цель - защитник

    def update(self, *args, **kwargs):
        """Двигает снаряд влево и уничтожает его за пределами экрана."""
        self.rect.x += self.speed
        if self.rect.right < 0:
            self.kill()