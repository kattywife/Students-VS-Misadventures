# game_logic.py

import pygame
import sys
from settings import *
from sprites import *
from ui_manager import UIManager
from level_manager import LevelManager
from assets import load_image, load_sound, SOUNDS
from levels import LEVELS


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
        self.level_select_buttons = {}
        self.level_intro_button = None
        self.selected_defender = None
        self.control_buttons = {}

        self.state = 'START_SCREEN'
        self.level_clear_timer = 0
        self.level_clear_duration = 3000

        self._setup_sprite_groups()
        self._load_assets()

    def _load_assets(self):
        load_sound('button', 'pressing a button.mp3')
        load_sound('purchase', 'purchase and landing of the hero.mp3')
        load_sound('damage', 'damage.mp3')
        load_sound('eating', 'eating.mp3')
        load_sound('scream', 'scream.mp3')
        load_sound('enemy_dead', 'enemy_dead.mp3')
        load_sound('hero_dead', 'hero_dead.mp3')
        load_sound('money', 'money.mp3')
        load_sound('win', 'win.mp3')

        if SOUNDS.get('win'):
            self.level_clear_duration = SOUNDS['win'].get_length() * 1000

    def _setup_sprite_groups(self):
        self.all_sprites = pygame.sprite.Group()
        self.defenders = pygame.sprite.Group()
        self.enemies = pygame.sprite.Group()
        self.projectiles = pygame.sprite.Group()
        self.coffee_beans = pygame.sprite.Group()
        self.akadems = pygame.sprite.Group()

    def _prepare_level(self, level_id):
        self.current_level_id = level_id
        self._setup_sprite_groups()
        self.level_manager = LevelManager(level_id, self.enemies, self.akadems, self.all_sprites)
        self.coffee_beans_amount = self.level_manager.level_data['start_coffee']
        self.state = 'LEVEL_INTRO'

    def _start_level(self):
        self.level_manager.start()
        self.state = 'PLAYING'

    def run(self):
        while self.running:
            try:
                self.dt = self.clock.tick(FPS) / 1000.0

                if self.state == 'START_SCREEN':
                    self._start_screen_loop()
                elif self.state == 'MAIN_MENU':
                    self._main_menu_loop()
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
            except Exception as e:
                print(f"An error occurred: {e}")
                import traceback
                traceback.print_exc()
                self.running = False
        pygame.quit()
        sys.exit()

    def _handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            if self.state == 'PLAYING':
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    if SOUNDS.get('button'): SOUNDS['button'].play()
                    pygame.time.delay(100)
                    self.state = 'PAUSED'
                    pygame.mixer.pause()
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    self._handle_playing_clicks(event.pos)

    def _handle_playing_clicks(self, pos):
        if self.ui_manager.pause_button_rect.collidepoint(pos):
            if SOUNDS.get('button'): SOUNDS['button'].play()
            pygame.time.delay(100)
            self.state = 'PAUSED'
            pygame.mixer.pause()
            return

        clicked_shop_item = self.ui_manager.handle_shop_click(pos)
        if clicked_shop_item:
            if SOUNDS.get('purchase'): SOUNDS['purchase'].play()
            if self.selected_defender == clicked_shop_item:
                self.selected_defender = None
            else:
                self.selected_defender = clicked_shop_item
            return

        for bean in list(self.coffee_beans):
            if bean.alive() and bean.rect.collidepoint(pos):
                if SOUNDS.get('money'): SOUNDS['money'].play()
                self.coffee_beans_amount += bean.value
                bean.kill()
                return

        if self.selected_defender:
            cost = DEFENDERS_DATA[self.selected_defender]['cost']
            if self.coffee_beans_amount >= cost:
                grid_pos = self._get_grid_cell(pos)
                if grid_pos and not self._is_cell_occupied(grid_pos):
                    self.coffee_beans_amount -= cost
                    self._place_defender(grid_pos)
                    self.selected_defender = None

    def _get_grid_cell(self, pos):
        x, y = pos
        if GRID_START_X <= x < GRID_START_X + GRID_WIDTH and GRID_START_Y <= y < GRID_START_Y + GRID_HEIGHT:
            col = (x - GRID_START_X) // CELL_SIZE_W
            row = (y - GRID_START_Y) // CELL_SIZE_H
            return col, row
        return None

    def _is_cell_occupied(self, grid_pos):
        col, row = grid_pos
        cell_center_x = GRID_START_X + col * CELL_SIZE_W + CELL_SIZE_W / 2
        cell_center_y = GRID_START_Y + row * CELL_SIZE_H + CELL_SIZE_H / 2
        for defender in self.defenders:
            if defender.alive() and defender.rect.collidepoint(cell_center_x, cell_center_y):
                return True
        return False

    def _place_defender(self, grid_pos):
        if SOUNDS.get('purchase'): SOUNDS['purchase'].play()
        col, row = grid_pos
        x = GRID_START_X + col * CELL_SIZE_W + CELL_SIZE_W / 2
        y = GRID_START_Y + row * CELL_SIZE_H + CELL_SIZE_H / 2

        groups = (self.all_sprites, self.defenders)
        if self.selected_defender == 'programmer':
            ProgrammerBoy(x, y, groups, self.all_sprites, self.projectiles, self.enemies)
        elif self.selected_defender == 'botanist':
            BotanistGirl(x, y, groups, self.all_sprites, self.enemies)
        elif self.selected_defender == 'coffee_machine':
            CoffeeMachine(x, y, groups, self.all_sprites, self.coffee_beans)

    def _update(self):
        if self.level_manager.is_complete():
            if self.state != 'LEVEL_CLEAR':
                pygame.mixer.stop()
                if SOUNDS.get('win'): SOUNDS['win'].play()
                self.level_clear_timer = pygame.time.get_ticks()
                self.state = 'LEVEL_CLEAR'
            return

        # ----- ВОТ ИСПРАВЛЕНИЕ: Правильный порядок действий для счетчика -----
        # 1. Запоминаем, сколько всего врагов на поле ДО всех действий
        enemies_before_update = len(self.enemies)

        # 2. Обновляем все спрайты (атаки, движение, смерть от урона)
        self.all_sprites.update(self.defenders)

        # 3. Проверяем столкновения и другие причины смерти
        for proj in list(self.projectiles):
            if proj.alive():
                hit_list = pygame.sprite.spritecollide(proj, self.enemies, False)
                if hit_list:
                    if hit_list[0].alive():
                        hit_list[0].get_hit(proj.damage)
                    proj.kill()

        for akadem in list(self.akadems):
            if akadem.is_active:
                pygame.sprite.spritecollide(akadem, self.enemies, True)

        for enemy in list(self.enemies):
            if enemy.alive() and enemy.rect.right < GRID_START_X:
                enemy_cleared = False
                for akadem in list(self.akadems):
                    if akadem.rect.centery == enemy.rect.centery and not akadem.is_active:
                        akadem.activate()
                        enemy.kill()
                        enemy_cleared = True
                        break
                if not enemy_cleared and enemy.alive():
                    pygame.mixer.stop()
                    self.state = 'GAME_OVER'
                    return

        # 4. Сравниваем количество врагов "до" и "после" всех действий битвы
        enemies_after_update = len(self.enemies)
        killed_this_frame = enemies_before_update - enemies_after_update
        if killed_this_frame > 0:
            for _ in range(killed_this_frame):
                self.level_manager.enemy_killed()

        # 5. И только ПОСЛЕ всего этого спавним новых врагов на следующий кадр
        self.level_manager.update()
        # --------------------------------------------------------------------

    def _draw(self):
        self.screen.blit(self.background, (0, 0))
        self.ui_manager.draw_grid()
        self.all_sprites.draw(self.screen)
        self.ui_manager.draw_shop(self.selected_defender, self.coffee_beans_amount)

        spawn_progress = self.level_manager.get_spawn_progress()
        kill_progress = self.level_manager.get_kill_progress()
        spawn_count_data = self.level_manager.get_spawn_count_data()
        kill_count_data = self.level_manager.get_kill_count_data()
        self.ui_manager.draw_hud(spawn_progress, kill_progress, spawn_count_data, kill_count_data)

        pygame.display.flip()

    def _playing_loop(self):
        self._handle_events()
        self._update()
        self._draw()

    def _level_clear_loop(self):
        now = pygame.time.get_ticks()
        if now - self.level_clear_timer > self.level_clear_duration:
            self.state = 'LEVEL_VICTORY'
            return

        self._draw()
        self.ui_manager.draw_level_clear_message()
        pygame.display.flip()

    def _menu_loop_template(self, title, buttons_config, next_states):
        buttons = {}
        for i, (text, size) in enumerate(buttons_config.items()):
            rect = pygame.Rect(0, 0, size[0], size[1])
            rect.center = (SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 + i * 100)
            buttons[text] = rect

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                for text, rect in buttons.items():
                    if rect.collidepoint(event.pos):
                        if SOUNDS.get('button'): SOUNDS['button'].play()
                        pygame.time.delay(100)
                        if text == "Выход":
                            self.running = False
                        elif text == "Продолжить":
                            pygame.mixer.unpause()
                            self.state = next_states.get(text)
                        else:
                            pygame.mixer.stop()
                            self.state = next_states.get(text)

        self.screen.blit(self.background, (0, 0))
        if title == "Пауза":
            self.all_sprites.draw(self.screen)

        self.ui_manager.draw_menu(title, buttons)
        pygame.display.flip()

    def _start_screen_loop(self):
        self._menu_loop_template(
            "Студенты против Злоключений",
            {"Начать обучение": (400, 80), "Выход": (400, 80)},
            {"Начать обучение": "MAIN_MENU"}
        )

    def _main_menu_loop(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                for level_id, rect in self.level_select_buttons.items():
                    if rect.collidepoint(event.pos):
                        if SOUNDS.get('button'): SOUNDS['button'].play()
                        pygame.time.delay(100)
                        self._prepare_level(level_id)
                        return

                for text, rect in self.control_buttons.items():
                    if rect.collidepoint(event.pos):
                        if SOUNDS.get('button'): SOUNDS['button'].play()
                        pygame.time.delay(100)
                        if text == "Выход":
                            self.running = False
                        elif text == "Настройки":
                            print("Settings button clicked!")

        self.screen.blit(self.background, (0, 0))
        self.level_select_buttons, self.control_buttons = self.ui_manager.draw_main_menu(self.max_level_unlocked)
        pygame.display.flip()

    def _level_intro_loop(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.level_intro_button and self.level_intro_button.collidepoint(event.pos):
                    if SOUNDS.get('button'): SOUNDS['button'].play()
                    pygame.time.delay(100)
                    self._start_level()
                    return

        self.screen.blit(self.background, (0, 0))
        enemy_types = self.level_manager.get_enemy_types_for_level()
        self.level_intro_button = self.ui_manager.draw_level_intro(enemy_types)
        pygame.display.flip()

    def _paused_loop(self):
        self._menu_loop_template(
            "Пауза",
            {"Продолжить": (300, 80), "Главное меню": (400, 80)},
            {"Продолжить": "PLAYING", "Главное меню": "MAIN_MENU"}
        )

    def _game_over_loop(self):
        pygame.mixer.stop()
        self._menu_loop_template(
            "ОТЧИСЛЕНИЕ!",
            {"Попробовать снова": (400, 80), "Главное меню": (400, 80)},
            {"Попробовать снова": "MAIN_MENU", "Главное меню": "MAIN_MENU"}
        )

    def _level_victory_loop(self):
        if self.current_level_id == self.max_level_unlocked and self.max_level_unlocked < len(LEVELS):
            self.max_level_unlocked += 1

        if self.current_level_id >= len(LEVELS):
            self.state = "GAME_VICTORY"
            return

        self._menu_loop_template(
            "КУРС ПРОЙДЕН!",
            {"Следующий курс": (400, 80), "Главное меню": (400, 80)},
            {"Следующий курс": "MAIN_MENU", "Главное меню": "MAIN_MENU"}
        )

    def _game_victory_loop(self):
        pygame.mixer.stop()
        self._menu_loop_template(
            "ДИПЛОМ ЗАЩИЩЕН!",
            {"Главное меню": (400, 80)},
            {"Главное меню": "MAIN_MENU"}
        )