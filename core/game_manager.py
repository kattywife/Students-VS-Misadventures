# core/game_manager.py

import pygame
import sys
from data.settings import *
from entities.other_sprites import NeuroMower
from core.ui_manager import UIManager
from core.level_manager import LevelManager
from data.assets import load_all_resources, SOUNDS, load_image
from data.levels import LEVELS
from core.prep_manager import PrepManager
from core.battle_manager import BattleManager


class Game:
    def __init__(self):
        pygame.mixer.pre_init(44100, -16, 2, 512);
        pygame.init();
        pygame.mixer.init();
        pygame.mixer.set_num_channels(32)
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT));
        pygame.display.set_caption(TITLE)
        self.clock = pygame.time.Clock();
        self.running = True
        self.ui_manager = UIManager(self.screen)

        self.background = None
        self.max_level_unlocked = 1
        self.current_level_id = 1
        self.stipend = 150
        self.prep_manager = None;
        self.battle_manager = None

        self.level_select_buttons = {};
        self.control_buttons = {};
        self.prep_buttons = {}
        self.pause_menu_buttons = {"Продолжить": pygame.Rect(0, 0, 300, 80), "Главное меню": pygame.Rect(0, 0, 400, 80)}
        self.pause_menu_buttons["Продолжить"].center = (SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2);
        self.pause_menu_buttons["Главное меню"].center = (SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 + 100)

        self.state = 'START_SCREEN'
        self.level_clear_timer = 0;
        self.victory_initial_delay = 300;
        self.victory_sound_played = False;
        self.level_clear_duration = 3000

        self.placed_neuro_mowers = {}
        self.dragged_mower = None

        self._load_resources()

    def _load_resources(self):
        load_all_resources()
        self.background = load_image('background.png', DEFAULT_COLORS['background'], (SCREEN_WIDTH, SCREEN_HEIGHT))
        if SOUNDS.get('win'): self.level_clear_duration = SOUNDS['win'].get_length() * 1000

    def run(self):
        while self.running:
            self.dt = self.clock.tick(FPS) / 1000.0
            if self.state == 'START_SCREEN':
                self._start_screen_loop()
            elif self.state == 'MAIN_MENU':
                self._main_menu_loop()
            elif self.state == 'PREPARATION':
                self._preparation_loop()
            elif self.state == 'NEURO_PLACEMENT':
                self._neuro_placement_loop()
            elif self.state == 'PLAYING':
                self._playing_loop()
            elif self.state == 'PAUSED':
                self._paused_loop()
            elif self.state == 'LEVEL_CLEAR':
                self._level_clear_loop()
            elif self.state == 'GAME_OVER':
                self._game_over_loop()
            elif self.state == 'LEVEL_VICTORY':
                self._level_victory_loop()
            elif self.state == 'GAME_VICTORY':
                self._game_victory_loop()
            pygame.display.flip()

    def _prepare_level(self, level_id):
        self.current_level_id = level_id
        self.prep_manager = PrepManager(self.ui_manager, self.stipend, self.current_level_id)
        self.state = 'PREPARATION'
        self.placed_neuro_mowers.clear()
        self.dragged_mower = None

    def _start_neuro_placement(self):
        if self.prep_manager.is_ready():
            self.state = 'NEURO_PLACEMENT'

    def _start_battle(self):
        self.stipend = self.prep_manager.stipend
        all_sprites = pygame.sprite.LayeredUpdates()
        defenders = pygame.sprite.Group()
        enemies = pygame.sprite.Group()
        projectiles = pygame.sprite.Group()
        coffee_beans = pygame.sprite.Group()
        neuro_mowers = pygame.sprite.Group()
        level_manager = LevelManager(self.current_level_id, enemies, all_sprites)

        final_mower_placement = {row: info['type'] for row, info in self.placed_neuro_mowers.items()}

        self.battle_manager = BattleManager(all_sprites, defenders, enemies, projectiles, coffee_beans, neuro_mowers,
                                            self.ui_manager, level_manager,
                                            self.prep_manager.team, self.prep_manager.upgrades,
                                            final_mower_placement)
        self.battle_manager.start()
        self.state = 'PLAYING'

    def _menu_loop_template(self, title, buttons_config, next_states):
        for event in pygame.event.get():
            if event.type == pygame.QUIT: self.running = False
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                for text, rect in buttons_config.items():
                    if rect.collidepoint(event.pos):
                        if SOUNDS.get('button'): SOUNDS['button'].play()
                        pygame.time.delay(100)
                        if text == "Выход":
                            self.running = False
                        else:
                            pygame.mixer.stop()
                            if self.state == 'GAME_OVER' and text == 'Попробовать снова':
                                self.state = "MAIN_MENU"
                            else:
                                self.state = next_states.get(text)
        self.screen.blit(self.background, (0, 0))
        self.ui_manager.draw_menu(self.screen, title, buttons_config)

    def _start_screen_loop(self):
        buttons_data = {"Начать обучение": (400, 80), "Выход": (400, 80)};
        buttons = {}
        for i, (text, size) in enumerate(buttons_data.items()):
            rect = pygame.Rect(0, 0, size[0], size[1]);
            rect.center = (SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 + i * 120);
            buttons[text] = rect
        self._menu_loop_template("Студенты против Злоключений", buttons, {"Начать обучение": "MAIN_MENU"})

    def _main_menu_loop(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT: self.running = False
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                for level_id, rect in self.level_select_buttons.items():
                    if rect.collidepoint(event.pos):
                        if SOUNDS.get('button'): SOUNDS['button'].play(); self._prepare_level(level_id); return
                for text, rect in self.control_buttons.items():
                    if rect.collidepoint(event.pos):
                        if SOUNDS.get('button'): SOUNDS['button'].play()
                        if text == "Выход": self.running = False
        self.screen.blit(self.background, (0, 0))
        self.level_select_buttons, self.control_buttons = self.ui_manager.draw_main_menu(self.screen,
                                                                                         self.max_level_unlocked)

    def _preparation_loop(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT: self.running = False
            self.prep_manager.handle_event(event)
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                pos = event.pos
                if 'start' in self.prep_buttons and self.prep_buttons['start'].collidepoint(pos):
                    if self.prep_manager.is_ready():
                        if SOUNDS.get('button'): SOUNDS['button'].play()
                        self._start_neuro_placement()
                        return
                if 'back' in self.prep_buttons and self.prep_buttons['back'].collidepoint(pos):
                    if SOUNDS.get('button'): SOUNDS['button'].play()
                    self.state = 'MAIN_MENU'
                    return

        self.prep_buttons = self.prep_manager.draw(self.screen)

    def _neuro_placement_loop(self):
        unplaced_rects, start_rect = self.ui_manager.draw_neuro_placement_screen(self.screen,
                                                                                 self.prep_manager.purchased_mowers,
                                                                                 self.placed_neuro_mowers,
                                                                                 self.dragged_mower)

        for event in pygame.event.get():
            if event.type == pygame.QUIT: self.running = False
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.dragged_mower is None:
                    for index, rect in unplaced_rects.items():
                        if rect.collidepoint(event.pos):
                            if SOUNDS.get('purchase'): SOUNDS['purchase'].play()
                            self.dragged_mower = {'type': self.prep_manager.purchased_mowers[index],
                                                  'original_index': index, 'pos': event.pos}
                            return
                    for row, info in list(self.placed_neuro_mowers.items()):
                        placement_zone_width = CELL_SIZE_W + 20
                        placement_zone_x = GRID_START_X - placement_zone_width
                        mower_rect = pygame.Rect(0, 0, CELL_SIZE_W, CELL_SIZE_H)
                        mower_rect.center = (
                            placement_zone_x + placement_zone_width / 2,
                            GRID_START_Y + row * CELL_SIZE_H + CELL_SIZE_H / 2)

                        if mower_rect.collidepoint(event.pos):
                            if SOUNDS.get('purchase'): SOUNDS['purchase'].play()
                            self.dragged_mower = self.placed_neuro_mowers.pop(row)
                            self.dragged_mower['pos'] = event.pos
                            return

                if start_rect.collidepoint(event.pos) and len(self.prep_manager.purchased_mowers) == len(
                        self.placed_neuro_mowers):
                    if SOUNDS.get('button'): SOUNDS['button'].play()
                    self._start_battle()
                    return

            if event.type == pygame.MOUSEMOTION:
                if self.dragged_mower: self.dragged_mower['pos'] = event.pos

            if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                if self.dragged_mower:
                    pos = event.pos
                    placement_area_rect = pygame.Rect(GRID_START_X - CELL_SIZE_W - 20, GRID_START_Y,
                                                      CELL_SIZE_W + 20, GRID_ROWS * CELL_SIZE_H)

                    if placement_area_rect.collidepoint(pos):
                        row = (pos[1] - GRID_START_Y) // CELL_SIZE_H
                        if 0 <= row < GRID_ROWS and row not in self.placed_neuro_mowers:
                            if SOUNDS.get('purchase'): SOUNDS['purchase'].play()
                            self.placed_neuro_mowers[row] = {'type': self.dragged_mower['type'],
                                                             'original_index': self.dragged_mower['original_index']}

                    self.dragged_mower = None

    def _playing_loop(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT: self.running = False
            action = self.battle_manager.handle_event(event)
            if action == 'PAUSE':
                if SOUNDS.get('button'): SOUNDS['button'].play()
                pygame.time.delay(100)
                pygame.mixer.pause()
                self.state = 'PAUSED'

        self.battle_manager.update()
        self.battle_manager.draw(self.screen)

        if self.battle_manager.level_manager.is_complete():
            self.stipend += 150
            if self.current_level_id == self.max_level_unlocked and self.max_level_unlocked < len(LEVELS):
                self.max_level_unlocked += 1
            self.state = 'LEVEL_CLEAR'
            self.level_clear_timer = pygame.time.get_ticks()
            self.victory_sound_played = False
        elif self.battle_manager.is_game_over:
            self.state = 'GAME_OVER'

    def _paused_loop(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT: self.running = False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE: pygame.mixer.unpause(); self.state = "PLAYING"
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                for text, rect in self.pause_menu_buttons.items():
                    if rect.collidepoint(event.pos):
                        if SOUNDS.get('button'): SOUNDS['button'].play(); pygame.time.delay(100)
                        if text == "Продолжить":
                            pygame.mixer.unpause();
                            self.state = "PLAYING"
                        else:
                            pygame.mixer.stop();
                            self.state = "MAIN_MENU"
        self.battle_manager.draw_world(self.screen)
        self.ui_manager.draw_shop(self.screen, self.battle_manager.selected_defender, self.battle_manager.coffee)
        spawn_progress = self.battle_manager.level_manager.get_spawn_progress();
        kill_progress = self.battle_manager.level_manager.get_kill_progress()
        spawn_data = self.battle_manager.level_manager.get_spawn_count_data();
        kill_data = self.battle_manager.level_manager.get_kill_count_data()
        self.ui_manager.draw_hud(self.screen, spawn_progress, kill_progress, spawn_data, kill_data,
                                 self.battle_manager.calamity_notification)
        self.ui_manager.draw_menu(self.screen, "Пауза", self.pause_menu_buttons)

    def _level_clear_loop(self):
        now = pygame.time.get_ticks()
        if not self.victory_sound_played and now - self.level_clear_timer > self.victory_initial_delay:
            pygame.mixer.stop();
            if SOUNDS.get('win'): SOUNDS['win'].play()
            self.victory_sound_played = True;
            self.level_clear_timer = pygame.time.get_ticks()
        if self.victory_sound_played and now - self.level_clear_timer > self.level_clear_duration:
            if self.current_level_id >= len(LEVELS):
                self.state = "GAME_VICTORY"
            else:
                self.state = 'LEVEL_VICTORY'
            return
        self.battle_manager.draw_world(self.screen)
        self.ui_manager.draw_level_clear_message(self.screen)

    def _game_over_loop(self):
        buttons = {"Попробовать снова": pygame.Rect(0, 0, 400, 80), "Главное меню": pygame.Rect(0, 0, 400, 80)}
        buttons["Попробовать снова"].center = (SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2);
        buttons["Главное меню"].center = (SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 + 100)
        self._menu_loop_template("ОТЧИСЛЕНИЕ!", buttons,
                                 {"Попробовать снова": "MAIN_MENU", "Главное меню": "MAIN_MENU"})

    def _level_victory_loop(self):
        buttons = {"Следующий курс": pygame.Rect(0, 0, 400, 80), "Главное меню": pygame.Rect(0, 0, 400, 80)}
        buttons["Следующий курс"].center = (SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2);
        buttons["Главное меню"].center = (SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 + 100)
        self._menu_loop_template("КУРС ПРОЙДЕН!", buttons, {"Следующий курс": "MAIN_MENU", "Главное меню": "MAIN_MENU"})

    def _game_victory_loop(self):
        buttons = {"Главное меню": pygame.Rect(0, 0, 400, 80)};
        buttons["Главное меню"].center = (SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)
        self._menu_loop_template("ДИПЛОМ ЗАЩИЩЕН!", buttons, {"Главное меню": "MAIN_MENU"})