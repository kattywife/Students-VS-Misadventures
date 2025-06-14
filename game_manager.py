# game_manager.py

import pygame
import sys
from settings import *
from sprites import *
from ui_manager import UIManager
from level_manager import LevelManager
from assets import load_image, load_sound, SOUNDS
from levels import LEVELS
from prep_manager import PrepManager
from battle_manager import BattleManager


class Game:
    def __init__(self):
        pygame.mixer.pre_init(44100, -16, 2, 512)
        pygame.init()
        pygame.mixer.init()
        pygame.mixer.set_num_channels(32)

        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption(TITLE)
        self.clock = pygame.time.Clock()
        self.running = True

        self.ui_manager = UIManager(self.screen)
        self.background = load_image('background.png', DEFAULT_COLORS['background'], (SCREEN_WIDTH, SCREEN_HEIGHT))

        self.max_level_unlocked = 1
        self.current_level_id = 1
        self.stipend = 150

        self.prep_manager = None
        self.battle_manager = None

        self.level_select_buttons = {}
        self.control_buttons = {}
        self.prep_start_button = None
        self.level_intro_button = None
        self.pause_menu_buttons = {
            "Продолжить": pygame.Rect(0, 0, 300, 80),
            "Главное меню": pygame.Rect(0, 0, 400, 80)
        }
        self.pause_menu_buttons["Продолжить"].center = (SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)
        self.pause_menu_buttons["Главное меню"].center = (SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 + 100)

        self.state = 'START_SCREEN'
        self.level_clear_timer = 0
        self.victory_initial_delay = 300
        self.victory_sound_played = False
        self.level_clear_duration = 3000

        self._load_assets()

    def _load_assets(self):
        load_sound('button', 'pressing a button.mp3')
        load_sound('purchase', 'purchase and landing of the hero.mp3')
        load_sound('cards', 'cards.mp3')
        load_sound('damage', 'damage.mp3')
        load_sound('eating', 'eating.mp3')
        load_sound('scream', 'scream.mp3')
        load_sound('enemy_dead', 'enemy_dead.mp3')
        load_sound('hero_dead', 'hero_dead.mp3')
        load_sound('money', 'money.mp3')
        load_sound('win', 'win.mp3')

        for data in {**DEFENDERS_DATA, **ENEMIES_DATA}.values():
            if 'select_sound' in data: load_sound(data['select_sound'], data['select_sound'])

        if SOUNDS.get('win'):
            self.level_clear_duration = SOUNDS['win'].get_length() * 1000

    def run(self):
        while self.running:
            self.dt = self.clock.tick(FPS) / 1000.0

            if self.state == 'START_SCREEN':
                self._start_screen_loop()
            elif self.state == 'MAIN_MENU':
                self._main_menu_loop()
            elif self.state == 'PREPARATION':
                self._preparation_loop()
            elif self.state == 'LEVEL_INTRO':
                self._level_intro_loop()
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
        self.prep_manager = PrepManager(self.ui_manager, self.stipend)
        self.state = 'PREPARATION'

    def _start_intro(self):
        if not self.prep_manager.is_ready(): return
        self.state = 'LEVEL_INTRO'

    def _start_battle(self):
        self.stipend = self.prep_manager.stipend

        all_sprites = pygame.sprite.Group()
        defenders = pygame.sprite.Group()
        enemies = pygame.sprite.Group()
        projectiles = pygame.sprite.Group()
        coffee_beans = pygame.sprite.Group()
        neuro_mowers = pygame.sprite.Group()

        level_manager = LevelManager(self.current_level_id, enemies, neuro_mowers, all_sprites)

        self.battle_manager = BattleManager(all_sprites, defenders, enemies, projectiles, coffee_beans, neuro_mowers,
                                            self.ui_manager, level_manager,
                                            self.prep_manager.team, self.prep_manager.upgraded_heroes,
                                            self.prep_manager.neuro_mowers)
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
        buttons_data = {"Начать обучение": (400, 80), "Выход": (400, 80)}
        buttons = {}
        for i, (text, size) in enumerate(buttons_data.items()):
            rect = pygame.Rect(0, 0, size[0], size[1])
            rect.center = (SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 + i * 120)
            buttons[text] = rect
        next_states = {"Начать обучение": "MAIN_MENU"}
        self._menu_loop_template("Студенты против Злоключений", buttons, next_states)

    def _main_menu_loop(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT: self.running = False
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                for level_id, rect in self.level_select_buttons.items():
                    if rect.collidepoint(event.pos):
                        if SOUNDS.get('button'): SOUNDS['button'].play()
                        self._prepare_level(level_id)
                        return
                for text, rect in self.control_buttons.items():
                    if rect.collidepoint(event.pos):
                        if SOUNDS.get('button'): SOUNDS['button'].play()
                        if text == "Выход":
                            self.running = False
                        elif text == "Настройки":
                            print("Settings button clicked!")

        self.screen.blit(self.background, (0, 0))
        self.level_select_buttons, self.control_buttons = self.ui_manager.draw_main_menu(self.screen,
                                                                                         self.max_level_unlocked)

    def _preparation_loop(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT: self.running = False
            self.prep_manager.handle_event(event)
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.prep_start_button and self.prep_start_button.collidepoint(event.pos):
                    if self.prep_manager.is_ready():
                        if SOUNDS.get('button'): SOUNDS['button'].play()
                        self._start_intro()
                        return

        self.prep_start_button, _ = self.prep_manager.draw(self.screen)

    def _level_intro_loop(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT: self.running = False
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                pos = event.pos
                if self.prep_manager.selected_card_info:
                    if self.prep_manager.close_card_button_rect and self.prep_manager.close_card_button_rect.collidepoint(
                            pos):
                        if SOUNDS.get('cards'): SOUNDS['cards'].play()
                        self.prep_manager.selected_card_info = None
                    return

                all_cards = {**self.ui_manager.defender_card_rects, **self.ui_manager.enemy_card_rects}
                clicked_on_card = False
                for name, rect in all_cards.items():
                    if rect.collidepoint(pos):
                        self.prep_manager.show_card_info(name)
                        clicked_on_card = True
                        break

                if not clicked_on_card and self.level_intro_button and self.level_intro_button.collidepoint(pos):
                    if SOUNDS.get('button'): SOUNDS['button'].play()
                    self._start_battle()
                    return

        enemy_types = LevelManager(self.current_level_id, None, None, None).get_enemy_types_for_level()
        defender_types = list(DEFENDERS_DATA.keys())
        _, self.defender_card_rects, self.enemy_card_rects, self.level_intro_button, self.prep_manager.close_card_button_rect = \
            self.ui_manager.draw_character_intro_screen(self.screen, defender_types, enemy_types,
                                                        self.prep_manager.selected_card_info)

    def _playing_loop(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT: self.running = False
            action = self.battle_manager.handle_event(event)
            if action == 'PAUSE':
                if SOUNDS.get('button'): SOUNDS['button'].play()
                pygame.mixer.pause()
                self.state = 'PAUSED'

        self.battle_manager.update()
        self.battle_manager.draw(self.screen)

        if self.battle_manager.level_manager.is_complete():
            self.stipend += 150
            self.state = 'LEVEL_CLEAR'
        elif self.battle_manager.is_game_over:
            self.state = 'GAME_OVER'

    def _paused_loop(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                pygame.mixer.unpause()
                self.state = "PLAYING"
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                for text, rect in self.pause_menu_buttons.items():
                    if rect.collidepoint(event.pos):
                        if SOUNDS.get('button'): SOUNDS['button'].play()
                        pygame.time.delay(100)
                        if text == "Продолжить":
                            pygame.mixer.unpause()
                            self.state = "PLAYING"
                        else:
                            pygame.mixer.stop()
                            self.state = "MAIN_MENU"

        self.battle_manager.draw_world(self.screen)
        self.ui_manager.draw_menu(self.screen, "Пауза", self.pause_menu_buttons)

    def _level_clear_loop(self):
        now = pygame.time.get_ticks()
        if not self.victory_sound_played and now - self.level_clear_timer > self.victory_initial_delay:
            pygame.mixer.stop()
            if SOUNDS.get('win'): SOUNDS['win'].play()
            self.victory_sound_played = True
            self.level_clear_timer = pygame.time.get_ticks()

        if self.victory_sound_played and now - self.level_clear_timer > self.level_clear_duration:
            self.state = 'LEVEL_VICTORY'
            return

        self.battle_manager.draw_world(self.screen)
        self.ui_manager.draw_level_clear_message(self.screen)

    def _game_over_loop(self):
        buttons = {
            "Попробовать снова": pygame.Rect(0, 0, 400, 80),
            "Главное меню": pygame.Rect(0, 0, 400, 80)
        }
        buttons["Попробовать снова"].center = (SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)
        buttons["Главное меню"].center = (SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 + 100)
        next_states = {"Попробовать снова": "MAIN_MENU", "Главное меню": "MAIN_MENU"}
        self._menu_loop_template("ОТЧИСЛЕНИЕ!", buttons, next_states)

    def _level_victory_loop(self):
        if self.current_level_id == self.max_level_unlocked and self.max_level_unlocked < len(LEVELS):
            self.max_level_unlocked += 1
        if self.current_level_id >= len(LEVELS):
            self.state = "GAME_VICTORY"
            return

        buttons = {
            "Следующий курс": pygame.Rect(0, 0, 400, 80),
            "Главное меню": pygame.Rect(0, 0, 400, 80)
        }
        buttons["Следующий курс"].center = (SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)
        buttons["Главное меню"].center = (SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 + 100)
        next_states = {"Следующий курс": "MAIN_MENU", "Главное меню": "MAIN_MENU"}
        self._menu_loop_template("КУРС ПРОЙДЕН!", buttons, next_states)

    def _game_victory_loop(self):
        buttons = {"Главное меню": pygame.Rect(0, 0, 400, 80)}
        buttons["Главное меню"].center = (SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)
        self._menu_loop_template("ДИПЛОМ ЗАЩИЩЕН!", buttons, {"Главное меню": "MAIN_MENU"})