# prep_manager.py

import pygame
from settings import *
from assets import SOUNDS
from levels import LEVELS


class PrepManager:
    def __init__(self, ui_manager, stipend, level_id):
        self.ui_manager = ui_manager
        self.stipend = stipend
        self.level_id = level_id
        self.level_data = LEVELS.get(level_id, LEVELS[1])

        self.team_slots = 5
        self.team = []
        self.upgraded_heroes = set()

        # <-- ИЗМЕНЕНИЕ: Лимиты берутся из данных уровня
        self.neuro_mower_slots = self.level_data.get('neuro_slots', 2)
        self.chat_gpt_limit = 2
        self.neuro_mowers = {}  # {row: type}

        self.all_defenders = list(DEFENDERS_DATA.keys())
        self.all_neuro_mowers = list(NEURO_MOWERS_DATA.keys())

        self.selected_card_info = None
        self.info_panel_buttons = {}

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            self.handle_click(event.pos)

    def handle_click(self, pos):
        if self.selected_card_info:
            if 'close' in self.info_panel_buttons and self.info_panel_buttons['close'].collidepoint(pos):
                if SOUNDS.get('cards'): SOUNDS['cards'].play()
                self.selected_card_info = None
                return

            if 'take' in self.info_panel_buttons and self.info_panel_buttons['take'].collidepoint(pos):
                self.try_take_card(self.selected_card_info['type'])
                self.selected_card_info = None
                return

            if self.ui_manager.desc_panel_rect and self.ui_manager.desc_panel_rect.collidepoint(pos):
                return

        for hero_type, rect in self.ui_manager.upgrade_buttons.items():
            if rect.collidepoint(pos):
                self.try_upgrade_hero(hero_type)
                return

        all_clickable_cards = {
            **self.ui_manager.selection_cards_rects,
            **self.ui_manager.team_card_rects,
            **self.ui_manager.plan_cards_rects,
        }
        for card_type, rect in all_clickable_cards.items():
            if rect.collidepoint(pos):
                self.show_card_info(card_type)
                return

    def try_take_card(self, card_type):
        if card_type in self.all_defenders:
            if len(self.team) < self.team_slots and card_type not in self.team:
                if SOUNDS.get('taking'): SOUNDS['taking'].play()
                self.team.append(card_type)

        elif card_type in self.all_neuro_mowers:
            # <-- ИЗМЕНЕНИЕ: Проверки на лимиты
            if len(self.neuro_mowers) >= self.neuro_mower_slots:
                print("No more neuro-mower slots available for this level.")
                return

            if card_type == 'chat_gpt' and list(self.neuro_mowers.values()).count('chat_gpt') >= self.chat_gpt_limit:
                print("ChatGPT limit reached.")
                return

            cost = NEURO_MOWERS_DATA[card_type]['cost']
            if self.stipend >= cost:
                for row in range(GRID_ROWS):  # Ищем свободный слот в пределах всех рядов
                    if row not in self.neuro_mowers:
                        if SOUNDS.get('taking'): SOUNDS['taking'].play()
                        self.stipend -= cost
                        self.neuro_mowers[row] = card_type
                        break

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

        data_source = {}
        if card_type in DEFENDERS_DATA:
            data_source = DEFENDERS_DATA
        elif card_type in ENEMIES_DATA:
            data_source = ENEMIES_DATA
        elif card_type in NEURO_MOWERS_DATA:
            data_source = NEURO_MOWERS_DATA
        elif card_type in CALAMITIES_DATA:
            data_source = CALAMITIES_DATA
        else:
            return

        data = data_source[card_type]
        description_template = data.get('description', '')
        description = description_template.format(**{k: data.get(k, '?') for k in data})

        self.selected_card_info = {
            'type': card_type,
            'name': data['display_name'],
            'description': description
        }

    def draw(self, surface):
        start_button_rect, self.info_panel_buttons = self.ui_manager.draw_preparation_screen(
            surface, self.stipend, self.team, self.upgraded_heroes, self.neuro_mowers,
            self.all_defenders, self.all_neuro_mowers,
            self.level_id, self.selected_card_info, self.neuro_mower_slots
        )
        return start_button_rect

    def is_ready(self):
        return len(self.team) > 0