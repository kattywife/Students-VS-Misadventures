# ui/prep_screen_renderer.py

import pygame
from data.settings import *
from data.assets import CARD_IMAGES, load_image
# ИСПРАВЛЕНИЕ: Возвращаем относительные импорты
from .base_component import BaseUIComponent
from .description_panel_renderer import DescriptionPanelRenderer


class PrepScreenRenderer(BaseUIComponent):
    """Отвечает за отрисовку экрана подготовки к бою."""

    def __init__(self, screen):
        super().__init__(screen)
        self.background_image = load_image('prep_background.png', DEFAULT_COLORS['background'],
                                           (SCREEN_WIDTH, SCREEN_HEIGHT))
        self.description_panel_renderer = DescriptionPanelRenderer(screen)

        # Кэширование Rect'ов для панелей
        panel_width = (SCREEN_WIDTH - 4 * PREP_PANEL_MARGIN) / 3
        panel_height = SCREEN_HEIGHT - 150
        self.team_panel_rect = pygame.Rect(PREP_PANEL_MARGIN, PREP_TOP_Y, panel_width, panel_height)
        self.selection_panel_rect = pygame.Rect(self.team_panel_rect.right + PREP_PANEL_MARGIN, PREP_TOP_Y, panel_width,
                                                panel_height)
        self.plan_panel_rect = pygame.Rect(self.selection_panel_rect.right + PREP_PANEL_MARGIN, PREP_TOP_Y, panel_width,
                                           panel_height)

        # Словари для хранения Rect'ов кликабельных карточек, будут обновляться при каждой отрисовке
        self.selection_cards_rects = {}
        self.team_card_rects = {}
        self.plan_cards_rects = {}

    def draw(self, surface, stipend, team, upgrades, purchased_mowers, neuro_slots, enemy_types, calamity_types,
             selected_card_info):
        """Главный метод отрисовки экрана."""
        surface.blit(self.background_image, (0, 0))

        # Отрисовка трех основных панелей
        random_buttons = self._draw_team_panel(surface, team, upgrades, purchased_mowers, neuro_slots)
        self.selection_cards_rects = self._draw_selection_panel(surface, upgrades, team, purchased_mowers)
        self.plan_cards_rects = self._draw_plan_panel(surface, enemy_types, calamity_types)

        # Отрисовка HUD и стипендии
        prep_buttons = self._draw_prep_hud(surface, len(team) > 0)
        self._draw_stipend_panel(surface, stipend)

        # Отрисовка панели с описанием, если выбрана карточка
        info_panel_buttons = {}
        if selected_card_info:
            info_panel_buttons = self.description_panel_renderer.draw(surface, selected_card_info, team, upgrades,
                                                                      purchased_mowers, neuro_slots)

        return prep_buttons, random_buttons, info_panel_buttons

    def _draw_team_panel(self, surface, team, upgrades, purchased_mowers, neuro_slots):
        """Отрисовка левой панели с командой игрока."""
        self._draw_panel_with_title(surface, self.team_panel_rect, "Твоя команда")
        self.team_card_rects = {}

        hero_slots_bottom_y = self._render_hero_slots(surface, team, upgrades)

        random_team_rect = pygame.Rect((0, 0), PREP_RANDOM_TEAM_BTN_SIZE)
        random_team_rect.center = (self.team_panel_rect.centerx, hero_slots_bottom_y + PREP_RANDOM_TEAM_BTN_TOP_OFFSET)
        self._draw_button(surface, "Случайная команда", random_team_rect, RANDOM_BUTTON_COLOR, WHITE,
                          self.fonts['tiny'])

        neuro_slots_start_y = random_team_rect.bottom + PREP_NEURO_SLOTS_TOP_MARGIN
        neuro_slots_bottom_y = self._render_neuro_slots(surface, purchased_mowers, neuro_slots, neuro_slots_start_y)

        random_neuro_rect = pygame.Rect((0, 0), PREP_RANDOM_TEAM_BTN_SIZE)
        random_neuro_rect.center = (
        self.team_panel_rect.centerx, neuro_slots_bottom_y + PREP_RANDOM_NEURO_BTN_TOP_OFFSET)
        self._draw_button(surface, "Случайные нейросети", random_neuro_rect, RANDOM_BUTTON_COLOR, WHITE,
                          self.fonts['tiny'])

        return {'team': random_team_rect, 'neuro': random_neuro_rect}

    def _render_hero_slots(self, surface, team, upgrades):
        """Отрисовка карточек героев в команде."""
        self._render_text_with_title(surface, "Одногруппники:", self.fonts['small'], YELLOW,
                                     self.team_panel_rect.centerx,
                                     self.team_panel_rect.top + PREP_HERO_SLOTS_TITLE_TOP_OFFSET)
        card_size, padding_x, padding_y, cols = PREP_TEAM_CARD_SIZE, PREP_TEAM_CARD_PADDING_X, PREP_TEAM_CARD_PADDING_Y, PREP_TEAM_COLS
        start_x = self.team_panel_rect.centerx - (cols * card_size + (cols - 1) * padding_x) / 2
        start_y = self.team_panel_rect.top + PREP_HERO_SLOTS_TOP_OFFSET
        bottom_y = start_y

        for i in range(MAX_TEAM_SIZE):
            row, col = divmod(i, cols)
            x, y = start_x + col * (card_size + padding_x), start_y + row * (card_size + padding_y)
            slot_rect = pygame.Rect(x, y, card_size, card_size)
            if i < len(team):
                hero_type = team[i]
                self._draw_unit_card(surface, hero_type, slot_rect, DEFENDERS_DATA[hero_type],
                                     is_upgraded=(hero_type in upgrades))
                self.team_card_rects[hero_type] = slot_rect
            else:
                pygame.draw.rect(surface, (*BLACK, PREP_EMPTY_SLOT_ALPHA), slot_rect,
                                 border_radius=DEFAULT_BORDER_RADIUS)
            bottom_y = slot_rect.bottom
        return bottom_y

    def _render_neuro_slots(self, surface, purchased_mowers, neuro_slots, start_y):
        """Отрисовка карточек нейросетей в команде."""
        title = f"Нейросети ({len(purchased_mowers)}/{neuro_slots}):"
        self._render_text_with_title(surface, title, self.fonts['small'], YELLOW, self.team_panel_rect.centerx, start_y)
        card_size, spacing = PREP_NEURO_CARD_SIZE, PREP_NEURO_CARD_H_SPACING
        neuro_start_x = self.team_panel_rect.centerx - (neuro_slots * card_size + (neuro_slots - 1) * spacing) / 2
        neuro_cards_y = start_y + PREP_NEURO_CARD_TOP_OFFSET
        bottom_y = neuro_cards_y

        for i in range(neuro_slots):
            rect = pygame.Rect(neuro_start_x + i * (card_size + spacing), neuro_cards_y, card_size, card_size)
            if i < len(purchased_mowers):
                mower_type = purchased_mowers[i]
                self._draw_unit_card(surface, mower_type, rect, NEURO_MOWERS_DATA[mower_type])
                unique_key = f"{mower_type}_{i}"
                self.team_card_rects[unique_key] = rect
            else:
                pygame.draw.rect(surface, (*BLACK, PREP_EMPTY_SLOT_ALPHA), rect, border_radius=DEFAULT_BORDER_RADIUS)
            bottom_y = rect.bottom
        return bottom_y

    def _draw_selection_panel(self, surface, upgrades, current_team, current_mowers):
        """Отрисовка центральной панели со всеми доступными юнитами."""
        self._draw_panel_with_title(surface, self.selection_panel_rect, "Выбор юнитов")

        self._render_text_with_title(surface, "Герои:", self.fonts['small'], WHITE, self.selection_panel_rect.centerx,
                                     self.selection_panel_rect.top + PREP_SELECTION_HEROES_TITLE_TOP)
        rects1 = self._draw_card_selection_list(surface, self.selection_panel_rect, list(DEFENDERS_DATA.keys()),
                                                DEFENDERS_DATA, PREP_SELECTION_HEROES_LIST_TOP, upgrades, current_team,
                                                current_mowers)

        self._render_text_with_title(surface, "Нейросети:", self.fonts['small'], WHITE,
                                     self.selection_panel_rect.centerx,
                                     self.selection_panel_rect.top + PREP_SELECTION_NEURO_TITLE_TOP)
        rects2 = self._draw_card_selection_list(surface, self.selection_panel_rect, list(NEURO_MOWERS_DATA.keys()),
                                                NEURO_MOWERS_DATA, PREP_SELECTION_NEURO_LIST_TOP, upgrades,
                                                current_team, current_mowers)

        return {**rects1, **rects2}

    def _draw_plan_panel(self, surface, enemy_types, calamity_types):
        """Отрисовка правой панели с информацией о предстоящем уровне."""
        self._draw_panel_with_title(surface, self.plan_panel_rect, "Учебный план")

        self._render_text_with_title(surface, "Ожидаемые враги:", self.fonts['small'], WHITE,
                                     self.plan_panel_rect.centerx,
                                     self.plan_panel_rect.top + PREP_SELECTION_HEROES_TITLE_TOP)
        enemy_rects = self._draw_card_selection_list(surface, self.plan_panel_rect, enemy_types, ENEMIES_DATA,
                                                     PREP_SELECTION_HEROES_LIST_TOP)

        calamity_rects = {}
        if calamity_types:
            self._render_text_with_title(surface, "Возможные напасти:", self.fonts['small'], YELLOW,
                                         self.plan_panel_rect.centerx,
                                         self.plan_panel_rect.top + PREP_SELECTION_NEURO_TITLE_TOP)
            calamity_rects = self._draw_card_selection_list(surface, self.plan_panel_rect, calamity_types,
                                                            CALAMITIES_DATA, PREP_SELECTION_NEURO_LIST_TOP)

        return {**enemy_rects, **calamity_rects}

    def _draw_card_selection_list(self, surface, panel_rect, types, data_source, start_y_offset, upgrades=None,
                                  current_team=None, current_mowers=None):
        """Вспомогательный метод для отрисовки сетки карточек."""
        card_rects = {}
        if not types: return card_rects

        card_size, padding, cols = PREP_SELECTION_CARD_SIZE, PREP_SELECTION_CARD_PADDING, PREP_SELECTION_COLS
        items_in_row = min(len(types), cols)
        total_width = items_in_row * card_size + (items_in_row - 1) * padding
        start_x_base = panel_rect.left + (panel_rect.width - total_width) / 2

        for i, item_type in enumerate(types):
            row, col = divmod(i, cols)
            x = start_x_base + col * (card_size + padding)
            y = panel_rect.top + start_y_offset + row * (card_size + padding + PREP_SELECTION_CARD_V_SPACING)
            card_rect = pygame.Rect(x, y, card_size, card_size)
            if item_type in data_source:
                is_upgraded = upgrades and item_type in upgrades
                is_selected = (current_team and item_type in current_team) or (
                            current_mowers and item_type in current_mowers)
                self._draw_unit_card(surface, item_type, card_rect, data_source[item_type], is_upgraded, is_selected)
                card_rects[item_type] = card_rect
        return card_rects

    def _draw_stipend_panel(self, surface, stipend):
        """Отрисовка панели стипендии вверху экрана."""
        stipend_bg_rect = pygame.Rect((0, 0), (PREP_STIPEND_PANEL_WIDTH, PREP_STIPEND_PANEL_HEIGHT))
        stipend_bg_rect.centerx = SCREEN_WIDTH / 2
        pygame.draw.rect(surface, DEFAULT_COLORS['shop_panel'], stipend_bg_rect, border_radius=DEFAULT_BORDER_RADIUS)

        stipend_text = self.fonts['default'].render(f"Стипендия: {stipend}", True, YELLOW)
        text_rect = stipend_text.get_rect(center=stipend_bg_rect.center)

        stipend_icon = CARD_IMAGES.get('stipend')
        if stipend_icon:
            text_rect.centerx += PREP_STIPEND_ICON_X_OFFSET
            surface.blit(stipend_text, text_rect)
            icon_rect = stipend_icon.get_rect(
                midleft=(text_rect.right + PREP_STIPEND_ICON_TEXT_GAP, stipend_bg_rect.centery))
            surface.blit(stipend_icon, icon_rect)
        else:
            surface.blit(stipend_text, text_rect)

    def _draw_prep_hud(self, surface, is_ready):
        """Отрисовка нижних кнопок 'Назад' и 'К расстановке'."""
        btn_width, btn_height = PREP_HUD_BUTTON_SIZE
        buttons = {}

        back_rect = pygame.Rect(PREP_HUD_BOTTOM_MARGIN, SCREEN_HEIGHT - btn_height - PREP_HUD_BOTTOM_MARGIN, btn_width,
                                btn_height)
        self._draw_button(surface, "Назад", back_rect, GREY, WHITE, self.fonts['default'])
        buttons['back'] = back_rect

        start_rect = pygame.Rect(SCREEN_WIDTH - btn_width - PREP_HUD_BOTTOM_MARGIN,
                                 SCREEN_HEIGHT - btn_height - PREP_HUD_BOTTOM_MARGIN, btn_width, btn_height)
        color = GREEN if is_ready else GREY
        text_color = BLACK if is_ready else DARK_GREY
        self._draw_button(surface, "К расстановке", start_rect, color, text_color, self.fonts['default'])
        buttons['start'] = start_rect

        return buttons

    def _draw_unit_card(self, surface, unit_type, rect, data, is_upgraded=False, is_selected=False):
        """Отрисовывает одну карточку юнита с рамками и стоимостью."""
        pygame.draw.rect(surface, DEFAULT_COLORS['shop_card'], rect, border_radius=DEFAULT_BORDER_RADIUS)
        if is_upgraded:
            pygame.draw.rect(surface, AURA_PINK,
                             rect.inflate(PREP_UPGRADED_BORDER_INFLATE, PREP_UPGRADED_BORDER_INFLATE),
                             SHOP_UPGRADE_BORDER_WIDTH, border_radius=PREP_UPGRADED_BORDER_RADIUS)
        if is_selected:
            pygame.draw.rect(surface, YELLOW, rect, THICK_BORDER_WIDTH, border_radius=PREP_SELECTED_BORDER_RADIUS)

        img = CARD_IMAGES.get(unit_type)
        if img:
            img = pygame.transform.scale(img, (
            rect.width - PREP_UNIT_CARD_IMG_PADDING, rect.height - PREP_UNIT_CARD_IMG_PADDING))
            surface.blit(img, img.get_rect(center=rect.center))

        cost = data.get('cost')
        if cost is not None:
            cost_color = COFFEE_COST_COLOR if unit_type in DEFENDERS_DATA else YELLOW
            cost_surf = self.fonts['tiny'].render(str(cost), True, cost_color)
            cost_rect = cost_surf.get_rect(bottomright=(
            rect.right - PREP_UNIT_CARD_COST_RIGHT_OFFSET, rect.bottom - PREP_UNIT_CARD_COST_BOTTOM_OFFSET))
            surface.blit(cost_surf, cost_rect)