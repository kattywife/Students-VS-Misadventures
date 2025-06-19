# ui/main_menu_renderer.py

import pygame
from data.settings import *
from data.levels import LEVELS
from data.assets import UI_IMAGES
from ui.base_component import BaseUIComponent


class MainMenuRenderer(BaseUIComponent):
    """
    Отвечает за отрисовку двух основных экранов: стартового экрана и главного меню.
    Использует утилитарные методы из BaseUIComponent для рисования кнопок и панелей.
    """

    def __init__(self, screen):
        """
        Инициализирует рендерер главного меню.

        Args:
            screen (pygame.Surface): Основная поверхность для отрисовки.
        """
        super().__init__(screen)

    def draw_start_screen(self, surface, title_text, buttons):
        """
        Отрисовывает стартовый экран с большой плашкой с названием игры и кнопками.

        Args:
            surface (pygame.Surface): Поверхность для отрисовки.
            title_text (str): Текст заголовка (название игры).
            buttons (dict): Словарь вида { 'имя_кнопки': pygame.Rect },
                            содержащий Rect'ы для обработки кликов.
        """
        plaque_img = UI_IMAGES.get('title_plaque')
        if plaque_img:
            # Отрисовка красивой плашки с названием
            plaque_rect = plaque_img.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 4))
            surface.blit(plaque_img, plaque_rect)

            title_surf = self.fonts['title'].render(title_text, True, TITLE_BROWN)
            title_rect = title_surf.get_rect(
                center=(plaque_rect.centerx, plaque_rect.centery + TITLE_PLAQUE_TEXT_V_OFFSET))
            surface.blit(title_surf, title_rect)
        else:
            # Резервный вариант (Fallback), если изображение плашки не загрузилось.
            # Отрисовываем простой текст.
            title = self.fonts['large'].render(title_text, True, WHITE)
            surface.blit(title, title.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 4)))

        # Отрисовка кнопок с использованием универсального метода _draw_button
        for name, rect in buttons.items():
            button_color = DEFAULT_COLORS['button']
            # Применяем специальные цвета для ключевых кнопок
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
                                      Используется для определения, какие кнопки уровней
                                      должны быть активными.

        Returns:
            tuple: Кортеж (level_buttons, control_buttons), где каждый элемент -
                   это словарь с Rect'ами кликабельных кнопок для обработки ввода.
        """
        # Отрисовка центральной панели меню
        panel_rect = pygame.Rect(
            MAIN_MENU_PANEL_X_OFFSET,
            (SCREEN_HEIGHT - MAIN_MENU_PANEL_SIZE[1]) / 2,
            *MAIN_MENU_PANEL_SIZE
        )
        self._draw_panel_with_title(surface, panel_rect, "Главное меню", self.fonts['large'])

        # Отрисовка и получение Rect'ов для кнопок
        level_buttons = self._draw_level_buttons(surface, panel_rect, max_level_unlocked)
        control_buttons = self._draw_control_buttons(surface)

        return level_buttons, control_buttons

    def _draw_level_buttons(self, surface, panel_rect, max_level_unlocked):
        """
        Отрисовывает кнопки выбора уровней на панели меню.
        Заблокированные уровни рисуются серым цветом и не возвращаются в словаре кнопок.
        """
        level_buttons = {}
        # Итерируемся по данным уровней из файла levels.py
        for level_id, data in LEVELS.items():
            if level_id == 0:  # Пропускаем тестовый уровень (ID 0)
                continue

            is_unlocked = level_id <= max_level_unlocked
            button_rect = pygame.Rect((0, 0), MAIN_MENU_LEVEL_BUTTON_SIZE)
            # Рассчитываем положение кнопки на основе ее ID
            button_rect.center = (
                panel_rect.centerx,
                panel_rect.top + MAIN_MENU_LEVEL_BUTTON_TOP_OFFSET + (level_id - 1) * MAIN_MENU_LEVEL_BUTTON_V_SPACING
            )
            color = YELLOW if is_unlocked else GREY
            self._draw_button(surface, data['name'], button_rect, color, BLACK, self.fonts['default'])

            # Добавляем кнопку в словарь для обработки кликов, только если она разблокирована
            if is_unlocked:
                level_buttons[level_id] = button_rect
        return level_buttons

    def _draw_control_buttons(self, surface):
        """Отрисовывает кнопки управления справа (Настройки, Тест, Выход)."""
        control_buttons = {}
        btn_width, btn_height = MAIN_MENU_CONTROL_BUTTON_SIZE
        # Расчет базовых координат для группы кнопок
        base_x = SCREEN_WIDTH - MAIN_MENU_CONTROL_RIGHT_OFFSET - btn_width
        settings_x = base_x - (btn_width / 2 + MAIN_MENU_CONTROL_H_GAP / 2)
        test_x = base_x + (btn_width / 2 + MAIN_MENU_CONTROL_H_GAP / 2)

        # Кнопка "Настройки"
        settings_rect = pygame.Rect((0, 0), (btn_width, btn_height))
        settings_rect.center = (settings_x, MAIN_MENU_CONTROL_TOP_OFFSET)
        self._draw_button(surface, "Настройки", settings_rect, DEFAULT_COLORS['shop_panel'], WHITE)
        control_buttons["Настройки"] = settings_rect

        # Кнопка "Тест"
        test_rect = pygame.Rect((0, 0), (btn_width, btn_height))
        test_rect.center = (test_x, MAIN_MENU_CONTROL_TOP_OFFSET)
        self._draw_button(surface, "Тест", test_rect, DEFAULT_COLORS['shop_panel'], WHITE)
        control_buttons["Тест"] = test_rect

        # Кнопка "Выход" (широкая)
        exit_rect = pygame.Rect((0, 0), (btn_width * 2 + MAIN_MENU_CONTROL_H_GAP, btn_height))
        exit_rect.center = (base_x, MAIN_MENU_CONTROL_TOP_OFFSET + btn_height + MAIN_MENU_CONTROL_V_GAP)
        self._draw_button(surface, "Выход", exit_rect, DEFAULT_COLORS['shop_panel'], WHITE)
        control_buttons["Выход"] = exit_rect

        return control_buttons