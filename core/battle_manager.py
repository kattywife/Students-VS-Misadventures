# core/battle_manager.py

import pygame
import random
from data.settings import *
from data.assets import load_image
from entities.defenders import Defender, ProgrammerBoy, BotanistGirl, CoffeeMachine, Activist, Guitarist, Medic, Artist, \
    Fashionista
from entities.enemies import Enemy
from entities.projectiles import Integral, PaintSplat, SoundWave
from entities.other_sprites import NeuroMower, CoffeeBean


class BattleManager:
    """
    Управляет всей логикой боевой фазы игры.
    Отвечает за размещение защитников, обновление состояния всех игровых объектов,
    обработку столкновений, запуск "напастей" (calamities) и проверку условий
    победы или поражения на уровне.
    """
    def __init__(self, all_sprites, defenders, enemies, projectiles, coffee_beans, neuro_mowers, ui_manager,
                 level_manager, sound_manager, team, upgrades, placed_mowers):
        """
        Инициализирует менеджер боя.

        Args:
            all_sprites (pygame.sprite.LayeredUpdates): Группа для всех спрайтов.
            defenders (pygame.sprite.Group): Группа для спрайтов защитников.
            enemies (pygame.sprite.Group): Группа для спрайтов врагов.
            projectiles (pygame.sprite.Group): Группа для спрайтов снарядов.
            coffee_beans (pygame.sprite.Group): Группа для спрайтов кофейных зерен.
            neuro_mowers (pygame.sprite.Group): Группа для спрайтов нейросетей.
            ui_manager (UIManager): Менеджер интерфейса для отрисовки HUD.
            level_manager (LevelManager): Менеджер, управляющий волнами врагов.
            sound_manager (SoundManager): Менеджер для воспроизведения звуков.
            team (list): Список типов защитников, выбранных игроком.
            upgrades (dict): Словарь с улучшениями для защитников.
            placed_mowers (dict): Словарь с размещенными нейросетями {ряд: тип}.
        """
        self.all_sprites = all_sprites
        self.defenders = defenders
        self.enemies = enemies
        self.projectiles = projectiles
        self.coffee_beans = coffee_beans
        self.neuro_mowers = neuro_mowers
        self.ui_manager = ui_manager
        self.level_manager = level_manager
        self.sound_manager = sound_manager
        self.is_game_over = False
        self.team_data = team
        self.upgrades = upgrades
        self.placed_mowers_data = placed_mowers
        self.coffee = level_manager.level_data.get('start_coffee', 150)
        self.selected_defender = None

        self.background_image = load_image('battle_background.png', DEFAULT_COLORS['background'],
                                           (SCREEN_WIDTH, SCREEN_HEIGHT))

        self.ui_manager.create_battle_shop(self.team_data)
        self.place_neuro_mowers()

        # --- Инициализация системы "Напастей" (Calamities) ---
        self.pending_calamities = self.level_manager.calamities.copy()
        random.shuffle(self.pending_calamities)
        self.calamity_triggers = CALAMITY_TRIGGERS.copy()
        self.calamity_notification = None
        self.calamity_notification_timer = 0
        self.notification_duration = CALAMITY_NOTIFICATION_DURATION

        self.active_calamity = None
        self.calamity_end_time = 0
        self.calamity_duration = CALAMITY_DURATION

    def _get_walkable_grid(self):
        """Создает 2D-сетку проходимости, где 0 - свободно, 1 - препятствие."""
        grid = [[0 for _ in range(GRID_COLS)] for _ in range(GRID_ROWS)]
        for defender in self.defenders:
            if defender.alive():
                # Конвертируем пиксельные координаты в координаты сетки
                col = int((defender.rect.centerx - GRID_START_X) / CELL_SIZE_W)
                row = int((defender.rect.centery - GRID_START_Y) / CELL_SIZE_H)
                if 0 <= row < GRID_ROWS and 0 <= col < GRID_COLS:
                    grid[row][col] = 1  # 1 означает препятствие
        return grid

    def start(self):
        """Запускает начало боя, активируя LevelManager."""
        self.level_manager.start()

    def place_neuro_mowers(self):
        """Размещает нейросети-газонокосилки на поле в соответствии с выбором игрока."""
        for row, mower_type in self.placed_mowers_data.items():
            NeuroMower(row, (self.all_sprites, self.neuro_mowers), mower_type, self.sound_manager)

    def handle_event(self, event):
        """
        Обрабатывает пользовательский ввод во время боя.

        Args:
            event (pygame.event.Event): Событие Pygame.

        Returns:
            str | None: 'PAUSE', если игра должна быть поставлена на паузу, иначе None.
        """
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            pos = event.pos
            # Обработка клика по кнопке паузы делегирована UIManager'у
            clicked_item = self.ui_manager.handle_shop_click(pos)
            if clicked_item == 'pause_button':
                return 'PAUSE'
            self.handle_click(pos)
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            return 'PAUSE'
        return None

    def handle_click(self, pos):
        """
        Обрабатывает клики мыши по игровому полю и интерфейсу.

        Args:
            pos (tuple): Координаты (x, y) клика мыши.
        """
        # 1. Клик по магазину
        clicked_shop_item = self.ui_manager.handle_shop_click(pos)
        if clicked_shop_item:
            self.sound_manager.play_sfx('purchase')
            # Выбор или отмена выбора юнита
            self.selected_defender = clicked_shop_item if self.selected_defender != clicked_shop_item else None
            return
        # 2. Клик по кофейному зерну
        for bean in list(self.coffee_beans):
            if bean.alive() and bean.rect.collidepoint(pos):
                self.sound_manager.play_sfx('money')
                self.coffee += bean.value
                bean.kill()
                return
        # 3. Клик по сетке для размещения юнита
        if self.selected_defender:
            cost = DEFENDERS_DATA[self.selected_defender]['cost']
            if self.coffee >= cost:
                grid_pos = self._get_grid_cell(pos)
                if grid_pos and not self._is_cell_occupied(grid_pos):
                    self.coffee -= cost
                    self._place_defender(grid_pos)
                    self.selected_defender = None
            else:
                self.sound_manager.play_sfx('no_money')
                self.selected_defender = None

    def _get_grid_cell(self, pos):
        """
        Преобразует координаты мыши в координаты ячейки на сетке.

        Args:
            pos (tuple): Координаты (x, y) клика мыши.

        Returns:
            tuple | None: Кортеж (колонка, ряд) или None, если клик был вне сетки.
        """
        x, y = pos
        if GRID_START_X <= x < GRID_START_X + GRID_WIDTH and GRID_START_Y <= y < GRID_START_Y + GRID_HEIGHT:
            return (x - GRID_START_X) // CELL_SIZE_W, (y - GRID_START_Y) // CELL_SIZE_H
        return None

    def _is_cell_occupied(self, grid_pos):
        """
        Проверяет, занята ли указанная ячейка сетки другим защитником.

        Args:
            grid_pos (tuple): Кортеж (колонка, ряд) ячейки.

        Returns:
            bool: True, если ячейка занята, иначе False.
        """
        col, row = grid_pos
        new_defender_rect = pygame.Rect(
            GRID_START_X + col * CELL_SIZE_W,
            GRID_START_Y + row * CELL_SIZE_H,
            CELL_SIZE_W,
            CELL_SIZE_H
        )
        for defender in self.defenders:
            if defender.alive() and defender.rect.colliderect(new_defender_rect):
                return True
        return False

    def _place_defender(self, grid_pos):
        """
        Создает и размещает экземпляр защитника на поле.

        Args:
            grid_pos (tuple): Кортеж (колонка, ряд) для размещения.
        """
        self.sound_manager.play_sfx('purchase')
        col, row = grid_pos
        x = GRID_START_X + col * CELL_SIZE_W + CELL_SIZE_W / 2
        y = GRID_START_Y + row * CELL_SIZE_H + CELL_SIZE_H / 2
        groups = (self.all_sprites, self.defenders)
        defender_type = self.selected_defender
        data = DEFENDERS_DATA[defender_type].copy()
        data['type'] = defender_type

        # Применяет улучшения, если они были куплены
        if defender_type in self.upgrades:
            upgraded_stats = self.upgrades[defender_type]
            for stat_name in upgraded_stats:
                upgrade_info = DEFENDERS_DATA[defender_type]['upgrades'][stat_name]
                data[stat_name] += upgrade_info['value']

        # Карта для сопоставления типа юнита с его классом
        unit_map = {'programmer': ProgrammerBoy, 'botanist': BotanistGirl, 'coffee_machine': CoffeeMachine,
                    'activist': Activist, 'guitarist': Guitarist, 'medic': Medic, 'artist': Artist,
                    'modnik': Fashionista}
        constructor = unit_map[defender_type]
        common_args = {'x': x, 'y': y, 'groups': groups, 'data': data, 'sound_manager': self.sound_manager}

        # Аргументы, специфичные для каждого типа юнита
        specific_args = {
            'programmer': {'all_sprites': self.all_sprites, 'projectile_group': self.projectiles,
                           'enemies_group': self.enemies},
            'botanist': {'all_sprites': self.all_sprites, 'enemies_group': self.enemies},
            'coffee_machine': {'all_sprites': self.all_sprites, 'coffee_bean_group': self.coffee_beans},
            'activist': {'all_sprites': self.all_sprites},
            'guitarist': {'all_sprites': self.all_sprites, 'enemies_group': self.enemies},
            'medic': {'defenders_group': self.defenders},
            'artist': {'all_sprites': self.all_sprites, 'projectile_group': self.projectiles,
                       'enemies_group': self.enemies},
            'modnik': {'all_sprites': self.all_sprites, 'enemies_group': self.enemies}
        }
        all_args = {**common_args, **specific_args.get(defender_type, {})}

        defender = constructor(**all_args)
        if defender_type in self.upgrades: defender.is_upgraded = True

    def update(self):
        """Обновляет состояние всего боя за один кадр."""
        now = pygame.time.get_ticks()

        # Словарь с группами спрайтов, который передается в метод update каждого спрайта
        grid_state = self._get_walkable_grid()

        update_args = {
            'defenders_group': self.defenders,
            'enemies_group': self.enemies,
            'all_sprites': self.all_sprites,
            'projectiles': self.projectiles,
            'coffee_beans': self.coffee_beans,
            'neuro_mowers': self.neuro_mowers,
            'grid_state': grid_state
        }

        # Отслеживаем появление новых врагов для применения эффектов напастей
        enemies_before_spawn = set(self.enemies.sprites())
        self.level_manager.update()
        newly_spawned = set(self.enemies.sprites()) - enemies_before_spawn

        # Отслеживаем убийство врагов для прогресса уровня
        enemies_before_update = len(self.enemies)
        self.all_sprites.update(**update_args)
        enemies_after_update = len(self.enemies)

        killed_this_frame = enemies_before_update - enemies_after_update
        for _ in range(killed_this_frame):
            self.level_manager.enemy_killed()

        self.apply_auras()
        self.check_collisions()
        self._check_calamity_triggers(now)

        # Применяем эффект напасти к только что появившимся врагам
        if self.active_calamity:
            for enemy in newly_spawned:
                enemy.apply_calamity_effect(self.active_calamity)

        # Проверяем прорыв врагов (Game Over)
        for enemy in list(self.enemies):
            if enemy.alive() and enemy.rect.right < GRID_START_X:
                mower_activated = False
                for mower in self.neuro_mowers:
                    # Поиск нейросети на той же линии
                    if mower.rect.centery == enemy.rect.centery and not mower.is_active:
                        enemies_before_activation = set(self.enemies.sprites())
                        mower.activate(self.enemies, enemy)
                        enemies_after_activation = set(self.enemies.sprites())
                        killed_by_mower = len(enemies_before_activation - enemies_after_activation)
                        for _ in range(killed_by_mower):
                            self.level_manager.enemy_killed()
                        mower_activated = True
                        break
                # Если нейросети не было, игра проиграна
                if not mower_activated:
                    self.is_game_over = True
                    return

        # Обновление таймеров
        if self.calamity_notification and now > self.calamity_notification_timer: self.calamity_notification = None
        if self.active_calamity and now > self.calamity_end_time: self._end_calamity()

    def _check_calamity_triggers(self, now):
        """Проверяет, не достигнут ли прогресс спавна порога для запуска напасти."""
        if self.active_calamity: return
        spawn_progress = self.level_manager.get_spawn_progress()
        for trigger_point in self.calamity_triggers:
            if spawn_progress >= trigger_point:
                self.calamity_triggers.remove(trigger_point) # Удаляем, чтобы не сработал снова
                self._trigger_random_calamity(now)
                break

    def _trigger_random_calamity(self, now):
        """Запускает случайную напасть из списка доступных на уровне."""
        if not self.pending_calamities: return
        self.active_calamity = self.pending_calamities.pop()
        calamity_data = CALAMITIES_DATA[self.active_calamity]

        self.sound_manager.play_sfx('misfortune')

        # Создание уведомления для UI
        self.calamity_notification = {'type': self.active_calamity, 'name': calamity_data['display_name'],
                                      'desc': calamity_data['description']}
        self.calamity_notification_timer = now + self.notification_duration
        self.calamity_end_time = now + self.calamity_duration

        # Некоторые напасти имеют мгновенный эффект
        if self.active_calamity == 'big_party':
            heroes_to_consider = [d for d in self.defenders if d.alive() and not isinstance(d, CoffeeMachine)]
            if heroes_to_consider:
                num_to_remove = int(len(heroes_to_consider) * CALAMITY_BIG_PARTY_REMOVAL_RATIO)
                heroes_to_remove = random.sample(heroes_to_consider, k=min(num_to_remove, len(heroes_to_consider)))
                for hero in heroes_to_remove:
                    hero.kill()
            self.active_calamity = None # Эффект мгновенный
        else:
            # Применяем эффекты к существующим спрайтам
            for sprite in self.all_sprites:
                if hasattr(sprite, 'apply_calamity_effect'): sprite.apply_calamity_effect(self.active_calamity)

    def _end_calamity(self):
        """Завершает действие напасти и возвращает параметры спрайтов в норму."""
        if not self.active_calamity: return
        for sprite in self.all_sprites:
            if hasattr(sprite, 'revert_calamity_effect'): sprite.revert_calamity_effect(self.active_calamity)
        self.active_calamity = None

    def check_collisions(self):
        """Проверяет и обрабатывает все столкновения между игровыми объектами."""
        # --- Снаряды vs Цели ---
        for proj in list(self.projectiles):
            if not proj.alive():
                continue

            target_group = None
            if hasattr(proj, 'target_type'):
                if proj.target_type == 'enemy':
                    target_group = self.enemies
                elif proj.target_type == 'defender':
                    target_group = self.defenders

            if target_group:
                hits = pygame.sprite.spritecollide(proj, target_group, False)
                if hits:
                    target = hits[0]
                    if target.alive():
                        if isinstance(proj, PaintSplat): # Особый эффект для кляксы
                            target.slow_down(proj.artist.data['slow_factor'], proj.artist.data['slow_duration'])
                        target.get_hit(proj.damage)
                        proj.kill()

        # --- Звуковая волна vs Враги ---
        for wave in [s for s in self.all_sprites if isinstance(s, SoundWave)]:
            for enemy in self.enemies:
                if wave.rect.colliderect(enemy.rect) and enemy not in wave.hit_enemies:
                    enemy.get_hit(wave.damage)
                    wave.hit_enemies.add(enemy) # Помечаем, чтобы не ударить дважды

        # --- Враги vs Неактивные нейросети ---
        for mower in list(self.neuro_mowers):
            if not mower.is_active:
                colliding_enemies = pygame.sprite.spritecollide(mower, self.enemies, False)
                if colliding_enemies:
                    enemies_before_activation = set(self.enemies.sprites())
                    mower.activate(self.enemies, colliding_enemies[0])
                    enemies_after_activation = set(self.enemies.sprites())
                    killed_by_mower = len(enemies_before_activation - enemies_after_activation)
                    for _ in range(killed_by_mower):
                        self.level_manager.enemy_killed()

    def apply_auras(self):
        """Применяет эффекты от аур (например, от Активиста) к защитникам."""
        # Сначала сбрасываем баффы для всех
        for d in self.defenders:
            d.buff_multiplier = 1.0

        # Затем находим всех активистов и применяем их ауры
        for activist in [s for s in self.defenders if isinstance(s, Activist) and s.alive()]:
            for defender in self.defenders:
                if pygame.math.Vector2(activist.rect.center).distance_to(defender.rect.center) < activist.data[
                    'radius'] * CELL_SIZE_W:
                    defender.buff_multiplier *= activist.data['buff']

    def draw(self, surface):
        """Полная отрисовка боевого экрана."""
        self.draw_world(surface)
        self.draw_hud(surface)

    def draw_world(self, surface):
        """Отрисовка только игрового мира (фон, сетка, спрайты)."""
        surface.blit(self.background_image, (0, 0))
        self.ui_manager.draw_grid(surface)

        # Сортировка по `_layer` для правильного порядка отрисовки
        for sprite in sorted(self.all_sprites, key=lambda s: s._layer):
            surface.blit(sprite.image, sprite.rect)

    def draw_hud(self, surface):
        """Отрисовка только интерфейса (магазин, прогресс-бары, уведомления)."""
        spawn_progress = self.level_manager.get_spawn_progress()
        kill_progress = self.level_manager.get_kill_progress()
        spawn_data = self.level_manager.get_spawn_count_data()
        kill_data = self.level_manager.get_kill_count_data()
        self.ui_manager.draw_shop_and_hud(
            surface, self.selected_defender, self.coffee, self.upgrades,
            spawn_progress, kill_progress, spawn_data, kill_data,
            self.calamity_notification
        )

    def draw_for_pause(self, surface):
        """Отрисовка 'замороженного' кадра для меню паузы."""
        self.draw_world(surface)
        self.draw_hud(surface)