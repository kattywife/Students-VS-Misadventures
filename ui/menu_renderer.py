# ui/menu_renderer.py

import pygame
from data.settings import *
from .base_component import BaseUIComponent


class MenuRenderer(BaseUIComponent):
    """
    Отвечает за отрисовку простых полноэкранных меню, таких как меню паузы,
    экран победы или поражения. Также содержит метод для отрисовки сообщения
    о завершении уровня.
    """

    def __init__(self, screen):
        """
        Инициализирует рендерер простых меню.

        Args:
            screen (pygame.Surface): Основная поверхность для отрисовки.
        """
        super().__init__(screen)

    def draw(self, surface, title_text, buttons):
        """
        Отрисовывает универсальное меню с затемнением, заголовком и кнопками.
        Этот метод используется для состояний "Пауза", "Победа", "Поражение".

        Args:
            surface (pygame.Surface): Поверхность для отрисовки.
            title_text (str): Текст, который будет отображен в качестве заголовка меню.
            buttons (dict): Словарь вида { 'имя_кнопки': pygame.Rect }, содержащий
                            кнопки, которые нужно отрисовать.
        """
        # 1. Затемняем фон, чтобы акцентировать внимание на меню
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, MENU_OVERLAY_ALPHA))
        surface.blit(overlay, (0, 0))

        # 2. Отрисовываем заголовок меню
        title = self.fonts['large'].render(title_text, True, WHITE)
        title_rect = title.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 4))
        surface.blit(title, title_rect)

        # 3. Отрисовываем все переданные кнопки
        for name, rect in buttons.items():
            self._draw_button(surface, name, rect, DEFAULT_COLORS['button'], WHITE, self.fonts['default'])

    def draw_level_clear_message(self, surface):
        """
        Отрисовывает большое сообщение "БРС: 100/100" по центру экрана
        после успешного прохождения уровня, перед показом меню победы.

        Args:
            surface (pygame.Surface): Поверхность для отрисовки.
        """
        text = "БРС: 100/100"
        font = self.fonts['huge']

        # Создаем две версии текста: основной и для тени
        text_surf = font.render(text, True, YELLOW)
        shadow_surf = font.render(text, True, BLACK)

        # Рисуем тень со смещением
        shadow_offset = LEVEL_CLEAR_SHADOW_OFFSET
        shadow_rect = shadow_surf.get_rect(center=(SCREEN_WIDTH / 2 + shadow_offset, SCREEN_HEIGHT / 2 + shadow_offset))
        surface.blit(shadow_surf, shadow_rect)

        # Рисуем основной текст поверх тени
        text_rect = text_surf.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2))
        surface.blit(text_surf, text_rect)