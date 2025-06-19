# core/level_manager.py

import pygame
import random
from data.levels import LEVELS
from entities.enemies import Enemy, Calculus, MathTeacher, Addict, Thief
from data.settings import *


class LevelManager:
    """
    Управляет логикой конкретного уровня: последовательностью и таймингами
    появления врагов, отслеживает прогресс и определяет момент завершения уровня.
    """
    def __init__(self, level_id, enemy_group=None, all_sprites_group=None, sound_manager=None):
        """
        Инициализирует менеджер уровня.

        Args:
            level_id (int): ID уровня для загрузки данных из `LEVELS`.
            enemy_group (pygame.sprite.Group, optional): Группа для добавления врагов.
            all_sprites_group (pygame.sprite.Group, optional): Общая группа всех спрайтов.
            sound_manager (SoundManager, optional): Менеджер звуков.
        """
        self.level_data = LEVELS.get(level_id, LEVELS[1]) # Загружаем данные уровня
        # Копируем и перемешиваем список врагов для случайного порядка появления
        self.enemy_spawn_list = self.level_data['enemies'].copy()
        random.shuffle(self.enemy_spawn_list)

        self.enemy_group = enemy_group
        self.all_sprites_group = all_sprites_group
        self.sound_manager = sound_manager
        self.calamities = self.level_data.get('calamities', []) # Список напастей для уровня

        self.is_running = False # Флаг, запущен ли уровень

        # --- Счетчики прогресса ---
        self.total_enemies_in_level = len(self.enemy_spawn_list)
        self.enemies_killed = 0
        self.enemies_spawned = 0

        # --- Тайминги спавна ---
        self.spawn_cooldown = INITIAL_SPAWN_COOLDOWN
        self.last_spawn_time = 0
        self.final_wave_threshold = FINAL_WAVE_THRESHOLD # Порог для ускорения спавна
        self.in_final_wave = False

    def start(self):
        """Запускает уровень и таймер спавна."""
        self.is_running = True
        self.last_spawn_time = pygame.time.get_ticks()

    def enemy_killed(self):
        """Увеличивает счетчик убитых врагов."""
        self.enemies_killed += 1

    def get_spawn_progress(self):
        """Возвращает прогресс появления врагов от 0.0 до 1.0."""
        if self.total_enemies_in_level == 0: return 1.0
        return self.enemies_spawned / self.total_enemies_in_level

    def get_kill_progress(self):
        """Возвращает прогресс убийства врагов от 0.0 до 1.0."""
        if self.total_enemies_in_level == 0: return 1.0
        return self.enemies_killed / self.total_enemies_in_level

    def get_kill_count_data(self):
        """Возвращает кортеж (убито, всего) для отображения в UI."""
        return self.enemies_killed, self.total_enemies_in_level

    def get_spawn_count_data(self):
        """Возвращает кортеж (появилось, всего) для отображения в UI."""
        return self.enemies_spawned, self.total_enemies_in_level

    def get_enemy_types_for_level(self):
        """Возвращает отсортированный список уникальных типов врагов на уровне."""
        if not self.level_data['enemies']: return []
        return sorted(list(set(enemy[0] for enemy in self.level_data['enemies'])))

    def get_calamity_types_for_level(self):
        """Возвращает список типов напастей, возможных на уровне."""
        return self.level_data.get('calamities', [])

    def update(self):
        """
        Обновляет состояние менеджера уровня.
        Отвечает за спавн врагов по таймеру.
        """
        # --- ИСПРАВЛЕНИЕ: Проверяем на 'is None' вместо 'not' ---
        # Эта проверка теперь корректно отличает отсутствие группы от пустой группы.
        # Это важно для TempLevelManager в PrepManager, который создается без групп.
        if not self.is_running or not self.enemy_spawn_list or self.enemy_group is None:
            return

        now = pygame.time.get_ticks()

        # Проверяем, не достигнут ли порог для начала "финальной волны"
        if not self.in_final_wave and self.total_enemies_in_level > 0 and \
                (self.enemies_spawned / self.total_enemies_in_level) >= self.final_wave_threshold:
            self.in_final_wave = True
            self.spawn_cooldown = FINAL_WAVE_SPAWN_COOLDOWN # Уменьшаем задержку

        # Спавним врага, если прошло достаточно времени
        if now - self.last_spawn_time > self.spawn_cooldown:
            self.last_spawn_time = now
            enemy_type, row = self.enemy_spawn_list.pop(0)
            self.spawn_enemy(enemy_type, row)
            self.enemies_spawned += 1

    def spawn_enemy(self, enemy_type, row):
        """
        Создает экземпляр врага нужного типа и добавляет его в группы.

        Args:
            enemy_type (str): Тип врага (ключ из ENEMIES_DATA).
            row (int): Номер ряда для появления.
        """
        groups = (self.enemy_group, self.all_sprites_group)

        # Карта для сопоставления типа врага с его классом
        enemy_map = {
            'calculus': Calculus,
            'math_teacher': MathTeacher,
            'addict': Addict,
            'thief': Thief
        }

        # Выбираем нужный класс или базовый Enemy, если тип не найден в карте
        enemy_class = enemy_map.get(enemy_type, Enemy)
        enemy_class(row, groups, enemy_type, self.sound_manager)

    def is_complete(self):
        """
        Проверяет, завершен ли уровень.
        Уровень считается завершенным, когда все враги появились и все убиты.

        Returns:
            bool: True, если уровень завершен, иначе False.
        """
        if self.total_enemies_in_level == 0:
            return False # Уровень не может быть завершен, если в нем нет врагов

        all_spawned = not self.enemy_spawn_list
        all_defeated = self.enemies_killed >= self.total_enemies_in_level
        return all_spawned and all_defeated