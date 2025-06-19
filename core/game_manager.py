# core/game_manager.py

import pygame
import sys
from data.settings import *
from core.ui_manager import UIManager
from core.level_manager import LevelManager
from data.assets import load_all_resources, load_image
from data.levels import LEVELS
from core.prep_manager import PrepManager
from core.battle_manager import BattleManager
from core.sound_manager import SoundManager


class Game:
    def __init__(self):
        pygame.mixer.pre_init(AUDIO_FREQUENCY, AUDIO_SIZE, AUDIO_CHANNELS, AUDIO_BUFFER)
        pygame.init()
        pygame.mixer.init()
        pygame.mixer.set_num_channels(AUDIO_NUM_CHANNELS)

        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption(TITLE)

        load_all_resources()

        self.clock = pygame.time.Clock()
        self.running = True
        self.ui_manager = UIManager(self.screen)
        self.sound_manager = SoundManager()
        self.background = load_image('menu_background.png', DEFAULT_COLORS['background'], (SCREEN_WIDTH, SCREEN_HEIGHT))

        self.max_level_unlocked = 1
        self.current_level_id = 1
        self.stipend = 150
        self.prep_manager = None
        self.battle_manager = None

        self.level_select_buttons = {}
        self.control_buttons = {}
        self.prep_buttons = {}

        self.pause_menu_buttons = {
            "Продолжить": pygame.Rect((0, 0), PAUSE_MENU_BUTTON_SIZE),
            "Рестарт": pygame.Rect((0, 0), PAUSE_MENU_BUTTON_SIZE),
            "Главное меню": pygame.Rect((0, 0), PAUSE_MENU_BUTTON_SIZE)
        }
        self.pause_menu_buttons["Продолжить"].center = (SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 - PAUSE_MENU_V_SPACING)
        self.pause_menu_buttons["Рестарт"].center = (SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)
        self.pause_menu_buttons["Главное меню"].center = (SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 + PAUSE_MENU_V_SPACING)

        self.state = 'START_SCREEN'
        self.level_clear_timer = 0
        self.victory_initial_delay = VICTORY_SOUND_DELAY
        self.victory_sound_played = False
        self.level_clear_duration = LEVEL_CLEAR_DEFAULT_DURATION

        self.placed_neuro_mowers = {}
        self.dragged_mower = None

    def run(self):
        while self.running:
            self.dt = self.clock.tick(FPS) / 1000.0
            if self.state == 'START_SCREEN':
                self._start_screen_loop()
            elif self.state == 'MAIN_MENU':
                self._main_menu_loop()
            elif self.state == 'SETTINGS':
                self._settings_loop()
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
        self.prep_manager = PrepManager(self.ui_manager, self.stipend, self.current_level_id, self.sound_manager)
        self.state = 'PREPARATION'
        self.sound_manager.play_music('prep_screen')
        self.placed_neuro_mowers.clear()
        self.dragged_mower = None

    def _start_neuro_placement(self):
        if self.prep_manager.is_ready():
            self.state = 'NEURO_PLACEMENT'

    def _start_battle(self):
        all_sprites = pygame.sprite.LayeredUpdates()
        defenders = pygame.sprite.Group()
        enemies = pygame.sprite.Group()
        projectiles = pygame.sprite.Group()
        coffee_beans = pygame.sprite.Group()
        neuro_mowers = pygame.sprite.Group()
        level_manager = LevelManager(self.current_level_id, enemies, all_sprites, self.sound_manager)

        final_mower_placement = {row: info['type'] for row, info in self.placed_neuro_mowers.items()}

        self.battle_manager = BattleManager(all_sprites, defenders, enemies, projectiles, coffee_beans, neuro_mowers,
                                            self.ui_manager, level_manager, self.sound_manager,
                                            self.prep_manager.team, self.prep_manager.upgrades,
                                            final_mower_placement)
        self.battle_manager.start()
        self.sound_manager.play_music(f'level_{self.current_level_id}')
        self.state = 'PLAYING'

    def _start_screen_loop(self):
        buttons_data = {"Начать обучение": START_SCREEN_BUTTON_SIZE, "Выход": START_SCREEN_BUTTON_SIZE}
        buttons = {}
        for i, (text, size) in enumerate(buttons_data.items()):
            rect = pygame.Rect((0, 0), size)
            rect.center = (
            SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 + START_SCREEN_BUTTON_V_OFFSET + i * START_SCREEN_BUTTON_V_SPACING)
            buttons[text] = rect

        for event in pygame.event.get():
            if event.type == pygame.QUIT: self.running = False
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                for text, rect in buttons.items():
                    if rect.collidepoint(event.pos):
                        self.sound_manager.play_sfx('button')
                        pygame.time.delay(BUTTON_CLICK_DELAY)
                        if text == "Выход":
                            self.running = False
                        else:
                            self.sound_manager.stop_music()
                            self.state = "MAIN_MENU"
                            self.sound_manager.play_music('main_team')

        self.screen.blit(self.background, (0, 0))
        self.ui_manager.draw_start_screen(self.screen, "Студенты против Злоключений", buttons)

    def _main_menu_loop(self):
        if self.sound_manager.current_music != 'main_team':
            self.sound_manager.play_music('main_team')

        for event in pygame.event.get():
            if event.type == pygame.QUIT: self.running = False
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                for level_id, rect in self.level_select_buttons.items():
                    if rect.collidepoint(event.pos):
                        self.sound_manager.play_sfx('button')
                        self._prepare_level(level_id)
                        return

                for text, rect in self.control_buttons.items():
                    if rect.collidepoint(event.pos):
                        self.sound_manager.play_sfx('button')
                        if text == "Выход":
                            self.running = False
                        elif text == "Настройки":
                            self.state = 'SETTINGS'
                        elif text == "Тест":
                            self._prepare_level(0)
                            return

        self.screen.blit(self.background, (0, 0))
        self.level_select_buttons, self.control_buttons = self.ui_manager.draw_main_menu(self.screen,
                                                                                         self.max_level_unlocked)

    def _settings_loop(self):
        self.screen.blit(self.background, (0, 0))
        self.ui_manager.draw_main_menu(self.screen, self.max_level_unlocked)

        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, MENU_OVERLAY_ALPHA))
        self.screen.blit(overlay, (0, 0))

        buttons = self.ui_manager.draw_settings_menu(self.screen, self.sound_manager.music_enabled,
                                                     self.sound_manager.sfx_enabled)

        for event in pygame.event.get():
            if event.type == pygame.QUIT: self.running = False
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                pos = event.pos
                if buttons['toggle_music'].collidepoint(pos):
                    self.sound_manager.play_sfx('button')
                    self.sound_manager.toggle_music()
                elif buttons['toggle_sfx'].collidepoint(pos):
                    self.sound_manager.toggle_sfx()
                    self.sound_manager.play_sfx('button')
                elif buttons['close'].collidepoint(pos):
                    self.sound_manager.play_sfx('button')
                    self.state = 'MAIN_MENU'

    def _preparation_loop(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT: self.running = False
            self.prep_manager.handle_event(event)
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                pos = event.pos
                if 'start' in self.prep_buttons and self.prep_buttons['start'].collidepoint(pos):
                    if self.prep_manager.is_ready():
                        self.sound_manager.play_sfx('button')
                        self._start_neuro_placement()
                        return
                if 'back' in self.prep_buttons and self.prep_buttons['back'].collidepoint(pos):
                    self.sound_manager.play_sfx('button')
                    self.sound_manager.play_music('main_team')
                    self.state = 'MAIN_MENU'
                    return
        self.prep_buttons = self.prep_manager.draw(self.screen)

    def _neuro_placement_loop(self):
        unplaced_rects, start_rect = self.ui_manager.draw_neuro_placement_screen(self.screen,
                                                                                 self.prep_manager.purchased_mowers,
                                                                                 self.placed_neuro_mowers,
                                                                                 self.dragged_mower)
        placement_grid_start_y = (SCREEN_HEIGHT - GRID_ROWS * PLACEMENT_GRID_CELL_H) / 2

        for event in pygame.event.get():
            if event.type == pygame.QUIT: self.running = False
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.dragged_mower is None:
                    for index, rect in unplaced_rects.items():
                        if rect.collidepoint(event.pos):
                            self.sound_manager.play_sfx('purchase')
                            self.dragged_mower = {'type': self.prep_manager.purchased_mowers[index],
                                                  'original_index': index, 'pos': event.pos}
                            return
                    for row, info in list(self.placed_neuro_mowers.items()):
                        mower_rect = pygame.Rect(
                            PLACEMENT_ZONE_X,
                            placement_grid_start_y + row * PLACEMENT_GRID_CELL_H,
                            PLACEMENT_GRID_CELL_W,
                            PLACEMENT_GRID_CELL_H
                        )
                        if mower_rect.collidepoint(event.pos):
                            self.sound_manager.play_sfx('purchase')
                            self.dragged_mower = self.placed_neuro_mowers.pop(row)
                            self.dragged_mower['pos'] = event.pos
                            return

                if start_rect and start_rect.collidepoint(event.pos) and len(
                        self.prep_manager.purchased_mowers) == len(self.placed_neuro_mowers):
                    self.sound_manager.play_sfx('button')
                    self._start_battle()
                    return

            if event.type == pygame.MOUSEMOTION:
                if self.dragged_mower: self.dragged_mower['pos'] = event.pos

            if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                if self.dragged_mower:
                    pos = event.pos
                    placement_area_rect = pygame.Rect(
                        PLACEMENT_ZONE_X, placement_grid_start_y,
                        PLACEMENT_GRID_CELL_W, GRID_ROWS * PLACEMENT_GRID_CELL_H
                    )

                    if placement_area_rect.collidepoint(pos):
                        row = int((pos[1] - placement_grid_start_y) // PLACEMENT_GRID_CELL_H)
                        if 0 <= row < GRID_ROWS and row not in self.placed_neuro_mowers:
                            self.sound_manager.play_sfx('purchase')
                            self.placed_neuro_mowers[row] = {'type': self.dragged_mower['type'],
                                                             'original_index': self.dragged_mower['original_index']}
                    self.dragged_mower = None

    def _playing_loop(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT: self.running = False
            action = self.battle_manager.handle_event(event)
            if action == 'PAUSE':
                self.sound_manager.play_sfx('button')
                pygame.time.delay(BUTTON_CLICK_DELAY)
                pygame.mixer.pause()
                pygame.mixer.music.pause()
                self.state = 'PAUSED'

        self.battle_manager.update()
        self.battle_manager.draw(self.screen)

        if self.battle_manager.level_manager.is_complete():
            self.stipend = self.prep_manager.stipend
            self.stipend += 150
            if self.current_level_id == self.max_level_unlocked and self.current_level_id > 0 and self.max_level_unlocked < len(
                    LEVELS) - 1:
                self.max_level_unlocked += 1
            self.state = 'LEVEL_CLEAR'
            self.level_clear_timer = pygame.time.get_ticks()
            self.victory_sound_played = False
        elif self.battle_manager.is_game_over:
            self.sound_manager.stop_all_sfx()
            self.sound_manager.stop_music()
            self.sound_manager.play_sfx('lose')
            self.state = 'GAME_OVER'

    def _paused_loop(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT: self.running = False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                pygame.mixer.unpause()
                pygame.mixer.music.unpause()
                self.state = "PLAYING"
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                for text, rect in self.pause_menu_buttons.items():
                    if rect.collidepoint(event.pos):
                        self.sound_manager.play_sfx('button')
                        pygame.time.delay(BUTTON_CLICK_DELAY)

                        if text == "Продолжить":
                            pygame.mixer.unpause()
                            pygame.mixer.music.unpause()
                            self.state = "PLAYING"
                        elif text == "Рестарт":
                            pygame.mixer.unpause()
                            pygame.mixer.music.unpause()
                            self._prepare_level(self.current_level_id)
                        elif text == "Главное меню":
                            self.sound_manager.stop_music()
                            self.sound_manager.play_music('main_team')
                            self.state = "MAIN_MENU"

        self.battle_manager.draw_world(self.screen)
        self.ui_manager.draw_shop(self.screen, self.battle_manager.selected_defender, self.battle_manager.coffee,
                                  self.battle_manager.upgrades)
        spawn_progress = self.battle_manager.level_manager.get_spawn_progress()
        kill_progress = self.battle_manager.level_manager.get_kill_progress()
        spawn_data = self.battle_manager.level_manager.get_spawn_count_data()
        kill_data = self.battle_manager.level_manager.get_kill_count_data()
        self.ui_manager.draw_hud(self.screen, spawn_progress, kill_progress, spawn_data, kill_data,
                                 self.battle_manager.calamity_notification)
        self.ui_manager.draw_menu(self.screen, "Пауза", self.pause_menu_buttons)

    def _level_clear_loop(self):
        now = pygame.time.get_ticks()
        if not self.victory_sound_played and now - self.level_clear_timer > self.victory_initial_delay:
            self.sound_manager.stop_all_sfx()
            self.sound_manager.stop_music()
            self.sound_manager.play_sfx('win')
            self.victory_sound_played = True
            self.level_clear_timer = pygame.time.get_ticks()

        level_clear_duration = self.level_clear_duration
        if self.sound_manager.sfx_enabled:
            level_clear_duration = self.sound_manager.get_sfx_length('win') * 1000

        if self.victory_sound_played and now - self.level_clear_timer > level_clear_duration:
            if self.current_level_id >= len(LEVELS) - 1:
                self.state = "GAME_VICTORY"
            else:
                self.state = 'LEVEL_VICTORY'
            return
        self.battle_manager.draw_world(self.screen)
        self.ui_manager.draw_level_clear_message(self.screen)

    # --- ИЗМЕНЕНИЯ ЗДЕСЬ: Удаляем _menu_loop_template и делаем явные циклы ---

    def _game_over_loop(self):
        buttons = {
            "Попробовать снова": pygame.Rect((0, 0), PAUSE_MENU_BUTTON_SIZE),
            "Главное меню": pygame.Rect((0, 0), PAUSE_MENU_BUTTON_SIZE)
        }
        buttons["Попробовать снова"].center = (SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)
        buttons["Главное меню"].center = (SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 + PAUSE_MENU_V_SPACING)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                for text, rect in buttons.items():
                    if rect.collidepoint(event.pos):
                        self.sound_manager.play_sfx('button')
                        pygame.time.delay(BUTTON_CLICK_DELAY)
                        self.state = "MAIN_MENU"
                        self.sound_manager.play_music('main_team')
                        return

        self.screen.blit(self.background, (0, 0))
        self.ui_manager.draw_menu(self.screen, "ОТЧИСЛЕНИЕ!", buttons)

    def _level_victory_loop(self):
        buttons = {
            "Следующий курс": pygame.Rect((0, 0), PAUSE_MENU_BUTTON_SIZE),
            "Главное меню": pygame.Rect((0, 0), PAUSE_MENU_BUTTON_SIZE)
        }
        buttons["Следующий курс"].center = (SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)
        buttons["Главное меню"].center = (SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 + PAUSE_MENU_V_SPACING)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                for text, rect in buttons.items():
                    if rect.collidepoint(event.pos):
                        self.sound_manager.play_sfx('button')
                        pygame.time.delay(BUTTON_CLICK_DELAY)
                        self.state = "MAIN_MENU"
                        self.sound_manager.play_music('main_team')
                        return

        self.screen.blit(self.background, (0, 0))
        self.ui_manager.draw_menu(self.screen, "КУРС ПРОЙДЕН!", buttons)

    def _game_victory_loop(self):
        buttons = {"Главное меню": pygame.Rect((0, 0), PAUSE_MENU_BUTTON_SIZE)}
        buttons["Главное меню"].center = (SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if buttons["Главное меню"].collidepoint(event.pos):
                    self.sound_manager.play_sfx('button')
                    pygame.time.delay(BUTTON_CLICK_DELAY)
                    self.state = "MAIN_MENU"
                    self.sound_manager.play_music('main_team')
                    return

        self.screen.blit(self.background, (0, 0))
        self.ui_manager.draw_menu(self.screen, "ДИПЛОМ ЗАЩИЩЕН!", buttons)