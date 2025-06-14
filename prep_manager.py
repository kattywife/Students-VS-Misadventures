# prep_manager.py

import pygame
from settings import *
from assets import SOUNDS


class PrepManager:
    def __init__(self, ui_manager, stipend):
        self.ui_manager = ui_manager
        self.stipend = stipend

        self.team_slots = 5
        self.team = []
        self.upgraded_heroes = set()

        self.neuro_mower_slots = 5
        self.neuro_mowers = {}

        self.all_defenders = list(DEFENDERS_DATA.keys())
        self.all_neuro_mowers = list(NEURO_MOWERS_DATA.keys())

        self.selected_card = None
        self.selected_card_type = None
        self.dragging = False
        self.selected_card_info = None
        self.close_card_button_rect = None

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            self.handle_click(event.pos)
        if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if self.dragging:
                self.handle_drop(event.pos)
            self.dragging = False
            self.selected_card = None

    def handle_click(self, pos):
        # 1. Если карточка с описанием открыта, ПЕРВЫМ ДЕЛОМ проверяем клик по крестику.
        if self.selected_card_info and self.close_card_button_rect and self.close_card_button_rect.collidepoint(pos):
            if SOUNDS.get('cards'): SOUNDS['cards'].play()
            self.selected_card_info = None
            return  # Важно! Прерываем дальнейшую обработку клика.

        # Если карточка открыта, никакой другой клик не должен ничего делать, кроме закрытия.
        if self.selected_card_info:
            return

        # 2. Клик по кнопке улучшения героя в команде.
        for hero_type, rect in self.ui_manager.upgrade_buttons.items():
            if rect.collidepoint(pos):
                self.try_upgrade_hero(hero_type)
                return

        # 3. Клик по любой карточке (в выборе, в команде, в арсенале) для просмотра информации.
        # Этот блок теперь будет срабатывать, только если карточка с описанием закрыта.
        all_visible_cards = {
            **self.ui_manager.selection_cards_rects,
            **self.ui_manager.team_card_rects,
            **self.ui_manager.neuro_card_rects
        }
        for card_type, rect in all_visible_cards.items():
            if rect.collidepoint(pos):
                self.show_card_info(card_type)
                return

        # 4. Если ничего из вышеперечисленного не сработало, значит это клик, чтобы "взять" карточку.
        # Этот блок тоже сработает, только если описание закрыто.
        for card_type, rect in self.ui_manager.selection_cards_rects.items():
            if rect.collidepoint(pos):
                if SOUNDS.get('cards'): SOUNDS['cards'].play()
                self.selected_card = card_type
                self.dragging = True
                self.selected_card_type = 'defender' if card_type in self.all_defenders else 'neuro'
                return

    def handle_drop(self, pos):
        if not self.selected_card: return

        if self.selected_card_type == 'defender':
            if self.ui_manager.team_panel_rect.collidepoint(pos) and len(self.team) < self.team_slots:
                if self.selected_card not in self.team:
                    if SOUNDS.get('purchase'): SOUNDS['purchase'].play()
                    self.team.append(self.selected_card)

        elif self.selected_card_type == 'neuro':
            field_rect = self.ui_manager.field_panel_rect
            if field_rect.collidepoint(pos):
                row_height = (CELL_SIZE_H + 5)
                base_y = field_rect.top + 80
                if pos[1] > base_y:
                    row = int((pos[1] - base_y) / row_height)
                    if 0 <= row < GRID_ROWS:
                        cost = NEURO_MOWERS_DATA[self.selected_card]['cost']
                        if self.stipend >= cost and row not in self.neuro_mowers:
                            if SOUNDS.get('purchase'): SOUNDS['purchase'].play()
                            self.stipend -= cost
                            self.neuro_mowers[row] = self.selected_card

    def try_upgrade_hero(self, hero_type):
        if hero_type in self.upgraded_heroes: return
        upgrade_info = DEFENDERS_DATA[hero_type].get('upgrade')
        if not upgrade_info: return
        cost = upgrade_info['cost']
        if self.stipend >= cost:
            if SOUNDS.get('purchase'): SOUNDS['purchase'].play()
            self.stipend -= cost
            self.upgraded_heroes.add(hero_type)

    def show_card_info(self, card_type):
        if SOUNDS.get('cards'): SOUNDS['cards'].play()
        if card_type in DEFENDERS_DATA:
            data_source = DEFENDERS_DATA
        else:
            data_source = NEURO_MOWERS_DATA

        data = data_source[card_type]
        description = data.get('description', '').format(**data)
        self.selected_card_info = {
            'type': card_type,
            'name': data['display_name'],
            'description': description
        }

    def draw(self, surface):
        # Этот метод возвращает два значения, которые game_manager будет использовать
        start_button_rect, close_button_rect = self.ui_manager.draw_preparation_screen(
            surface, self.stipend, self.team, self.upgraded_heroes, self.neuro_mowers,
            self.all_defenders, self.all_neuro_mowers,
            self.selected_card, pygame.mouse.get_pos() if self.dragging else None,
            self.selected_card_info
        )
        self.close_card_button_rect = close_button_rect  # Сохраняем рект крестика для обработки кликов
        return start_button_rect

    def is_ready(self):
        return len(self.team) > 0