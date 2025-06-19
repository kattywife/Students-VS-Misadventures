# core/game_manager.py

import pygame
import sys
from data.settings import *
from ui.ui_manager import UIManager
from core.level_manager import LevelManager
from data.assets import load_all_resources, load_image
from data.levels import LEVELS
from core.prep_manager import PrepManager
from core.battle_manager import BattleManager
from core.sound_manager import SoundManager


class Game:
    """
    Главный класс игры. Отвечает за:
    - Инициализацию Pygame и основных менеджеров.
    - Управление основным игровым циклом.
    - Переключение между состояниями игры (меню, подготовка, бой и т.д.).
    - Хранение общих данных, передаваемых между состояниями.
    """

    def __init__(self):
        # 1. Инициализация Pygame и его подсистем
        pygame.mixer.pre_init(AUDIO_FREQUENCY, AUDIO_SIZE, AUDIO_CHANNELS, AUDIO_BUFFER)
        pygame.init()
        pygame.mixer.init()
        pygame.mixer.set_num_channels(AUDIO_NUM_CHANNELS)

        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption(TITLE)
        self.clock = pygame.time.Clock()
        self.running = True

        # 2. Загрузка ресурсов и инициализация менеджеров
        load_all_resources()
        self.ui_manager = UIManager(self.screen)
        self.sound_manager = SoundManager()
        self.background = load_image('menu_background.png', DEFAULT_COLORS['background'], (SCREEN_WIDTH, SCREEN_HEIGHT))

        # 3. Управление состояниями игры
        self.state = 'START_SCREEN'
        self.state_handlers = self._create_state_handlers()

        # 4. Общие данные игры, которые могут передаваться между состояниями
        self.game_data = {
            'stipend': INITIAL_STIPEND,
            'max_level_unlocked': 1,
            'current_level_id': 1,
            'placed_neuro_mowers': {},
            'dragged_mower': None,
            'prep_manager': None,
            'battle_manager': None
        }

    def _create_state_handlers(self):
        """
        Создает словарь-диспетчер. Ключ - имя состояния, значение - метод-обработчик.
        Это избавляет от громоздкой конструкции if/elif в главном цикле (принцип KISS).
        """
        return {
            'START_SCREEN': self._start_screen_loop,
            'MAIN_MENU': self._main_menu_loop,
            'SETTINGS': self._settings_loop,
            'PREPARATION': self._preparation_loop,
            'NEURO_PLACEMENT': self._neuro_placement_loop,
            'PLAYING': self._playing_loop,
            'PAUSED': self._paused_loop,
            'LEVEL_CLEAR': self._level_clear_loop,
            'GAME_OVER': self._game_over_loop,
            'LEVEL_VICTORY': self._level_victory_loop,
            'GAME_VICTORY': self._game_victory_loop,
        }

    def run(self):
        """Главный игровой цикл. Делегирует выполнение текущему состоянию."""
        while self.running:
            self.dt = self.clock.tick(FPS) / 1000.0

            handler = self.state_handlers.get(self.state)
            if handler:
                handler()
            else:
                print(f"Error: Unknown game state '{self.state}'")
                self.running = False

            pygame.display.flip()

    # --- Методы подготовки к состояниям ---

    def _prepare_level(self, level_id):
        """Готовит данные для входа в состояние PREPARATION."""
        self.game_data['current_level_id'] = level_id
        self.game_data['prep_manager'] = PrepManager(self.ui_manager, self.game_data['stipend'], level_id,
                                                     self.sound_manager)
        self.game_data['placed_neuro_mowers'].clear()
        self.game_data['dragged_mower'] = None
        self.sound_manager.play_music('prep_screen')
        self.state = 'PREPARATION'

    def _start_battle(self):
        """Готовит данные для входа в состояние PLAYING."""
        # Создаем все группы спрайтов для нового боя
        all_sprites = pygame.sprite.LayeredUpdates()
        defenders = pygame.sprite.Group()
        enemies = pygame.sprite.Group()
        projectiles = pygame.sprite.Group()
        coffee_beans = pygame.sprite.Group()
        neuro_mowers = pygame.sprite.Group()

        level_manager = LevelManager(self.game_data['current_level_id'], enemies, all_sprites, self.sound_manager)

        final_mower_placement = {row: info['type'] for row, info in self.game_data['placed_neuro_mowers'].items()}

        prep_manager = self.game_data['prep_manager']

        # ИСПРАВЛЕНИЕ: Передаем все 12 необходимых аргументов в конструктор BattleManager
        self.game_data['battle_manager'] = BattleManager(
            all_sprites=all_sprites,
            defenders=defenders,
            enemies=enemies,
            projectiles=projectiles,
            coffee_beans=coffee_beans,
            neuro_mowers=neuro_mowers,
            ui_manager=self.ui_manager,
            level_manager=level_manager,
            sound_manager=self.sound_manager,
            team=prep_manager.team,
            upgrades=prep_manager.upgrades,
            placed_mowers=final_mower_placement
        )

        self.game_data['battle_manager'].start()
        self.sound_manager.play_music(f"level_{self.game_data['current_level_id']}")
        self.state = 'PLAYING'

    # --- Методы-циклы для каждого состояния ---

    def _start_screen_loop(self):
        buttons = self._create_menu_buttons(
            [("Начать обучение", START_SCREEN_BUTTON_SIZE), ("Выход", START_SCREEN_BUTTON_SIZE)])

        for event in pygame.event.get():
            if event.type == pygame.QUIT: self.running = False
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if buttons["Начать обучение"].collidepoint(event.pos):
                    self.sound_manager.play_sfx('button')
                    self.sound_manager.play_music('main_team')
                    self.state = "MAIN_MENU"
                elif buttons["Выход"].collidepoint(event.pos):
                    self.running = False

        self.screen.blit(self.background, (0, 0))
        self.ui_manager.draw_start_screen(self.screen, "Студенты против Злоключений", buttons)

    def _main_menu_loop(self):
        if self.sound_manager.current_music != 'main_team':
            self.sound_manager.play_music('main_team')

        self.screen.blit(self.background, (0, 0))
        level_buttons, control_buttons = self.ui_manager.draw_main_menu(self.screen,
                                                                        self.game_data['max_level_unlocked'])

        for event in pygame.event.get():
            if event.type == pygame.QUIT: self.running = False
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                pos = event.pos
                for level_id, rect in level_buttons.items():
                    if rect.collidepoint(pos):
                        self.sound_manager.play_sfx('button')
                        self._prepare_level(level_id)
                        return
                for text, rect in control_buttons.items():
                    if rect.collidepoint(pos):
                        self.sound_manager.play_sfx('button')
                        if text == "Выход":
                            self.running = False
                        elif text == "Настройки":
                            self.state = 'SETTINGS'
                        elif text == "Тест":
                            self._prepare_level(0)
                        return

    def _settings_loop(self):
        self.screen.blit(self.background, (0, 0))
        self.ui_manager.draw_main_menu(self.screen, self.game_data['max_level_unlocked'])
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
        prep_manager = self.game_data['prep_manager']
        prep_buttons = prep_manager.draw(self.screen)

        for event in pygame.event.get():
            if event.type == pygame.QUIT: self.running = False
            prep_manager.handle_event(event)
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                pos = event.pos
                if 'start' in prep_buttons and prep_buttons['start'].collidepoint(pos) and prep_manager.is_ready():
                    self.sound_manager.play_sfx('button')
                    self.state = 'NEURO_PLACEMENT'
                elif 'back' in prep_buttons and prep_buttons['back'].collidepoint(pos):
                    self.sound_manager.play_sfx('button')
                    self.sound_manager.play_music('main_team')
                    self.state = 'MAIN_MENU'

    def _neuro_placement_loop(self):
        prep_manager = self.game_data['prep_manager']
        unplaced_rects, start_rect = self.ui_manager.draw_neuro_placement_screen(self.screen,
                                                                                 prep_manager.purchased_mowers,
                                                                                 self.game_data['placed_neuro_mowers'],
                                                                                 self.game_data['dragged_mower'])

        for event in pygame.event.get():
            if event.type == pygame.QUIT: self.running = False
            self._handle_neuro_placement_events(event, unplaced_rects, start_rect)

    def _handle_neuro_placement_events(self, event, unplaced_rects, start_rect):
        """Обрабатывает события на экране расстановки нейросетей."""
        dragged_mower = self.game_data['dragged_mower']

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            pos = event.pos

            if start_rect and start_rect.collidepoint(pos):
                self.sound_manager.play_sfx('button')
                self._start_battle()
                return

            if dragged_mower is None:
                for index, rect in unplaced_rects.items():
                    if rect.collidepoint(pos):
                        self.sound_manager.play_sfx('purchase')
                        self.game_data['dragged_mower'] = {
                            'type': self.game_data['prep_manager'].purchased_mowers[index],
                            'original_index': index, 'pos': pos}
                        return
                for row, info in list(self.game_data['placed_neuro_mowers'].items()):
                    grid_y = self.ui_manager.neuro_placement_renderer.placement_grid_start_y
                    mower_rect = pygame.Rect(PLACEMENT_ZONE_X, grid_y + row * PLACEMENT_GRID_CELL_H,
                                             PLACEMENT_GRID_CELL_W, PLACEMENT_GRID_CELL_H)
                    if mower_rect.collidepoint(pos):
                        self.sound_manager.play_sfx('purchase')
                        self.game_data['dragged_mower'] = self.game_data['placed_neuro_mowers'].pop(row)
                        self.game_data['dragged_mower']['pos'] = pos
                        return

        if event.type == pygame.MOUSEMOTION and dragged_mower:
            dragged_mower['pos'] = event.pos

        if event.type == pygame.MOUSEBUTTONUP and event.button == 1 and dragged_mower:
            pos = event.pos
            grid_y = self.ui_manager.neuro_placement_renderer.placement_grid_start_y
            placement_area = pygame.Rect(PLACEMENT_ZONE_X, grid_y, PLACEMENT_GRID_CELL_W,
                                         GRID_ROWS * PLACEMENT_GRID_CELL_H)

            if placement_area.collidepoint(pos):
                row = int((pos[1] - grid_y) // PLACEMENT_GRID_CELL_H)
                if 0 <= row < GRID_ROWS and row not in self.game_data['placed_neuro_mowers']:
                    self.sound_manager.play_sfx('purchase')
                    self.game_data['placed_neuro_mowers'][row] = {'type': dragged_mower['type'],
                                                                  'original_index': dragged_mower['original_index']}

            self.game_data['dragged_mower'] = None

    def _playing_loop(self):
        battle_manager = self.game_data['battle_manager']
        for event in pygame.event.get():
            if event.type == pygame.QUIT: self.running = False
            action = battle_manager.handle_event(event)
            if action == 'PAUSE':
                self.sound_manager.play_sfx('button')
                pygame.mixer.pause();
                pygame.mixer.music.pause()
                self.state = 'PAUSED'

        battle_manager.update()
        battle_manager.draw(self.screen)

        if battle_manager.level_manager.is_complete():
            self._handle_level_win()
        elif battle_manager.is_game_over:
            self._handle_level_loss()

    def _handle_level_win(self):
        """Обрабатывает логику победы в уровне."""
        self.game_data['stipend'] = self.game_data['prep_manager'].stipend + LEVEL_WIN_STIPEND_BONUS
        if self.game_data['current_level_id'] == self.game_data['max_level_unlocked'] and self.game_data[
            'current_level_id'] > 0:
            if self.game_data['max_level_unlocked'] < len(LEVELS) - 1:
                self.game_data['max_level_unlocked'] += 1

        self.game_data['level_clear_timer'] = pygame.time.get_ticks()
        self.game_data['victory_sound_played'] = False
        self.state = 'LEVEL_CLEAR'

    def _handle_level_loss(self):
        """Обрабатывает логику поражения."""
        self.sound_manager.stop_all_sfx()
        self.sound_manager.stop_music()
        self.sound_manager.play_sfx('lose')
        self.state = 'GAME_OVER'

    def _level_clear_loop(self):
        now = pygame.time.get_ticks()
        if not self.game_data.get('victory_sound_played') and now - self.game_data.get('level_clear_timer',
                                                                                       0) > VICTORY_SOUND_DELAY:
            self.sound_manager.stop_all_sfx()
            self.sound_manager.stop_music()
            self.sound_manager.play_sfx('win')
            self.game_data['victory_sound_played'] = True
            self.game_data['level_clear_timer'] = now

        sfx_len = self.sound_manager.get_sfx_length('win')
        duration = sfx_len * 1000 if sfx_len > 0 else LEVEL_CLEAR_DEFAULT_DURATION

        if self.game_data.get('victory_sound_played') and now - self.game_data.get('level_clear_timer', 0) > duration:
            is_last_level = self.game_data['current_level_id'] >= len(LEVELS) - 1
            self.state = "GAME_VICTORY" if is_last_level else 'LEVEL_VICTORY'
            return

        self.game_data['battle_manager'].draw_world(self.screen)
        self.ui_manager.draw_level_clear_message(self.screen)

    # --- Универсальные методы для простых меню (DRY) ---

    def _create_menu_buttons(self, button_specs):
        """Создает словарь с Rect'ами кнопок для меню."""
        buttons = {}
        for i, (text, size) in enumerate(button_specs):
            rect = pygame.Rect((0, 0), size)
            v_offset = PAUSE_MENU_V_SPACING * (i - (len(button_specs) - 1) / 2)
            rect.center = (SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 + v_offset)
            buttons[text] = rect
        return buttons

    def _generic_menu_loop(self, title, button_specs, background_surface=None, next_states=None):
        """Универсальный цикл для всех простых меню (пауза, победа, поражение)."""
        buttons = self._create_menu_buttons(button_specs)

        if background_surface:
            self.screen.blit(background_surface, (0, 0))

        self.ui_manager.draw_menu(self.screen, title, buttons)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE and title == "Пауза":
                self.state = 'PLAYING'
                pygame.mixer.unpause();
                pygame.mixer.music.unpause()

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                for text, rect in buttons.items():
                    if rect.collidepoint(event.pos):
                        self.sound_manager.play_sfx('button')
                        pygame.time.delay(BUTTON_CLICK_DELAY)
                        if next_states and text in next_states:
                            action = next_states[text]
                            if callable(action):
                                action()
                            else:
                                self.state = action
                        return

    def _paused_loop(self):
        next_states = {
            "Продолжить": lambda: self._unpause_game(),
            "Рестарт": lambda: self._prepare_level(self.game_data['current_level_id']),
            "Главное меню": lambda: self._go_to_main_menu()
        }
        self.game_data['battle_manager'].draw_for_pause(self.screen)
        self._generic_menu_loop("Пауза", PAUSE_MENU_BUTTONS, None, next_states)

    def _game_over_loop(self):
        next_states = {
            "Попробовать снова": lambda: self._prepare_level(self.game_data['current_level_id']),
            "Главное меню": lambda: self._go_to_main_menu()
        }
        self._generic_menu_loop("ОТЧИСЛЕНИЕ!", GAME_OVER_BUTTONS, self.background, next_states)

    def _level_victory_loop(self):
        next_states = {
            "Следующий курс": lambda: self._go_to_main_menu(),
            "Главное меню": lambda: self._go_to_main_menu()
        }
        self._generic_menu_loop("КУРС ПРОЙДЕН!", LEVEL_VICTORY_BUTTONS, self.background, next_states)

    def _game_victory_loop(self):
        next_states = {"Главное меню": lambda: self._go_to_main_menu()}
        self._generic_menu_loop("ДИПЛОМ ЗАЩИЩЕН!", GAME_VICTORY_BUTTONS, self.background, next_states)

    # --- Вспомогательные методы для переходов ---

    def _unpause_game(self):
        pygame.mixer.unpause()
        pygame.mixer.music.unpause()
        self.state = "PLAYING"

    def _go_to_main_menu(self):
        self.sound_manager.stop_music()
        self.sound_manager.play_music('main_team')
        self.state = "MAIN_MENU"