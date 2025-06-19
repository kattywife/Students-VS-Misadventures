# entities/base_sprite.py

import pygame
from data.settings import *
from data.assets import load_image


class BaseSprite(pygame.sprite.Sprite):
    """
    Базовый класс для всех игровых спрайтов.
    Наследуется от `pygame.sprite.Sprite` и добавляет общую функциональность,
    такую как `_layer` для корректной отрисовки в `LayeredUpdates`.
    """
    def __init__(self, *groups):
        """
        Инициализирует базовый спрайт.

        Args:
            *groups: Группы спрайтов, в которые нужно добавить этот спрайт.
        """
        super().__init__(*groups)
        # Время последнего обновления, может использоваться дочерними классами для таймеров.
        self.last_update = pygame.time.get_ticks()
        # Определяем слой для отрисовки. Спрайты с большим значением _layer рисуются поверх.
        # `self.rect.bottom` обеспечивает эффект псевдо-3D: те, кто ниже на экране, кажутся ближе.
        self._layer = self.rect.bottom if hasattr(self, 'rect') else 4

    def draw(self, surface):
        """
        Стандартный метод отрисовки спрайта на поверхности.
        Примечание: в текущей реализации игры этот метод не используется,
        так как отрисовка происходит через `all_sprites.draw(screen)`.
        """
        surface.blit(self.image, self.rect)


class ExplosionEffect(BaseSprite):
    """
    Класс для визуального эффекта взрыва.
    Появляется, существует короткое время и исчезает.
    Используется, например, Модником.
    """
    def __init__(self, center, radius, *groups):
        """
        Инициализирует эффект взрыва.

        Args:
            center (tuple): Координаты центра взрыва (x, y).
            radius (int): Радиус взрыва в пикселях.
            *groups: Группы спрайтов для добавления эффекта.
        """
        super().__init__(*groups)
        self.radius = radius
        # Загружаем изображение и масштабируем его до диаметра взрыва
        self.image = load_image('projectiles/explosion.png', DEFAULT_COLORS['explosion'], (self.radius * 2, self.radius * 2))
        self.rect = self.image.get_rect(center=center)
        self.spawn_time = pygame.time.get_ticks()
        self.lifetime = EXPLOSION_LIFETIME # Время жизни эффекта из настроек

    def update(self, *args, **kwargs):
        """
        Обновляет состояние эффекта. Если время жизни истекло, уничтожает спрайт.
        """
        if pygame.time.get_ticks() - self.spawn_time > self.lifetime:
            self.kill()


class BookAttackEffect(BaseSprite):
    """
    Класс для визуального эффекта атаки Девочки-ботана.
    Представляет собой полупрозрачный круг, обозначающий область поражения.
    """
    def __init__(self, center_pos, groups, diameter):
        """
        Инициализирует эффект атаки.

        Args:
            center_pos (tuple): Координаты центра эффекта (x, y).
            groups: Группы спрайтов для добавления эффекта.
            diameter (int): Диаметр круга атаки в пикселях.
        """
        super().__init__(groups)
        self.image = load_image('projectiles/book_attack.png', DEFAULT_COLORS['book_attack'], (diameter, diameter))
        self.image.set_alpha(150) # Делаем эффект полупрозрачным
        self.rect = self.image.get_rect(center=center_pos)
        self.spawn_time = pygame.time.get_ticks()
        self.lifetime = BOOK_ATTACK_LIFETIME # Время жизни эффекта из настроек

    def update(self, *args, **kwargs):
        """
        Обновляет состояние эффекта. Если время жизни истекло, уничтожает спрайт.
        """
        if pygame.time.get_ticks() - self.spawn_time > self.lifetime:
            self.kill()