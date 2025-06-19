# ui/base_component.py

import pygame
from data.settings import *


class BaseUIComponent:
    """
    Базовый класс для всех компонентов пользовательского интерфейса.
    Содержит общие ресурсы (шрифты) и утилитарные методы отрисовки.
    """

    def __init__(self, screen):
        self.screen = screen
        self.fonts = {
            'default': pygame.font.SysFont(FONT_FAMILY_DEFAULT, FONT_SIZE_NORMAL),
            'small': pygame.font.SysFont(FONT_FAMILY_DEFAULT, FONT_SIZE_SMALL),
            'small_bold': pygame.font.SysFont(FONT_FAMILY_DEFAULT, FONT_SIZE_SMALL, bold=True),
            'tiny': pygame.font.SysFont(FONT_FAMILY_DEFAULT, FONT_SIZE_TINY),
            'large': pygame.font.SysFont(FONT_FAMILY_DEFAULT, FONT_SIZE_LARGE),
            'huge': pygame.font.SysFont(FONT_FAMILY_IMPACT, FONT_SIZE_HUGE),
            'title': pygame.font.SysFont(FONT_FAMILY_TITLE, FONT_SIZE_TITLE)
        }

    def _render_text_wrapped(self, text, font, color, max_width):
        """
        Отрисовывает текст с переносом по словам, если он не помещается в max_width.
        Возвращает список поверхностей (surfaces) с каждой строкой текста.
        """
        words = text.split(WORD_SEPARATOR)
        lines = []
        current_line = ""
        for word in words:
            test_line = f"{current_line}{word}{WORD_SEPARATOR}"
            if font.size(test_line)[0] < max_width:
                current_line = test_line
            else:
                lines.append(font.render(current_line, True, color))
                current_line = f"{word}{WORD_SEPARATOR}"

        # Добавляем последнюю или единственную строку
        lines.append(font.render(current_line, True, color))
        return lines

    def _draw_button(self, surface, text, rect, color, text_color, font=None, border_color=WHITE,
                     border_width=DEFAULT_BORDER_WIDTH):
        """Универсальная функция для отрисовки кнопки с текстом."""
        if font is None:
            font = self.fonts['default']

        pygame.draw.rect(surface, color, rect, border_radius=DEFAULT_BORDER_RADIUS)
        pygame.draw.rect(surface, border_color, rect, border_width, border_radius=DEFAULT_BORDER_RADIUS)

        text_surf = font.render(text, True, text_color)
        surface.blit(text_surf, text_surf.get_rect(center=rect.center))

    def _draw_panel_with_title(self, surface, rect, title, title_font=None, title_color=WHITE, panel_color=None,
                               border_color=WHITE):
        """Отрисовывает панель с заголовком."""
        if title_font is None:
            title_font = self.fonts['default']
        if panel_color is None:
            panel_color = DEFAULT_COLORS['shop_panel']

        pygame.draw.rect(surface, panel_color, rect, border_radius=SETTINGS_BORDER_RADIUS)
        pygame.draw.rect(surface, border_color, rect, THICK_BORDER_WIDTH, border_radius=SETTINGS_BORDER_RADIUS)

        title_surf = title_font.render(title, True, title_color)
        title_rect = title_surf.get_rect(centerx=rect.centerx, top=rect.top + PREP_TEAM_PANEL_TITLE_TOP_OFFSET)
        surface.blit(title_surf, title_rect)

    def _render_text_with_title(self, surface, text, font, color, center_x, top_y):
        """Отрисовывает центрированный текст."""
        text_surf = font.render(text, True, color)
        surface.blit(text_surf, text_surf.get_rect(centerx=center_x, top=top_y))