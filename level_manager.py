# level_manager.py

import pygame
import random
from levels import LEVELS
from sprites import Enemy, Calculus, Akadem
from settings import *


class LevelManager:
    def __init__(self, level_id, enemy_group, akadem_group, all_sprites_group):
        self.level_data = LEVELS.get(level_id, LEVELS[1])
        self.enemy_spawn_list = self.level_data['enemies'].copy()
        random.shuffle(self.enemy_spawn_list)

        self.enemy_group = enemy_group
        self.akadem_group = akadem_group
        self.all_sprites_group = all_sprites_group

        self.is_running = False

        self.total_enemies_in_level = len(self.enemy_spawn_list)
        self.enemies_killed = 0
        self.enemies_spawned = 0

        self.spawn_cooldown = 5000
        self.last_spawn_time = 0
        self.final_wave_threshold = 0.6
        self.in_final_wave = False

        self.setup_akadems()

    def start(self):
        self.is_running = True
        self.last_spawn_time = pygame.time.get_ticks()

    def enemy_killed(self):
        self.enemies_killed += 1

    def get_spawn_progress(self):
        """Возвращает прогресс спавна (0.0 до 1.0)."""
        if self.total_enemies_in_level == 0: return 1.0
        return self.enemies_spawned / self.total_enemies_in_level

    def get_kill_progress(self):
        """Возвращает прогресс убийств (0.0 до 1.0)."""
        if self.total_enemies_in_level == 0: return 1.0
        return self.enemies_killed / self.total_enemies_in_level

    def get_kill_count_data(self):
        """Возвращает данные для текстового счетчика БРС."""
        return self.enemies_killed, self.total_enemies_in_level
    def get_spawn_count_data(self):
        return self.enemies_spawned, self.total_enemies_in_level
    def get_enemy_types_for_level(self):
        if not self.level_data['enemies']: return []
        return sorted(list(set(enemy[0] for enemy in self.level_data['enemies'])))

    def setup_akadems(self):
        for i in range(GRID_ROWS):
            Akadem(i, (self.akadem_group, self.all_sprites_group))

    def update(self):
        if not self.is_running or not self.enemy_spawn_list: return

        now = pygame.time.get_ticks()

        if not self.in_final_wave and (self.enemies_spawned / self.total_enemies_in_level) >= self.final_wave_threshold:
            self.in_final_wave = True
            self.spawn_cooldown = 2000

        if now - self.last_spawn_time > self.spawn_cooldown:
            self.last_spawn_time = now
            enemy_type, row = self.enemy_spawn_list.pop(0)
            self.spawn_enemy(enemy_type, row)
            self.enemies_spawned += 1

    def spawn_enemy(self, enemy_type, row):
        groups = (self.enemy_group, self.all_sprites_group)
        if enemy_type == 'calculus':
            Calculus(row, groups)
        else:
            Enemy(row, groups, enemy_type)

    def is_complete(self):
        """
        Уровень считается пройденным, когда все враги из списка спавна выпущены,
        и на поле не осталось живых врагов.
        """
        all_spawned = len(self.enemy_spawn_list) == 0
        all_defeated = len(self.enemy_group) == 0
        return all_spawned and all_defeated and self.total_enemies_in_level > 0