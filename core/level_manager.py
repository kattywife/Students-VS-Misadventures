# core/level_manager.py

import pygame
import random
from data.levels import LEVELS
from entities.enemies import Enemy, Calculus, MathTeacher, Addict, Thief
from data.settings import *


class LevelManager:
    """
    Управляет логикой конкретного уровня: последовательностью и таймингами появления врагов.
    Не занимается их поведением, только созданием.
    """
    def __init__(self, level_id, enemy_group=None, all_sprites_group=None, sound_manager=None):
        """
        Инициализирует менеджер уровня.

        Args:
            level_id (int): ID уровня для загрузки данных.
            enemy_group (pygame.sprite.Group, optional): Группа для добавления созданных врагов.
            all_sprites_group (pygame.sprite.Group, optional): Общая группа спрайтов.
            sound_manager (SoundManager, optional): Менеджер звука.
        """
        self.level_data = LEVELS.get(level_id, LEVELS[1])
        # Копируем и перемешиваем список врагов для случайного порядка появления
        self.enemy_spawn_list = self.level_data['enemies'].copy()
        random.shuffle(self.enemy_spawn_list)

        self.enemy_group = enemy_group
        self.all_sprites_group = all_sprites_group
        self.sound_manager = sound_manager
        self.calamities = self.level_data.get('calamities', [])

        self.is_running = False

        # Статистика для отслеживания прогресса уровня
        self.total_enemies_in_level = len(self.enemy_spawn_list)
        self.enemies_killed = 0
        self.enemies_spawned = 0

        # Управление скоростью появления врагов
        self.spawn_cooldown = INITIAL_SPAWN_COOLDOWN
        self.last_spawn_time = 0
        self.final_wave_threshold = FINAL_WAVE_THRESHOLD
        self.in_final_wave = False

    def start(self):
        """Запускает процесс появления врагов."""
        self.is_running = True
        self.last_spawn_time = pygame.time.get_ticks()

    def enemy_killed(self):
        """Увеличивает счетчик убитых врагов. Вызывается из BattleManager."""
        self.enemies_killed += 1

    def get_spawn_progress(self):
        """
        Возвращает прогресс появления врагов в диапазоне от 0.0 до 1.0.
        Используется для HUD и триггеров напастей.
        """
        if self.total_enemies_in_level == 0: return 1.0
        return self.enemies_spawned / self.total_enemies_in_level

    def get_kill_progress(self):
        """
        Возвращает прогресс убийства врагов в диапазоне от 0.0 до 1.0.
        Используется для HUD.
        """
        if self.total_enemies_in_level == 0: return 1.0
        return self.enemies_killed / self.total_enemies_in_level

    def get_kill_count_data(self):
        """Возвращает кортеж с данными об убитых врагах (убито, всего)."""
        return self.enemies_killed, self.total_enemies_in_level

    def get_spawn_count_data(self):
        """Возвращает кортеж с данными о появившихся врагах (появилось, всего)."""
        return self.enemies_spawned, self.total_enemies_in_level

    def get_enemy_types_for_level(self):
        """
        Возвращает отсортированный список уникальных типов врагов для данного уровня.
        Используется на экране подготовки для информирования игрока.
        """
        if not self.level_data['enemies']: return []
        # Создаем множество, чтобы получить уникальные типы, затем сортируем
        return sorted(list(set(enemy[0] for enemy in self.level_data['enemies'])))

    def get_calamity_types_for_level(self):
        """
        Возвращает список типов напастей для данного уровня.
        Используется на экране подготовки.
        """
        return self.level_data.get('calamities', [])

    def update(self):
        """
        Проверяет, пора ли создавать нового врага, и если да, создает его.
        Вызывается каждый кадр из BattleManager.
        """
        # --- ИСХОДНАЯ ВЕРСИЯ ПРОВЕРКИ ---
        # Менеджер может быть создан без групп для получения данных (в PrepManager),
        # в этом случае update не должен ничего делать.
        if not self.is_running or not self.enemy_spawn_list or self.enemy_group is None:
            return

        now = pygame.time.get_ticks()

        # Проверка на переход к "финальной волне", когда спавн ускоряется
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
        """
        Создает экземпляр врага нужного класса и добавляет его в игровые группы.
        Использует словарь-карту для выбора конструктора (паттерн "Фабричный метод").

        Args:
            enemy_type (str): Тип врага (e.g., 'calculus').
            row (int): Номер ряда, в котором должен появиться враг.
        """
        groups = (self.enemy_group, self.all_sprites_group)

        enemy_map = {
            'calculus': Calculus,
            'math_teacher': MathTeacher,
            'addict': Addict,
            'thief': Thief
        }

        # Если тип не найден в карте, используется базовый класс Enemy
        enemy_class = enemy_map.get(enemy_type, Enemy)
        enemy_class(row, groups, enemy_type, self.sound_manager)

    def is_complete(self):
        """
        Проверяет, завершен ли уровень.
        Условия: все враги появились на поле И все враги побеждены.

        Returns:
            bool: True, если уровень завершен, иначе False.
        """
        if self.total_enemies_in_level == 0:
            return False # Тестовый уровень не может быть завершен

        all_spawned = not self.enemy_spawn_list
        all_defeated = self.enemies_killed >= self.total_enemies_in_level
        return all_spawned and all_defeated