# prep_manager.py

import pygame
import random
from settings import *
from assets import SOUNDS
from levels import LEVELS


class PrepManager:
    def __init__(self, ui_manager, stipend, level_id):
        self.ui_manager = ui_manager
        self.stipend = stipend
        self.level_id = level_id
        self.level_data = LEVELS.get(level_id, LEVELS[1])

        self.team_slots = MAX_TEAM_SIZE
        self.team = []
        self.upgraded_heroes = set()

        self.neuro_mower_slots = self.level_data.get('neuro_slots', 2)
        self.chat_gpt_limit = 2
        self.purchased_mowers = []

        self.all_defenders = list(DEFENDERS_DATA.keys())
        self.all_neuro_mowers = list(NEURO_MOWERS_DATA.keys())

        self.selected_card_info = None
        self.info_panel_buttons = {}
        self.random_buttons_rects = {}

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            self.handle_click(event.pos)

    def randomize_team(self):
        if SOUNDS.get('taking'): SOUNDS['taking'].play()
        self.team.clear();
        self.upgraded_heroes.clear()
        available_heroes = self.all_defenders.copy();
        random.shuffle(available_heroes)
        self.team = available_heroes[:self.team_slots]

    def randomize_neuro(self):
        if SOUNDS.get('taking'): SOUNDS['taking'].play()
        # Возвращаем стоимость старых нейросетей
        for mower_type in self.purchased_mowers:
            self.stipend += NEURO_MOWERS_DATA[mower_type]['cost']
        self.purchased_mowers.clear()

        # Покупаем новые случайные, пока хватает денег и слотов
        available_mowers = self.all_neuro_mowers.copy()
        while len(self.purchased_mowers) < self.neuro_mower_slots:
            random.shuffle(available_mowers)
            mower_to_buy = available_mowers[0]
            cost = NEURO_MOWERS_DATA[mower_to_buy]['cost']

            if mower_to_buy == 'chat_gpt' and self.purchased_mowers.count('chat_gpt') >= self.chat_gpt_limit:
                continue

            if self.stipend >= cost:
                self.stipend -= cost
                self.purchased_mowers.append(mower_to_buy)
            else:
                break  # Заканчиваем, если деньги кончились

    def handle_click(self, pos):
        # Обработка кнопок внутри открытой информационной панели
        if self.selected_card_info:
            if 'close' in self.info_panel_buttons and self.info_panel_buttons['close'].collidepoint(pos):
                if SOUNDS.get('cards'): SOUNDS['cards'].play(); self.selected_card_info = None; return
            if 'take' in self.info_panel_buttons and self.info_panel_buttons['take'].collidepoint(pos):
                self.try_take_card(self.selected_card_info['type']); self.selected_card_info = None; return
            if 'upgrade' in self.info_panel_buttons and self.info_panel_buttons['upgrade'].collidepoint(pos):
                self.try_upgrade_hero(self.selected_card_info['type']); return
            # Не закрывать панель при клике на нее саму
            if self.ui_manager.desc_panel_rect and self.ui_manager.desc_panel_rect.collidepoint(pos): return

        # Кнопки случайной генерации
        if 'team' in self.random_buttons_rects and self.random_buttons_rects['team'].collidepoint(pos):
            self.randomize_team(); return
        if 'neuro' in self.random_buttons_rects and self.random_buttons_rects['neuro'].collidepoint(pos):
            self.randomize_neuro(); return

        # Обработка кликов по карточкам (ИЗМЕНЕНИЕ 1)
        # Проверяем клики по всем группам карточек, чтобы избежать бага с перезаписью
        all_card_groups = [
            self.ui_manager.selection_cards_rects,
            self.ui_manager.team_card_rects,
            self.ui_manager.plan_cards_rects
        ]
        for group in all_card_groups:
            for card_type, rect in group.items():
                if rect.collidepoint(pos):
                    self.show_card_info(card_type)
                    return

    def try_take_card(self, card_type):
        if card_type in self.all_defenders:
            if len(self.team) < self.team_slots and card_type not in self.team:
                if SOUNDS.get('taking'): SOUNDS['taking'].play(); self.team.append(card_type)
        elif card_type in self.all_neuro_mowers:
            if len(self.purchased_mowers) >= self.neuro_mower_slots: return
            if card_type == 'chat_gpt' and self.purchased_mowers.count('chat_gpt') >= self.chat_gpt_limit: return
            cost = NEURO_MOWERS_DATA[card_type]['cost']
            if self.stipend >= cost:
                if SOUNDS.get('taking'): SOUNDS['taking'].play(); self.stipend -= cost; self.purchased_mowers.append(
                    card_type)

    def try_upgrade_hero(self, hero_type):
        if hero_type in self.upgraded_heroes: return
        upgrade_info = DEFENDERS_DATA[hero_type].get('upgrade')
        if not upgrade_info: return
        cost = upgrade_info['cost']
        if self.stipend >= cost:
            if SOUNDS.get('purchase'): SOUNDS['purchase'].play(); self.stipend -= cost; self.upgraded_heroes.add(
                hero_type)

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
        description = data.get('description', '').format(**{k: data.get(k, '?') for k in data})
        self.selected_card_info = {'type': card_type, 'name': data['display_name'], 'description': description}

    def draw(self, surface):
        start_button_rect, self.random_buttons_rects, self.info_panel_buttons = self.ui_manager.draw_preparation_screen(
            surface, self.stipend, self.team, self.upgraded_heroes, self.purchased_mowers,
            self.all_defenders, self.all_neuro_mowers,
            self.level_id, self.selected_card_info, self.neuro_mower_slots
        )
        return start_button_rect

    def is_ready(self):
        return len(self.team) > 0