# ui/description_panel_renderer.py

import pygame
from data.settings import *
from data.assets import CARD_IMAGES
from .base_component import BaseUIComponent

# Словарь для сопоставления внутренних имен характеристик с их отображаемыми названиями.
STAT_DISPLAY_NAMES = {
    'health': 'Здоровье:', 'damage': 'Урон:', 'cooldown': 'Перезарядка:', 'radius': 'Радиус:',
    'production': 'Производство:', 'buff': 'Усиление:', 'heal_amount': 'Запас лечения:',
    'slow_duration': 'Длит. замедл.:', 'slow_factor': 'Сила замедл.:',
    'speed': 'Скорость:', 'projectile_speed': 'Скор. снаряда:'
}


class DescriptionPanelRenderer(BaseUIComponent):
    """
    Отвечает за отрисовку всплывающей панели с подробной информацией о юните.
    Панель показывает характеристики, описание, а также кнопки для действий
    (взять, выгнать, улучшить, отменить улучшение).
    """

    def __init__(self, screen):
        """
        Инициализирует рендерер панели описания.

        Args:
            screen (pygame.Surface): Основная поверхность для отрисовки.
        """
        super().__init__(screen)
        # Кэшируем Rect панели, так как он всегда одного размера и по центру.
        self.panel_rect = pygame.Rect(
            (SCREEN_WIDTH - DESC_PANEL_SIZE[0]) / 2,
            (SCREEN_HEIGHT - DESC_PANEL_SIZE[1]) / 2,
            *DESC_PANEL_SIZE
        )

    def draw(self, surface, card_data, team, upgrades, purchased_mowers, neuro_slots):
        """
        Главный метод отрисовки панели. Собирает все части в единое целое.

        Args:
            surface (pygame.Surface): Поверхность для отрисовки.
            card_data (dict): Словарь с данными о выбранной карточке (тип, имя, описание).
            team (list): Текущий состав команды игрока.
            upgrades (dict): Словарь с улучшениями героев.
            purchased_mowers (list): Список купленных нейросетей.
            neuro_slots (int): Максимальное количество слотов для нейросетей.

        Returns:
            dict: Словарь, содержащий Rect'ы всех кликабельных кнопок на панели.
                  Ключи - идентификаторы действий ('take', 'kick', 'upgrade_*', 'revert_*', 'close').
        """
        # 1. Затемняем фон
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, MENU_OVERLAY_ALPHA))
        surface.blit(overlay, (0, 0))

        # 2. Рисуем фон и рамку самой панели
        pygame.draw.rect(surface, DEFAULT_COLORS['shop_panel'], self.panel_rect, border_radius=DESC_PANEL_BORDER_RADIUS)
        pygame.draw.rect(surface, WHITE, self.panel_rect, THICK_BORDER_WIDTH, border_radius=DESC_PANEL_BORDER_RADIUS)

        # 3. Отрисовка составных частей панели
        card_type = card_data['type']
        img_rect = self._draw_header(surface, card_type, card_data['name'])
        upgrade_buttons, current_y = self._draw_stats(surface, card_type, team, upgrades,
                                                      img_rect.bottom + DESC_PANEL_STATS_TOP_MARGIN)
        self._draw_description(surface, card_data['description'], current_y)
        action_buttons = self._draw_actions(surface, card_data, team, purchased_mowers, neuro_slots)

        # 4. Собираем все кнопки в один словарь и возвращаем
        all_buttons = {**upgrade_buttons, **action_buttons}
        return all_buttons

    def _draw_header(self, surface, card_type, name):
        """Отрисовывает "шапку" панели: изображение и имя юнита."""
        img_size = DESC_PANEL_IMG_SIZE
        img = CARD_IMAGES.get(card_type)
        if img:
            img = pygame.transform.scale(img, (img_size, img_size))
            img_rect = img.get_rect(centerx=self.panel_rect.centerx,
                                    top=self.panel_rect.top + DESC_PANEL_IMG_TOP_MARGIN)
            surface.blit(img, img_rect)
        else: # Резервный вариант, если изображение не загрузилось
            img_rect = pygame.Rect(0, 0, img_size, img_size)
            img_rect.centerx = self.panel_rect.centerx
            img_rect.top = self.panel_rect.top + DESC_PANEL_IMG_TOP_MARGIN

        name_surf = self.fonts['default'].render(name, True, YELLOW)
        name_rect = name_surf.get_rect(centerx=self.panel_rect.centerx,
                                       top=img_rect.bottom + DESC_PANEL_NAME_TOP_MARGIN)
        surface.blit(name_surf, name_rect)
        return name_rect

    def _draw_stats(self, surface, card_type, team, upgrades, start_y):
        """Отрисовывает блок с характеристиками юнита и кнопками улучшений."""
        buttons = {}
        all_data = {**DEFENDERS_DATA, **ENEMIES_DATA, **NEURO_MOWERS_DATA, **CALAMITIES_DATA}
        unit_data = all_data.get(card_type)
        if not unit_data: return buttons, start_y

        left_margin, right_margin = self.panel_rect.left + DESC_PANEL_LEFT_MARGIN, self.panel_rect.right - DESC_PANEL_RIGHT_MARGIN
        line_y = start_y

        # Итерируемся по стандартизированным именам характеристик
        for key, title in STAT_DISPLAY_NAMES.items():
            if line_y > self.panel_rect.bottom - DESC_PANEL_STATS_MAX_Y_OFFSET: break # Прерываем, если не хватает места
            if key in unit_data:
                # Получаем отформатированное значение стата
                _, value_color, value_str = self._get_stat_display_values(unit_data, card_type, key, upgrades)

                # Рисуем название и значение характеристики
                title_surf = self.fonts['small_bold'].render(title, True, WHITE)
                value_surf = self.fonts['small'].render(value_str, True, value_color)
                surface.blit(title_surf, (left_margin, line_y))
                surface.blit(value_surf, (left_margin + DESC_PANEL_VALUE_X_OFFSET, line_y))

                # Рисуем кнопки улучшения, если юнит в команде и имеет улучшения для этого стата
                is_in_team = team and card_type in team
                if is_in_team and 'upgrades' in unit_data and key in unit_data['upgrades']:
                    upgrade_buttons = self._draw_upgrade_buttons_for_stat(surface, unit_data, card_type, key, upgrades,
                                                                          line_y, right_margin)
                    buttons.update(upgrade_buttons)

                line_y += DESC_PANEL_LINE_HEIGHT
        return buttons, line_y

    def _get_stat_display_values(self, unit_data, card_type, key, upgrades):
        """Форматирует значение характеристики для отображения."""
        base_value = unit_data[key]
        value_color = WHITE
        if base_value is None: return None, WHITE, DESC_PANEL_NO_STAT_TEXT

        # Проверяем, улучшена ли эта характеристика
        upgraded_stats_set = upgrades.get(card_type, set())
        if key in upgraded_stats_set:
            base_value += unit_data['upgrades'][key]['value']
            value_color = AURA_PINK  # Подсвечиваем улучшенные статы

        # Форматируем значения в зависимости от типа (проценты, секунды и т.д.)
        if key == 'radius':
            value_str = f"{base_value} {DESC_PANEL_RADIUS_UNIT}"
        elif key == "slow_factor":
            value_str = f"{1 - base_value:.0%}" # Отображаем как процент замедления
        elif key == "slow_duration":
            value_str = f"{base_value / 1000:.1f} {DESC_PANEL_SLOW_DURATION_UNIT}"
        elif key == "cooldown":
            value_str = f"{base_value:.1f} {DESC_PANEL_COOLDOWN_UNIT}"
        else:
            value_str = f"{base_value:.1f}".replace('.0', '') # Убираем .0 у целых чисел

        return base_value, value_color, value_str

    def _draw_upgrade_buttons_for_stat(self, surface, unit_data, card_type, key, upgrades, line_y, right_margin):
        """Отрисовывает кнопку 'Улучшить' или 'Отменить' для конкретной характеристики."""
        buttons = {}
        upgrade_info = unit_data['upgrades'][key]
        cost = upgrade_info['cost']
        line_height = DESC_PANEL_LINE_HEIGHT
        upgraded_stats_set = upgrades.get(card_type, set())

        # Если стат уже улучшен, рисуем кнопку отмены
        if key in upgraded_stats_set:
            btn_rect = pygame.Rect(0, 0, DESC_PANEL_UPGRADE_BTN_WIDTH,
                                   line_height + DESC_PANEL_UPGRADE_BTN_HEIGHT_ADJUST)
            btn_rect.midleft = (right_margin - btn_rect.width, line_y + line_height / 2)
            self._draw_button(surface, "Отменить", btn_rect, RED, WHITE, self.fonts['tiny'])
            buttons[f'revert_{key}'] = btn_rect
        # Иначе рисуем кнопку улучшения с бонусом и стоимостью
        else:
            bonus = upgrade_info['value']
            bonus_str = f"+{bonus:.1f}".replace('.0', '') if bonus > 0 else f"{bonus:.1f}".replace('.0', '')
            if key == 'radius': bonus_str = f"+{int(bonus)}"
            btn_text = f"Улучшить ({bonus_str}) ({cost}$)"
            btn_rect = pygame.Rect(0, 0, DESC_PANEL_UPGRADE_BTN_WIDTH_WIDE,
                                   line_height + DESC_PANEL_UPGRADE_BTN_HEIGHT_ADJUST)
            btn_rect.midleft = (right_margin - btn_rect.width, line_y + line_height / 2)
            self._draw_button(surface, btn_text, btn_rect, GREEN, BLACK, self.fonts['tiny'])
            buttons[f'upgrade_{key}'] = btn_rect
        return buttons

    def _draw_description(self, surface, description, start_y):
        """Отрисовывает блок с текстовым описанием юнита."""
        left_margin = self.panel_rect.left + DESC_PANEL_LEFT_MARGIN
        desc_title_surf = self.fonts['small_bold'].render("Описание:", True, WHITE)
        surface.blit(desc_title_surf, (left_margin, start_y + DESC_PANEL_DESC_TITLE_V_OFFSET))

        current_y_desc = start_y + DESC_PANEL_DESC_TEXT_V_OFFSET
        # Используем метод базового класса для переноса текста по словам
        wrapped_lines = self._render_text_wrapped(description, self.fonts['small'], WHITE,
                                                  self.panel_rect.width - 2 * DESC_PANEL_LEFT_MARGIN)
        for line_surf in wrapped_lines:
            surface.blit(line_surf, (left_margin, current_y_desc))
            current_y_desc += line_surf.get_height()

    def _draw_actions(self, surface, card_data, team, purchased_mowers, neuro_slots):
        """Отрисовывает основные кнопки действий (взять/выгнать) и кнопку закрытия."""
        buttons = {}
        card_type, source = card_data['type'], card_data.get('source')
        is_hero, is_mower = card_type in DEFENDERS_DATA, card_type in NEURO_MOWERS_DATA
        is_in_team_panel = source == 'team' # Определяем, была ли карточка выбрана из панели команды

        action_button_rect = pygame.Rect((0, 0), DESC_PANEL_ACTION_BTN_SIZE)
        action_button_rect.center = (
        self.panel_rect.centerx, self.panel_rect.bottom + DESC_PANEL_ACTION_BTN_BOTTOM_OFFSET)

        # Логика определения текста и цвета кнопки в зависимости от контекста
        text, color, text_color, is_clickable = "Действие", GREY, DARK_GREY, False
        if is_in_team_panel: # Если юнит уже в команде
            text = "Выгнать" if is_hero else "Удалить"
            color, text_color, is_clickable = RED, WHITE, True
            buttons['kick'] = action_button_rect
        elif is_hero: # Если это герой, которого можно взять
            is_in_team = team and card_type in team
            team_is_full = team and len(team) >= MAX_TEAM_SIZE
            is_clickable = not is_in_team and not team_is_full
            color = GREEN if is_clickable else GREY
            text = "Взять"
            if is_in_team: text = "Уже в команде"
            elif team_is_full: text = "Команда полна"
            text_color = BLACK if is_clickable else DARK_GREY
            if is_clickable: buttons['take'] = action_button_rect
        elif is_mower: # Если это нейросеть, которую можно взять
            slots_are_full = len(purchased_mowers) >= neuro_slots
            limit_reached = card_type == 'chat_gpt' and purchased_mowers.count('chat_gpt') >= CHAT_GPT_LIMIT
            is_clickable = not slots_are_full and not limit_reached
            color = GREEN if is_clickable else GREY
            text = "Взять"
            if slots_are_full: text = "Слоты полны"
            elif limit_reached: text = "Достигнут лимит"
            text_color = BLACK if is_clickable else DARK_GREY
            if is_clickable: buttons['take'] = action_button_rect

        self._draw_button(surface, text, action_button_rect, color, text_color, self.fonts['default'])

        # Отрисовка кнопки закрытия (крестик)
        close_rect = pygame.Rect(
            self.panel_rect.right - DESC_PANEL_CLOSE_BUTTON_SIZE - DESC_PANEL_CLOSE_BUTTON_MARGIN,
            self.panel_rect.top + DESC_PANEL_CLOSE_BUTTON_MARGIN,
            DESC_PANEL_CLOSE_BUTTON_SIZE, DESC_PANEL_CLOSE_BUTTON_SIZE)
        pygame.draw.line(surface, WHITE, close_rect.topleft, close_rect.bottomright, THICK_BORDER_WIDTH)
        pygame.draw.line(surface, WHITE, close_rect.topright, close_rect.bottomleft, THICK_BORDER_WIDTH)
        buttons['close'] = close_rect

        return buttons