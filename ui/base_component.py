# ui/base_component.py

import pygame
from data.settings import *


class BaseUIComponent:
    """
    Базовый класс для всех компонентов пользовательского интерфейса.
    Содержит общие ресурсы (шрифты) и утилитарные методы отрисовки,
    которые используются его дочерними классами. Это помогает избежать
    дублирования кода (принцип DRY) и обеспечивает единообразный вид
    элементов UI.
    """

    def __init__(self, screen):
        """
        Инициализирует компонент UI.

        Также инициализирует и кэширует словарь `self.fonts` с различными
        размерами и стилями шрифтов для повышения производительности.

        Args:
            screen (pygame.Surface): Основная поверхность для отрисовки.
        """
        self.screen = screen
        # Кэшируем шрифты при инициализации, чтобы не создавать их в игровом цикле.
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
        Отрисовывает текст с автоматическим переносом по словам.

        Если строка текста превышает `max_width`, она разбивается на несколько
        строк. Метод не рисует на экране, а подготавливает строки для
        последующей отрисовки.

        Args:
            text (str): Входной текст для отрисовки.
            font (pygame.font.Font): Шрифт, который будет использоваться.
            color (tuple): Цвет текста в формате RGB.
            max_width (int): Максимальная ширина строки в пикселях.

        Returns:
            list[pygame.Surface]: Список поверхностей `pygame.Surface`, где каждая
                                  поверхность представляет собой одну строку текста.
        """
        words = text.split(WORD_SEPARATOR)
        lines = []
        current_line = ""
        for word in words:
            # Проверяем, поместится ли следующее слово в текущую строку
            test_line = f"{current_line}{word}{WORD_SEPARATOR}"
            if font.size(test_line)[0] < max_width:
                current_line = test_line
            else:
                # Если не помещается, завершаем текущую строку и начинаем новую
                lines.append(font.render(current_line, True, color))
                current_line = f"{word}{WORD_SEPARATOR}"

        # Добавляем последнюю или единственную строку
        lines.append(font.render(current_line, True, color))
        return lines

    def _draw_button(self, surface, text, rect, color, text_color, font=None, border_color=WHITE,
                     border_width=DEFAULT_BORDER_WIDTH):
        """
        Универсальная функция для отрисовки кнопки с текстом.
        Рисует прямоугольник-фон, рамку и центрированный текст.

        Args:
            surface (pygame.Surface): Поверхность, на которой будет нарисована кнопка.
            text (str): Текст на кнопке.
            rect (pygame.Rect): Прямоугольник, определяющий положение и размер кнопки.
            color (tuple): Цвет фона кнопки.
            text_color (tuple): Цвет текста.
            font (pygame.font.Font, optional): Шрифт для текста. По умолчанию 'default'.
            border_color (tuple, optional): Цвет рамки. По умолчанию WHITE.
            border_width (int, optional): Толщина рамки. По умолчанию DEFAULT_BORDER_WIDTH.
        """
        if font is None:
            font = self.fonts['default']

        pygame.draw.rect(surface, color, rect, border_radius=DEFAULT_BORDER_RADIUS)
        pygame.draw.rect(surface, border_color, rect, border_width, border_radius=DEFAULT_BORDER_RADIUS)

        text_surf = font.render(text, True, text_color)
        surface.blit(text_surf, text_surf.get_rect(center=rect.center))

    def _draw_panel_with_title(self, surface, rect, title, title_font=None, title_color=WHITE, panel_color=None,
                               border_color=WHITE):
        """
        Отрисовывает стандартную панель с заголовком вверху.

        Args:
            surface (pygame.Surface): Поверхность для отрисовки.
            rect (pygame.Rect): Прямоугольник панели.
            title (str): Текст заголовка.
            title_font (pygame.font.Font, optional): Шрифт заголовка. По умолчанию 'default'.
            title_color (tuple, optional): Цвет заголовка. По умолчанию WHITE.
            panel_color (tuple, optional): Цвет фона панели. По умолчанию цвет из настроек.
            border_color (tuple, optional): Цвет рамки. По умолчанию WHITE.
        """
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
        """
        Отрисовывает строку текста, центрируя ее по горизонтали.

        Args:
            surface (pygame.Surface): Поверхность для отрисовки.
            text (str): Текст для отрисовки.
            font (pygame.font.Font): Используемый шрифт.
            color (tuple): Цвет текста.
            center_x (int): Горизонтальная координата центра текста.
            top_y (int): Вертикальная координата верхнего края текста.
        """
        text_surf = font.render(text, True, color)
        surface.blit(text_surf, text_surf.get_rect(centerx=center_x, top=top_y))