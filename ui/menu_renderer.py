# ui/menu_renderer.py

import pygame
from data.settings import *
from ui.base_component import BaseUIComponent


class MenuRenderer(BaseUIComponent):
    """Отвечает за отрисовку простых полноэкранных меню (пауза, победа, поражение)."""

    def __init__(self, screen):
        super().__init__(screen)

    def draw(self, surface, title_text, buttons):
        """
        Отрисовывает универсальное меню с затемнением, заголовком и кнопками.

        Args:
            surface (pygame.Surface): Поверхность для отрисовки.
            title_text (str): Текст заголовка меню.
            buttons (dict): Словарь { 'имя_кнопки': pygame.Rect }.
        """
        # Затемняющий оверлей
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, MENU_OVERLAY_ALPHA))
        surface.blit(overlay, (0, 0))

        # Заголовок
        title = self.fonts['large'].render(title_text, True, WHITE)
        title_rect = title.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 4))
        surface.blit(title, title_rect)

        # Кнопки
        for name, rect in buttons.items():
            self._draw_button(surface, name, rect, DEFAULT_COLORS['button'], WHITE, self.fonts['default'])

    def draw_level_clear_message(self, surface):
        """
        Отрисовывает большое сообщение "БРС: 100/100" по центру экрана.

        Args:
            surface (pygame.Surface): Поверхность для отрисовки.
        """
        text = "БРС: 100/100"
        font = self.fonts['huge']
        text_surf = font.render(text, True, YELLOW)
        shadow_surf = font.render(text, True, BLACK)

        # Рисуем тень со смещением
        shadow_rect = shadow_surf.get_rect(center=(SCREEN_WIDTH / 2 + 5, SCREEN_HEIGHT / 2 + 5))
        surface.blit(shadow_surf, shadow_rect)

        # Рисуем основной текст поверх тени
        text_rect = text_surf.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2))
        surface.blit(text_surf, text_rect)