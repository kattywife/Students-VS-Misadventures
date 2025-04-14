# sprites.py

import pygame
import random
import time
# <<<--- Импортируем нужные модули и файлы ---
import settings           # Настройки игры (константы)
from assets import load_image # Функция для загрузки картинок

# --- Вспомогательная функция для определения ряда ---
# (Функция get_row_from_y остается без изменений)
def get_row_from_y(y_coord):
    if not (settings.GRID_START_Y <= y_coord < settings.GRID_START_Y + settings.GRID_ROWS * settings.CELL_HEIGHT): pass
    relative_y = y_coord - settings.GRID_START_Y
    row = int(relative_y // settings.CELL_HEIGHT)
    row = max(0, min(row, settings.GRID_ROWS - 1))
    return row

# <<<--- Изменение №1: Переименовываем базовый класс ---
# --- Базовый класс для Студентов и Генераторов ---
class PlacedObject(pygame.sprite.Sprite): # Вместо BasePlant
    """Общий родительский класс для размещаемых объектов (студенты, кофе-машина)."""
    def __init__(self, x, y, image_file, size, cost, health, color):
        super().__init__()
        self.image = load_image(image_file, (size, size), color)
        self.rect = self.image.get_rect(center=(x, y))
        self.cost = cost
        self.health = health
        self.row = get_row_from_y(self.rect.centery)
        self.grid_pos = None # Позиция в сетке (row, col)

    def take_damage(self, amount):
        """Уменьшает здоровье объекта."""
        self.health -= amount
        if self.health <= 0:
            self.kill() # Удаляем объект, если здоровье кончилось
            return True # Сигнализируем, что объект убит
        return False

# <<<--- Изменение №2: Переименовываем класс PeaShooter и его логику ---
# --- Класс Мальчика Джуна ---
class JunBoy(PlacedObject): # Наследуемся от PlacedObject
    """Студент, стреляющий шестеренками."""
    plant_type = "jun_boy" # Идентификатор для магазина
    def __init__(self, x, y):
        # Используем константы для Джуна из settings
        super().__init__(x, y, settings.JUN_BOY_IMAGE_FILE, settings.JUN_BOY_SIZE,
                         settings.JUN_BOY_COST, settings.JUN_BOY_HEALTH, settings.GREEN) # Цвет можно изменить
        self.last_shot_time = time.time()

    def can_shoot(self):
        """Проверяет перезарядку."""
        now = time.time()
        # Используем перезарядку Джуна
        return now - self.last_shot_time >= settings.JUN_BOY_COOLDOWN

    def shoot(self):
        """Создает и возвращает объект Шестеренки."""
        try:
            if self.can_shoot():
                self.last_shot_time = time.time()
                # Создаем снаряд Шестеренку
                projectile = Gear(self.rect.right, self.rect.centery) # Используем новый класс снаряда
                return projectile
            return None
        except Exception as e:
            print(f"ОШИБКА в JunBoy.shoot(): {e}")
            return None

    def update(self, adversities_on_my_row_ahead): # Переименовали аргумент
        """Проверяет цель и возвращает Шестеренку."""
        try:
            if adversities_on_my_row_ahead: # Если есть "злоключение" впереди
                 return self.shoot() # Стреляем
            return None
        except Exception as e:
            print(f"ОШИБКА в JunBoy.update(): {e}")
            return None

# <<<--- Изменение №3: Добавляем класс Девочки Ботана ---
# --- Класс Девочки Ботана ---
class BotanGirl(PlacedObject):
    """Студент, стреляющий книгами."""
    plant_type = "botan_girl"
    def __init__(self, x, y):
        super().__init__(x, y, settings.BOTAN_GIRL_IMAGE_FILE, settings.BOTAN_GIRL_SIZE,
                         settings.BOTAN_GIRL_COST, settings.BOTAN_GIRL_HEALTH, settings.BLUE) # Другой цвет
        self.last_shot_time = time.time()

    def can_shoot(self):
        now = time.time()
        return now - self.last_shot_time >= settings.BOTAN_GIRL_COOLDOWN

    def shoot(self):
        """Создает и возвращает объект Книги."""
        try:
            if self.can_shoot():
                self.last_shot_time = time.time()
                projectile = Book(self.rect.right, self.rect.centery) # Создаем Книгу
                return projectile
            return None
        except Exception as e:
            print(f"ОШИБКА в BotanGirl.shoot(): {e}")
            return None

    def update(self, adversities_on_my_row_ahead):
        """Проверяет цель и возвращает Книгу."""
        try:
            if adversities_on_my_row_ahead:
                 return self.shoot()
            return None
        except Exception as e:
            print(f"ОШИБКА в BotanGirl.update(): {e}")
            return None

# <<<--- Изменение №4: Переименовываем класс Sunflower ---
# --- Класс Кофе-машины ---
class CoffeeMachine(PlacedObject): # Наследуемся от PlacedObject
    """Генератор 'кофеина' (ресурса)."""
    plant_type = "coffee_machine" # Идентификатор для магазина
    def __init__(self, x, y):
        super().__init__(x, y, settings.COFFEE_MACHINE_IMAGE_FILE, settings.COFFEE_MACHINE_SIZE,
                         settings.COFFEE_MACHINE_COST, settings.COFFEE_MACHINE_HEALTH, settings.YELLOW)
        self.last_production_time = time.time() + random.uniform(0, settings.COFFEE_MACHINE_PRODUCTION_RATE / 2)

    def update(self): # Метод update остается таким же по логике
        """Создает и возвращает Кофейное Зерно."""
        try:
            now = time.time()
            if now - self.last_production_time >= settings.COFFEE_MACHINE_PRODUCTION_RATE:
                self.last_production_time = now
                bean_x = self.rect.centerx + random.randint(-10, 10)
                bean_y = self.rect.top - settings.COFFEE_BEAN_SIZE // 2 + random.randint(-5, 5)
                # Создаем Кофейное Зерно
                new_bean = CoffeeBean(bean_x, bean_y, settings.COFFEE_BEAN_VALUE) # Используем новый класс
                return new_bean
            return None
        except Exception as e:
            print(f"ОШИБКА в CoffeeMachine.update(): {e}")
            return None

# <<<--- Изменение №5: Переименовываем класс Sun ---
# --- Класс Кофейного Зерна ---
class CoffeeBean(pygame.sprite.Sprite):
    """Ресурс ('кофеин'), который нужно собирать."""
    def __init__(self, x, y, value):
        super().__init__()
        self.value = value
        # Используем новые константы для зерна
        self.image = load_image(settings.COFFEE_BEAN_IMAGE_FILE, (settings.COFFEE_BEAN_SIZE, settings.COFFEE_BEAN_SIZE), settings.YELLOW)
        self.rect = self.image.get_rect(center=(x, y))
        self.creation_time = time.time()
        self.lifetime = settings.COFFEE_BEAN_LIFETIME

    def update(self):
        """Проверяет время жизни."""
        now = time.time()
        if now - self.creation_time > self.lifetime:
            self.kill()

# <<<--- Изменение №6: Переименовываем класс Zombie ---
# --- Класс Злоключения (Базовый) ---
class Adversity(pygame.sprite.Sprite): # Вместо Zombie
    """Базовый класс для всех типов 'злоключений'."""
    def __init__(self, y_pos, adversity_type="alarm_clock"): # Тип по умолчанию - будильник
        super().__init__()
        # Используем ADVERSITY_TYPES из settings
        if adversity_type not in settings.ADVERSITY_TYPES:
            print(f"Предупреждение: неизвестный тип злоключения '{adversity_type}', используется 'alarm_clock'")
            adversity_type = "alarm_clock"
        self.type_info = settings.ADVERSITY_TYPES[adversity_type]
        self.adversity_type = adversity_type # Сохраняем тип

        adversity_image_file = self.type_info.get("image")
        # Используем общий ADVERSITY_SIZE
        self.image = load_image(adversity_image_file, (settings.ADVERSITY_SIZE, settings.ADVERSITY_SIZE), self.type_info["color"])

        self.rect = self.image.get_rect(centery=y_pos)
        self.rect.left = settings.SCREEN_WIDTH + random.randint(0, 50)
        self.speed = self.type_info["speed"]
        self.health = self.type_info["health"]
        self.row = get_row_from_y(self.rect.centery)

        self.state = "WALKING"
        self.eating_target = None # Цель атаки (объект PlacedObject)
        self.last_bite_time = 0

    # <<<--- Обновляем update для работы с PlacedObject и ADVERSITY_DAMAGE/RATE ---
    def update(self, placed_objects_group): # Принимает группу студентов/машин
        """Обновляет состояние злоключения: движение или атака."""
        now = time.time()

        if self.state == "EATING":
            if self.eating_target and self.eating_target.alive():
                if now - self.last_bite_time >= settings.ADVERSITY_BITE_RATE:
                    # print(f"Adversity {self.adversity_type} на {self.row} атакует {type(self.eating_target)}") # Отладка
                    was_killed = self.eating_target.take_damage(settings.ADVERSITY_DAMAGE)
                    self.last_bite_time = now
                    # Если цель убита методом take_damage, она сама себя удалит
            else:
                # print(f"Adversity {self.adversity_type} на {self.row} прекращает атаку.") # Отладка
                self.state = "WALKING"
                self.eating_target = None

        elif self.state == "WALKING":
            target_object = None
            objects_on_my_row = [p for p in placed_objects_group if p.row == self.row]
            for obj in objects_on_my_row:
                if self.rect.colliderect(obj.rect) and self.rect.left < obj.rect.right:
                     target_object = obj
                     break

            if target_object:
                # print(f"Adversity {self.adversity_type} на {self.row} начинает атаку на {type(target_object)}") # Отладка
                self.state = "EATING"
                self.eating_target = target_object
                self.last_bite_time = now
            else:
                try:
                    self.rect.x -= self.speed
                except Exception as e:
                    print(f"ОШИБКА в Adversity.update() при движении: {e}")

    # <<<--- Обновляем take_damage ---
    def take_damage(self, amount):
        """Получение урона и проверка на смерть."""
        try:
            self.health -= amount
            if self.health <= 0:
                if self.eating_target:
                    self.eating_target = None
                self.kill()
                return True # Сигнализируем об убийстве
            return False
        except Exception as e:
            print(f"ОШИБКА в Adversity.take_damage(): {e}")
            return False

# <<<--- Изменение №7: Переименовываем и создаем классы Снарядов ---
# --- Класс Шестеренки ---
class Gear(pygame.sprite.Sprite): # Вместо Projectile
    """Снаряд Мальчика Джуна."""
    def __init__(self, x, y):
        super().__init__()
        # Используем параметры Шестеренки из settings
        self.image = load_image(settings.GEAR_IMAGE_FILE, (settings.GEAR_SIZE, settings.GEAR_SIZE), settings.DARK_GREY) # Цвет можно изменить
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = settings.GEAR_SPEED
        self.damage = settings.GEAR_DAMAGE # <<<--- Сохраняем урон

    def update(self):
        """Движение снаряда вправо."""
        try:
            self.rect.x += self.speed
            if self.rect.left > settings.SCREEN_WIDTH:
                self.kill()
        except Exception as e:
            print(f"ОШИБКА в Gear.update(): {e}")
            self.kill()

# --- Класс Книги ---
class Book(pygame.sprite.Sprite):
    """Снаряд Девочки Ботана."""
    def __init__(self, x, y):
        super().__init__()
        # Используем параметры Книги из settings
        self.image = load_image(settings.BOOK_IMAGE_FILE, (settings.BOOK_SIZE, settings.BOOK_SIZE), settings.BROWN) # Цвет можно изменить
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = settings.BOOK_SPEED
        self.damage = settings.BOOK_DAMAGE # <<<--- Сохраняем урон

    def update(self):
        """Движение снаряда вправо."""
        try:
            self.rect.x += self.speed
            if self.rect.left > settings.SCREEN_WIDTH:
                self.kill()
        except Exception as e:
            print(f"ОШИБКА в Book.update(): {e}")
            self.kill()


# <<<--- Изменение №8: Переименовываем класс Lawnmower ---
# --- Класс Академа ---
class Academ(pygame.sprite.Sprite): # Вместо Lawnmower
    """Последняя линия обороны - академический отпуск."""
    def __init__(self, row):
        super().__init__()
        self.row = row
        # Используем параметры Академа из settings
        self.image = load_image(settings.ACADEM_IMAGE_FILE, (settings.ACADEM_WIDTH, settings.ACADEM_HEIGHT), settings.RED)
        self.rect = self.image.get_rect()
        self.rect.centery = settings.GRID_START_Y + self.row * settings.CELL_HEIGHT + settings.CELL_HEIGHT // 2
        self.rect.right = settings.GRID_START_X - 5
        self.state = "IDLE"
        self.speed = settings.ACADEM_SPEED

    def activate(self):
        """Активирует 'академ'."""
        if self.state == "IDLE":
            self.state = "ACTIVE"
            print(f"!!! АКТИВАЦИЯ 'Академа' на ряду {self.row}.")

    # <<<--- Обновляем update для работы с классом Adversity ---
    def update(self, adversities_group): # Принимает группу злоключений
        """Движение и уничтожение злоключений для активного 'академа'."""
        killed_count = 0
        if self.state == "ACTIVE":
            self.rect.x += self.speed

            # Используем улучшенную проверку столкновений
            for adversity in adversities_group: # Перебираем злоключения
                if adversity.row == self.row: # Проверяем ряд
                    if self.rect.colliderect(adversity.rect): # Проверяем столкновение
                        # print(f"    'Академ' ({self.row}) столкнулся с {adversity.adversity_type} ({adversity.row}).") # Отладка
                        adversity.kill() # Уничтожаем злоключение
                        killed_count += 1

            if self.rect.left > settings.SCREEN_WIDTH:
                self.kill() # Удаляем 'академ'
        # Возвращаем количество убитых (может понадобиться для статистики)
        return killed_count


# конец файла sprites