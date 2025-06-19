# ui/main_menu_renderer.py

import pygame
from data.settings import *
from data.levels import LEVELS
from data.assets import UI_IMAGES
from ui.base_component import BaseUIComponent


class MainMenuRenderer(BaseUIComponent):
    """Отвечает за отрисовку стартового экрана и главного меню."""

    def __init__(self, screen):
        super().__init__(screen)

    def draw_start_screen(self, surface, title_text, buttons):
        """
        Отрисовывает стартовый экран с большой плашкой и кнопками.

        Args:
            surface (pygame.Surface): Поверхность для отрисовки.
            title_text (str): Текст заголовка.
            buttons (dict): Словарь { 'имя_кнопки': pygame.Rect }.
        """
        plaque_img = UI_IMAGES.get('title_plaque')
        if plaque_img:
            plaque_rect = plaque_img.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 4))
            surface.blit(plaque_img, plaque_rect)

            title_surf = self.fonts['title'].render(title_text, True, TITLE_BROWN)
            title_rect = title_surf.get_rect(
                center=(plaque_rect.centerx, plaque_rect.centery + TITLE_PLAQUE_TEXT_V_OFFSET))
            surface.blit(title_surf, title_rect)
        else:
            # Fallback, если изображение не загрузилось
            title = self.fonts['large'].render(title_text, True, WHITE)
            surface.blit(title, title.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 4)))

        for name, rect in buttons.items():
            button_color = DEFAULT_COLORS['button']
            if name == "Начать обучение":
                button_color = START_BUTTON_GREEN
            elif name == "Выход":
                button_color = EXIT_BUTTON_RED

            self._draw_button(surface, name, rect, button_color, WHITE, self.fonts['default'])

    def draw_main_menu(self, surface, max_level_unlocked):
        """
        Отрисовывает главное меню с панелью выбора уровней и кнопками управления.

        Args:
            surface (pygame.Surface): Поверхность для отрисовки.
            max_level_unlocked (int): ID последнего разблокированного уровня.

        Returns:
            tuple: (level_buttons, control_buttons) - словари с Rect'ами кликабельных кнопок.
        """
        panel_rect = pygame.Rect(
            MAIN_MENU_PANEL_X_OFFSET,
            (SCREEN_HEIGHT - MAIN_MENU_PANEL_SIZE[1]) / 2,
            *MAIN_MENU_PANEL_SIZE
        )
        self._draw_panel_with_title(surface, panel_rect, "Главное меню", self.fonts['large'])

        level_buttons = self._draw_level_buttons(surface, panel_rect, max_level_unlocked)
        control_buttons = self._draw_control_buttons(surface)

        return level_buttons, control_buttons

    def _draw_level_buttons(self, surface, panel_rect, max_level_unlocked):
        """Отрисовывает кнопки выбора уровней на панели."""
        level_buttons = {}
        for level_id, data in LEVELS.items():
            if level_id == 0:  # Пропускаем тестовый уровень
                continue

            is_unlocked = level_id <= max_level_unlocked
            button_rect = pygame.Rect((0, 0), MAIN_MENU_LEVEL_BUTTON_SIZE)
            button_rect.center = (
                panel_rect.centerx,
                panel_rect.top + MAIN_MENU_LEVEL_BUTTON_TOP_OFFSET + (level_id - 1) * MAIN_MENU_LEVEL_BUTTON_V_SPACING
            )
            color = YELLOW if is_unlocked else GREY
            self._draw_button(surface, data['name'], button_rect, color, BLACK, self.fonts['default'])

            if is_unlocked:
                level_buttons[level_id] = button_rect
        return level_buttons

    def _draw_control_buttons(self, surface):
        """Отрисовывает кнопки управления (Настройки, Тест, Выход)."""
        control_buttons = {}
        btn_width, btn_height = MAIN_MENU_CONTROL_BUTTON_SIZE
        base_x = SCREEN_WIDTH - MAIN_MENU_CONTROL_RIGHT_OFFSET - btn_width
        settings_x = base_x - (btn_width / 2 + MAIN_MENU_CONTROL_H_GAP / 2)
        test_x = base_x + (btn_width / 2 + MAIN_MENU_CONTROL_H_GAP / 2)

        # Кнопка Настройки
        settings_rect = pygame.Rect((0, 0), (btn_width, btn_height))
        settings_rect.center = (settings_x, MAIN_MENU_CONTROL_TOP_OFFSET)
        self._draw_button(surface, "Настройки", settings_rect, DEFAULT_COLORS['shop_panel'], WHITE)
        control_buttons["Настройки"] = settings_rect

        # Кнопка Тест
        test_rect = pygame.Rect((0, 0), (btn_width, btn_height))
        test_rect.center = (test_x, MAIN_MENU_CONTROL_TOP_OFFSET)
        self._draw_button(surface, "Тест", test_rect, DEFAULT_COLORS['shop_panel'], WHITE)
        control_buttons["Тест"] = test_rect

        # Кнопка Выход
        exit_rect = pygame.Rect((0, 0), (btn_width * 2 + MAIN_MENU_CONTROL_H_GAP, btn_height))
        exit_rect.center = (base_x, MAIN_MENU_CONTROL_TOP_OFFSET + btn_height + MAIN_MENU_CONTROL_V_GAP)
        self._draw_button(surface, "Выход", exit_rect, DEFAULT_COLORS['shop_panel'], WHITE)
        control_buttons["Выход"] = exit_rect

        return control_buttons