# core/level_manager.py

import pygame
import random
from data.levels import LEVELS
from entities.enemies import Enemy, Calculus, MathTeacher, Addict, Thief
from data.settings import *


class LevelManager:
    def __init__(self, level_id, enemy_group=None, all_sprites_group=None, sound_manager=None):
        self.level_data = LEVELS.get(level_id, LEVELS[1])
        self.enemy_spawn_list = self.level_data['enemies'].copy()
        random.shuffle(self.enemy_spawn_list)

        self.enemy_group = enemy_group
        self.all_sprites_group = all_sprites_group
        self.sound_manager = sound_manager
        self.calamities = self.level_data.get('calamities', [])

        self.is_running = False

        self.total_enemies_in_level = len(self.enemy_spawn_list)
        self.enemies_killed = 0
        self.enemies_spawned = 0

        self.spawn_cooldown = INITIAL_SPAWN_COOLDOWN
        self.last_spawn_time = 0
        self.final_wave_threshold = FINAL_WAVE_THRESHOLD
        self.in_final_wave = False

    def start(self):
        self.is_running = True
        self.last_spawn_time = pygame.time.get_ticks()

    def enemy_killed(self):
        self.enemies_killed += 1

    def get_spawn_progress(self):
        if self.total_enemies_in_level == 0: return 1.0
        return self.enemies_spawned / self.total_enemies_in_level

    def get_kill_progress(self):
        if self.total_enemies_in_level == 0: return 1.0
        return self.enemies_killed / self.total_enemies_in_level

    def get_kill_count_data(self):
        return self.enemies_killed, self.total_enemies_in_level

    def get_spawn_count_data(self):
        return self.enemies_spawned, self.total_enemies_in_level

    def get_enemy_types_for_level(self):
        if not self.level_data['enemies']: return []
        return sorted(list(set(enemy[0] for enemy in self.level_data['enemies'])))

    def get_calamity_types_for_level(self):
        return self.level_data.get('calamities', [])

    def update(self):
        # --- ИСПРАВЛЕНИЕ: Проверяем на 'is None' вместо 'not' ---
        # Эта проверка теперь корректно отличает отсутствие группы от пустой группы.
        if not self.is_running or not self.enemy_spawn_list or self.enemy_group is None:
            return

        now = pygame.time.get_ticks()

        if not self.in_final_wave and self.total_enemies_in_level > 0 and \
                (self.enemies_spawned / self.total_enemies_in_level) >= self.final_wave_threshold:
            self.in_final_wave = True
            self.spawn_cooldown = FINAL_WAVE_SPAWN_COOLDOWN

        if now - self.last_spawn_time > self.spawn_cooldown:
            self.last_spawn_time = now
            enemy_type, row = self.enemy_spawn_list.pop(0)
            self.spawn_enemy(enemy_type, row)
            self.enemies_spawned += 1

    def spawn_enemy(self, enemy_type, row):
        groups = (self.enemy_group, self.all_sprites_group)

        enemy_map = {
            'calculus': Calculus,
            'math_teacher': MathTeacher,
            'addict': Addict,
            'thief': Thief
        }

        enemy_class = enemy_map.get(enemy_type, Enemy)
        enemy_class(row, groups, enemy_type, self.sound_manager)

    def is_complete(self):
        if self.total_enemies_in_level == 0:
            return False

        all_spawned = not self.enemy_spawn_list
        all_defeated = self.enemies_killed >= self.total_enemies_in_level
        return all_spawned and all_defeated