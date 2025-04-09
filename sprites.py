# sprites.py

import pygame
import random
import time
# <<<--- Импортируем нужные модули и файлы ---
import settings           # Настройки игры (константы)
from assets import load_image # Функция для загрузки картинок

# --- Вспомогательная функция для определения ряда ---
def get_row_from_y(y_coord):
    """Определяет номер ряда (0-индексированный) по Y координате центра."""
    if not (settings.GRID_START_Y <= y_coord < settings.GRID_START_Y + settings.GRID_ROWS * settings.CELL_HEIGHT):
        # print(f"Предупреждение: Координата Y={y_coord} вне диапазона сетки.")
        pass
    relative_y = y_coord - settings.GRID_START_Y
    row = int(relative_y // settings.CELL_HEIGHT)
    row = max(0, min(row, settings.GRID_ROWS - 1))
    # print(f"get_row_from_y: y={y_coord}, relative_y={relative_y}, calculated_row={row}")
    return row

# --- Базовый класс для Растений ---
class BasePlant(pygame.sprite.Sprite):
    """Общий родительский класс для всех растений."""
    def __init__(self, x, y, image_file, size, cost, health, color):
        super().__init__()
        self.image = load_image(image_file, (size, size), color)
        self.rect = self.image.get_rect(center=(x, y))
        self.cost = cost
        self.health = health # Используем переданное здоровье
        self.row = get_row_from_y(self.rect.centery)
        self.grid_pos = None # <<<--- Позиция в сетке (row, col), устанавливается в game._handle_events

    # <<<--- ДОБАВЛЕН МЕТОД ---
    def take_damage(self, amount):
        """Уменьшает здоровье растения и убивает его, если здоровье <= 0."""
        self.health -= amount
        # print(f"Plant {self.grid_pos} took damage, health: {self.health}") # Отладка
        if self.health <= 0:
            # print(f"Plant {self.grid_pos} destroyed.") # Отладка
            self.kill() # Метод kill() удаляет спрайт из всех групп pygame

# --- Класс Горохострела ---
class PeaShooter(BasePlant):
    """Растение, стреляющее горохом."""
    plant_type = "peashooter"
    def __init__(self, x, y):
        super().__init__(x, y, settings.PEASHOOTER_IMAGE_FILE, settings.PEASHOOTER_SIZE,
                         settings.PEASHOOTER_COST, settings.PEASHOOTER_HEALTH, settings.GREEN)
        self.last_shot_time = time.time()

    def can_shoot(self):
        now = time.time()
        return now - self.last_shot_time >= settings.PEASHOOTER_COOLDOWN

    def shoot(self):
        try:
            if self.can_shoot():
                self.last_shot_time = time.time()
                projectile = Projectile(self.rect.right, self.rect.centery)
                return projectile
            return None
        except Exception as e:
            print(f"ОШИБКА в PeaShooter.shoot(): {e}")
            return None

    def update(self, zombies_on_my_row_ahead):
        try:
            if zombies_on_my_row_ahead:
                 return self.shoot()
            return None
        except Exception as e:
            print(f"ОШИБКА в PeaShooter.update(): {e}")
            return None

# --- Класс Подсолнуха ---
class Sunflower(BasePlant):
    """Растение, производящее солнышки."""
    plant_type = "sunflower"
    def __init__(self, x, y):
        super().__init__(x, y, settings.SUNFLOWER_IMAGE_FILE, settings.SUNFLOWER_SIZE,
                         settings.SUNFLOWER_COST, settings.SUNFLOWER_HEALTH, settings.YELLOW)
        self.last_production_time = time.time() + random.uniform(0, settings.SUNFLOWER_PRODUCTION_RATE / 2)

    def update(self): # Подсолнух не зависит от зомби
        try:
            now = time.time()
            if now - self.last_production_time >= settings.SUNFLOWER_PRODUCTION_RATE:
                self.last_production_time = now
                sun_x = self.rect.centerx + random.randint(-10, 10)
                sun_y = self.rect.top - settings.SUN_SIZE // 2 + random.randint(-5, 5)
                new_sun = Sun(sun_x, sun_y, settings.SUN_VALUE)
                return new_sun
            return None
        except Exception as e:
            print(f"ОШИБКА в Sunflower.update(): {e}")
            return None

# --- Класс Солнышка (для сбора) ---
class Sun(pygame.sprite.Sprite):
    """Объект солнышка, который появляется и исчезает со временем."""
    def __init__(self, x, y, value):
        super().__init__()
        self.value = value
        self.image = load_image(settings.SUN_IMAGE_FILE, (settings.SUN_SIZE, settings.SUN_SIZE), settings.YELLOW)
        self.rect = self.image.get_rect(center=(x, y))
        self.creation_time = time.time()
        self.lifetime = settings.SUN_LIFETIME

    def update(self):
        now = time.time()
        if now - self.creation_time > self.lifetime:
            self.kill()

# --- Класс Зомби (С ИЗМЕНЕНИЯМИ) ---
class Zombie(pygame.sprite.Sprite):
    """Класс зомби с состояниями ходьбы и поедания."""
    def __init__(self, y_pos, zombie_type="regular"):
        super().__init__()
        if zombie_type not in settings.ZOMBIE_TYPES:
            print(f"Предупреждение: неизвестный тип зомби '{zombie_type}', используется 'regular'")
            zombie_type = "regular"
        self.type_info = settings.ZOMBIE_TYPES[zombie_type]
        self.zombie_type = zombie_type

        zombie_image_file = self.type_info.get("image")
        self.image = load_image(zombie_image_file, (settings.ZOMBIE_SIZE, settings.ZOMBIE_SIZE), self.type_info["color"])

        self.rect = self.image.get_rect(centery=y_pos)
        self.rect.left = settings.SCREEN_WIDTH + random.randint(0, 50)
        self.speed = self.type_info["speed"]
        self.health = self.type_info["health"]
        self.row = get_row_from_y(self.rect.centery)
        # print(f"Создан зомби типа {self.zombie_type} на ряду {self.row} (Y={self.rect.centery})")

        # <<<--- НОВЫЕ АТРИБУТЫ ---
        self.state = "WALKING" # Состояния: WALKING, EATING
        self.eating_target = None # Какое растение ест (объект BasePlant)
        self.last_bite_time = 0 # Время последнего укуса

    # <<<--- ПОЛНОСТЬЮ ПЕРЕПИСАННЫЙ МЕТОД update ---
    def update(self, plants_group): # Принимает группу растений для проверки столкновений
        """Обновляет состояние зомби: движение или поедание."""
        now = time.time() # Получаем текущее время один раз

        # --- Логика для состояния EATING ---
        if self.state == "EATING":
            # Проверяем, существует ли еще цель (ее могли убить снарядом или съесть)
            # .alive() проверяет, есть ли спрайт еще в каких-либо группах
            if self.eating_target and self.eating_target.alive():
                # Если цель есть, проверяем, пора ли кусать (прошла ли перезарядка укуса)
                if now - self.last_bite_time >= settings.ZOMBIE_BITE_RATE:
                    # print(f"Zombie на {self.row} кусает растение {self.eating_target.grid_pos}") # Отладка
                    self.eating_target.take_damage(settings.ZOMBIE_DAMAGE) # Наносим урон растению
                    self.last_bite_time = now # Обновляем время последнего укуса
            else:
                # Если цели больше нет (убили снарядом или съели до конца)
                # print(f"Zombie на {self.row} закончил есть, цель исчезла.") # Отладка
                self.state = "WALKING" # Возвращаемся к ходьбе
                self.eating_target = None # Сбрасываем цель (уже не едим никого)

        # --- Логика для состояния WALKING ---
        elif self.state == "WALKING":
            # Ищем растение ПЕРЕД зомби на ЭТОМ ЖЕ ряду
            target_plant = None
            # Фильтруем растения только на ряду зомби
            plants_on_my_row = [p for p in plants_group if p.row == self.row]

            # Ищем ПЕРЕСЕЧЕНИЕ с растением на пути
            for plant in plants_on_my_row:
                # Зомби должен остановиться, когда его "нос" (левая часть rect + небольшой запас)
                # достигнет правой части rect'а растения.
                # Или просто проверяем пересечение, а скорость = 0 в состоянии EATING не даст пройти дальше.
                # Проверяем, пересекается ли ПРЯМОУГОЛЬНИК зомби с ПРЯМОУГОЛЬНИКОМ растения
                if self.rect.colliderect(plant.rect):
                     # Дополнительно убедимся, что растение действительно впереди (или хотя бы частично)
                     # Это предотвратит атаку на растение, которое он уже прошел (маловероятно, но все же)
                     if self.rect.left < plant.rect.right:
                           target_plant = plant
                           break # Нашли первое растение на пути, дальше не ищем

            # Если нашли растение для поедания
            if target_plant:
                # print(f"Zombie на {self.row} начал есть растение {target_plant.grid_pos}") # Отладка
                self.state = "EATING" # Меняем состояние на "Едим"
                self.eating_target = target_plant # Запоминаем, КОГО едим
                self.last_bite_time = now # Начинаем кусать немедленно
                # В состоянии EATING зомби не будет двигаться (нет self.rect.x -= self.speed)
            else:
                # Если столкновений с растениями на пути нет, продолжаем идти влево
                try:
                    self.rect.x -= self.speed
                except Exception as e:
                    print(f"ОШИБКА в Zombie.update() при движении: {e}")

    # Метод take_damage остается почти таким же, но сбрасывает цель при смерти
        # sprites.py -> class Zombie

        def take_damage(self, amount):
            """Получение урона, проверка на смерть и ВОЗВРАТ True при смерти."""
            try:
                self.health -= amount
                if self.health <= 0:
                    if self.eating_target:
                        self.eating_target = None
                    self.kill()
                    return True  # <<<--- ДОБАВЛЕНО: Сигнализируем, что зомби убит
                return False  # <<<--- ДОБАВЛЕНО: Зомби еще жив
            except Exception as e:
                print(f"ОШИБКА в Zombie.take_damage(): {e}")
                return False  # В случае ошибки считаем, что не убит

# --- Класс Снаряда ---
class Projectile(pygame.sprite.Sprite):
    """Снаряд (горошина), летящий от растения."""
    def __init__(self, x, y):
        super().__init__()
        self.image = load_image(settings.PROJECTILE_IMAGE_FILE, (settings.PROJECTILE_SIZE, settings.PROJECTILE_SIZE), settings.BLUE)
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = settings.PROJECTILE_SPEED

    def update(self):
        try:
            self.rect.x += self.speed
            if self.rect.left > settings.SCREEN_WIDTH:
                self.kill()
        except Exception as e:
            print(f"ОШИБКА в Projectile.update(): {e}")
            self.kill()

# --- Класс Газонокосилки ---
class Lawnmower(pygame.sprite.Sprite):
    """Газонокосилка - последняя линия обороны."""
    def __init__(self, row):
        super().__init__()
        self.row = row
        self.image = load_image(settings.LAWNMOWER_IMAGE_FILE, (settings.MOWER_WIDTH, settings.MOWER_HEIGHT), settings.RED)
        self.rect = self.image.get_rect()
        self.rect.centery = settings.GRID_START_Y + self.row * settings.CELL_HEIGHT + settings.CELL_HEIGHT // 2
        self.rect.right = settings.GRID_START_X - 5
        self.state = "IDLE"
        self.speed = settings.MOWER_SPEED
        # print(f"Создана косилка на ряду {self.row} (Y={self.rect.centery})")

    def activate(self):
        if self.state == "IDLE":
            self.state = "ACTIVE"
            print(f"!!! АКТИВАЦИЯ косилки на ряду {self.row}.")

    def update(self, zombies_group):
        if self.state == "ACTIVE":
            start_x = self.rect.x
            self.rect.x += self.speed
            # print(f"Косилка {self.row}: Движение с {start_x} до {self.rect.x}")

            for zombie in zombies_group:
                # print(f"  Проверка: Косилка({self.row}, rect:{self.rect}) vs Зомби({zombie.row}, rect:{zombie.rect})")
                if zombie.row == self.row:
                    # print(f"    Ряды совпали ({self.row}). Проверка столкновения...")
                    if self.rect.colliderect(zombie.rect):
                        print(f"    СТОЛКНОВЕНИЕ! Косилка({self.row}) и Зомби({zombie.row}). Зомби удален.")
                        zombie.kill()
                    # else:
                        # print("    Столкновения rect'ов нет.")
                # else:
                    # print("    Ряды не совпадают.")

            if self.rect.left > settings.SCREEN_WIDTH:
                self.kill()