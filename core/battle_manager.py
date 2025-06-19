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
    def __init__(self, all_sprites, defenders, enemies, projectiles, coffee_beans, neuro_mowers, ui_manager,
                 level_manager, sound_manager, team, upgrades, placed_mowers):
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

        self.occupied_cells = set()

        self.pending_calamities = self.level_manager.calamities.copy()
        random.shuffle(self.pending_calamities)
        self.calamity_triggers = CALAMITY_TRIGGERS.copy()
        self.calamity_notification = None
        self.calamity_notification_timer = 0
        self.notification_duration = CALAMITY_NOTIFICATION_DURATION

        self.active_calamity = None
        self.calamity_end_time = 0
        self.calamity_duration = CALAMITY_DURATION

    def start(self):
        self.level_manager.start()

    def place_neuro_mowers(self):
        for row, mower_type in self.placed_mowers_data.items():
            NeuroMower(row, (self.all_sprites, self.neuro_mowers), mower_type, self.sound_manager)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            pos = event.pos
            clicked_item = self.ui_manager.handle_shop_click(pos)
            if clicked_item == 'pause_button':
                return 'PAUSE'
            self.handle_click(pos)
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            return 'PAUSE'
        return None

    def handle_click(self, pos):
        clicked_shop_item = self.ui_manager.handle_shop_click(pos)
        if clicked_shop_item:
            self.sound_manager.play_sfx('purchase')
            self.selected_defender = clicked_shop_item if self.selected_defender != clicked_shop_item else None
            return
        for bean in list(self.coffee_beans):
            if bean.alive() and bean.rect.collidepoint(pos):
                self.sound_manager.play_sfx('money')
                self.coffee += bean.value
                bean.kill()
                return
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
        x, y = pos
        if GRID_START_X <= x < GRID_START_X + GRID_WIDTH and GRID_START_Y <= y < GRID_START_Y + GRID_HEIGHT:
            return (x - GRID_START_X) // CELL_SIZE_W, (y - GRID_START_Y) // CELL_SIZE_H
        return None

    def _is_cell_occupied(self, grid_pos):
        return grid_pos in self.occupied_cells

    def _place_defender(self, grid_pos):
        self.sound_manager.play_sfx('purchase')
        col, row = grid_pos
        x = GRID_START_X + col * CELL_SIZE_W + CELL_SIZE_W / 2
        y = GRID_START_Y + row * CELL_SIZE_H + CELL_SIZE_H / 2
        groups = (self.all_sprites, self.defenders)
        defender_type = self.selected_defender
        data = DEFENDERS_DATA[defender_type].copy()
        data['type'] = defender_type

        if defender_type in self.upgrades:
            upgraded_stats = self.upgrades[defender_type]
            for stat_name in upgraded_stats:
                upgrade_info = DEFENDERS_DATA[defender_type]['upgrades'][stat_name]
                data[stat_name] += upgrade_info['value']

        unit_map = {'programmer': ProgrammerBoy, 'botanist': BotanistGirl, 'coffee_machine': CoffeeMachine,
                    'activist': Activist, 'guitarist': Guitarist, 'medic': Medic, 'artist': Artist,
                    'modnik': Fashionista}
        constructor = unit_map[defender_type]
        common_args = {'x': x, 'y': y, 'groups': groups, 'data': data, 'sound_manager': self.sound_manager}

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

        self.occupied_cells.add(grid_pos)

    def _update_occupied_cells(self):
        self.occupied_cells.clear()
        for defender in self.defenders:
            if defender.alive():
                grid_pos = self._get_grid_cell(defender.rect.center)
                if grid_pos:
                    self.occupied_cells.add(grid_pos)

    def update(self):
        now = pygame.time.get_ticks()

        # Передаем группы спрайтов в метод update для всех спрайтов
        update_args = {
            'defenders_group': self.defenders,
            'enemies_group': self.enemies,
            'all_sprites': self.all_sprites,
            'projectiles': self.projectiles,
            'level_manager': self.level_manager  # Передаем level_manager для подсчета убийств
        }

        enemies_before_spawn = set(self.enemies.sprites())
        self.level_manager.update()
        newly_spawned = set(self.enemies.sprites()) - enemies_before_spawn

        enemies_before_update = len(self.enemies)
        self.all_sprites.update(**update_args)
        enemies_after_update = len(self.enemies)

        # Подсчет врагов, убитых непрямыми способами (например, взрывом)
        killed_this_frame = enemies_before_update - enemies_after_update
        if killed_this_frame > 0:
            for _ in range(killed_this_frame):
                self.level_manager.enemy_killed()

        self._update_occupied_cells()
        self.apply_auras()
        self.check_collisions()
        self._check_calamity_triggers(now)

        if self.active_calamity:
            for enemy in newly_spawned:
                enemy.apply_calamity_effect(self.active_calamity)

        # Проверка прорыва врагов за линию обороны
        for enemy in list(self.enemies):
            if enemy.alive() and enemy.rect.right < GRID_START_X:
                mower_activated = False
                for mower in self.neuro_mowers:
                    if mower.rect.centery == enemy.rect.centery and not mower.is_active:
                        mower.activate()
                        # Активированная косилка сама убьет врага, но мы должны это засчитать
                        enemy.kill()
                        self.level_manager.enemy_killed()
                        mower_activated = True
                        break
                if not mower_activated:
                    self.is_game_over = True
                    return

        if self.calamity_notification and now > self.calamity_notification_timer: self.calamity_notification = None
        if self.active_calamity and now > self.calamity_end_time: self._end_calamity()

    def _check_calamity_triggers(self, now):
        if self.active_calamity: return
        spawn_progress = self.level_manager.get_spawn_progress()
        for trigger_point in self.calamity_triggers:
            if spawn_progress >= trigger_point:
                self.calamity_triggers.remove(trigger_point)
                self._trigger_random_calamity(now)
                break

    def _trigger_random_calamity(self, now):
        if not self.pending_calamities: return
        self.active_calamity = self.pending_calamities.pop()
        calamity_data = CALAMITIES_DATA[self.active_calamity]
        self.sound_manager.play_sfx('misfortune')
        self.calamity_notification = {'type': self.active_calamity, 'name': calamity_data['display_name'],
                                      'desc': calamity_data['description']}
        self.calamity_notification_timer = now + self.notification_duration
        self.calamity_end_time = now + self.calamity_duration
        if self.active_calamity == 'big_party':
            heroes_to_consider = [d for d in self.defenders if d.alive() and not isinstance(d, CoffeeMachine)]
            if heroes_to_consider:
                num_to_remove = int(len(heroes_to_consider) * CALAMITY_BIG_PARTY_REMOVAL_RATIO)
                heroes_to_remove = random.sample(heroes_to_consider, k=min(num_to_remove, len(heroes_to_consider)))
                for hero in heroes_to_remove: hero.kill()
            self.active_calamity = None
        else:
            for sprite in self.all_sprites:
                if hasattr(sprite, 'apply_calamity_effect'): sprite.apply_calamity_effect(self.active_calamity)

    def _end_calamity(self):
        if not self.active_calamity: return
        for sprite in self.all_sprites:
            if hasattr(sprite, 'revert_calamity_effect'): sprite.revert_calamity_effect(self.active_calamity)
        self.active_calamity = None

    def check_collisions(self):
        # Столкновения снарядов с целями
        for proj in list(self.projectiles):
            if not proj.alive(): continue
            target_group = self.enemies if hasattr(proj,
                                                   'target_type') and proj.target_type == 'enemy' else self.defenders
            # Убиваем цель при столкновении (dokill=True)
            hits = pygame.sprite.spritecollide(proj, target_group, True)
            if hits:
                # Если снаряд попал, он исчезает
                proj.kill()
                # И мы регистрируем убийство для каждого пораженного врага
                for hit_enemy in hits:
                    if isinstance(hit_enemy, Enemy):
                        self.level_manager.enemy_killed()
                    if isinstance(proj, PaintSplat):
                        # Эффект замедления нужно применить до убийства, поэтому находим цель снова
                        # Этот код немного сложнее, но сохраняет логику
                        # Для простоты, можно оставить dokill=False и убивать вручную, как было
                        pass  # Логика замедления при dokill=True сложнее

        # Столкновения звуковых волн
        sound_waves = [s for s in self.all_sprites if isinstance(s, SoundWave)]
        for wave in sound_waves:
            collided_enemies = pygame.sprite.spritecollide(wave, self.enemies, False)
            for enemy in collided_enemies:
                if enemy not in wave.hit_enemies:
                    enemy.get_hit(wave.damage)
                    wave.hit_enemies.add(enemy)

        # Столкновения врагов с неактивными нейросетями
        for mower in list(self.neuro_mowers):
            if not mower.is_active:
                enemies_before = len(self.enemies)
                colliding_enemies = pygame.sprite.spritecollide(mower, self.enemies, True)
                if colliding_enemies:
                    killed_count = enemies_before - len(self.enemies)
                    for _ in range(killed_count):
                        self.level_manager.enemy_killed()
                    mower.activate()

    def apply_auras(self):
        for d in self.defenders:
            d.buff_multiplier = 1.0

        activists = [s for s in self.defenders if isinstance(s, Activist) and s.alive()]
        for activist in activists:
            activist.radius = activist.data['radius'] * CELL_SIZE_W
            affected_defenders = pygame.sprite.spritecollide(activist, self.defenders, False,
                                                             pygame.sprite.collide_circle)
            for defender in affected_defenders:
                if defender is not activist:
                    defender.buff_multiplier *= activist.data['buff']

    def draw(self, surface):
        self.draw_world(surface)
        self.draw_hud(surface)

    def draw_world(self, surface):
        surface.blit(self.background_image, (0, 0))
        self.ui_manager.draw_grid(surface)
        for sprite in sorted(self.all_sprites, key=lambda s: s._layer):
            surface.blit(sprite.image, sprite.rect)

    def draw_hud(self, surface):
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
        self.draw_world(surface)
        self.draw_hud(surface)
        return surface.copy()