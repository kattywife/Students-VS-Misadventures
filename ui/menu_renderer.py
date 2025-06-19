# ui/menu_renderer.py

import pygame
from data.settings import *
from .base_component import BaseUIComponent


class MenuRenderer(BaseUIComponent):
    """Отвечает за отрисовку простых полноэкранных меню (пауза, победа, поражение)."""

    def __init__(self, screen):
        super().__init__(screen)

    def draw(self, surface, title_text, buttons):
        """Отрисовывает универсальное меню с затемнением, заголовком и кнопками."""
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, MENU_OVERLAY_ALPHA))
        surface.blit(overlay, (0, 0))

        title = self.fonts['large'].render(title_text, True, WHITE)
        title_rect = title.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 4))
        surface.blit(title, title_rect)

        for name, rect in buttons.items():
            self._draw_button(surface, name, rect, DEFAULT_COLORS['button'], WHITE, self.fonts['default'])

    def draw_level_clear_message(self, surface):
        """Отрисовывает большое сообщение "БРС: 100/100" по центру экрана."""
        text = "БРС: 100/100"
        font = self.fonts['huge']
        text_surf = font.render(text, True, YELLOW)
        shadow_surf = font.render(text, True, BLACK)

        shadow_offset = LEVEL_CLEAR_SHADOW_OFFSET
        shadow_rect = shadow_surf.get_rect(center=(SCREEN_WIDTH / 2 + shadow_offset, SCREEN_HEIGHT / 2 + shadow_offset))
        surface.blit(shadow_surf, shadow_rect)

        text_rect = text_surf.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2))
        surface.blit(text_surf, text_rect)