# entities/defenders.py

import pygame
import os
import random
import math
from data.settings import *
from data.assets import PROJECTILE_IMAGES, load_image
from entities.base_sprite import BaseSprite, ExplosionEffect, BookAttackEffect
from entities.projectiles import Bracket, PaintSplat, SoundWave
from entities.other_sprites import CoffeeBean, AuraEffect


class Defender(BaseSprite):
    """
    Базовый класс для всех юнитов-защитников (студентов).
    Содержит общую логику: здоровье, анимации, получение урона,
    применение эффектов и т.д.
    """
    def __init__(self, x, y, groups, data, sound_manager):
        """
        Инициализирует защитника.

        Args:
            x (int): Координата X центра спрайта.
            y (int): Координата Y центра спрайта.
            groups (tuple): Группы спрайтов, в которые нужно добавить защитника.
            data (dict): Словарь с характеристиками из DEFENDERS_DATA.
            sound_manager (SoundManager): Менеджер для воспроизведения звуков.
        """
        super().__init__(groups)
        self.sound_manager = sound_manager
        self.data = data
        self.max_health = self.data['health']
        self.health = self.max_health
        self.cost = self.data['cost']

        self.animations = {}
        self.load_animations()

        self.current_animation = 'idle'
        self.frame_index = 0
        self.image = self.animations.get(self.current_animation, [None])[0]

        # Установка rect'а. Если анимация не загрузилась, создается резервный прямоугольник.
        if self.image:
            self.rect = self.image.get_rect(center=(x, y))
        else:
            self.image = pygame.Surface((CELL_SIZE_W - 10, CELL_SIZE_H - 10))
            unit_type = data.get('type', 'programmer')
            self.image.fill(DEFAULT_COLORS.get(unit_type, RED))
            self.rect = self.image.get_rect(center=(x, y))

        self.last_anim_update = pygame.time.get_ticks()
        self.anim_speed = self.data.get('animation_data', {}).get('speed', 0.3)

        self._layer = self.rect.bottom
        self.is_animate = 'animation_data' in self.data

        # --- Состояния и флаги ---
        self.is_being_eaten = False # Флаг, что защитника атакует враг в ближнем бою
        self.scream_channel = None  # Канал для звука крика, чтобы его можно было остановить
        self.attacker = None        # Ссылка на врага, который атакует
        self.is_upgraded = False    # Был ли юнит улучшен на экране подготовки
        self.buff_multiplier = 1.0  # Множитель урона от аур (например, Активиста)
        self.calamity_damage_multiplier = 1.0 # Множитель урона/здоровья от "напастей"

    def get_hit(self, damage):
        """Обрабатывает получение урона."""
        self.health -= damage
        self.sound_manager.play_sfx('damage')
        # Запускает анимацию получения урона, если она есть
        if 'hit' in self.animations and self.animations['hit']:
            self.current_animation = 'hit'
            self.frame_index = 0

    def load_animations(self):
        """Загружает все кадры анимаций для юнита, итеративно проверяя файлы."""
        anim_data = self.data.get('animation_data')
        if not anim_data:
            return

        size = (CELL_SIZE_W - 10, CELL_SIZE_H - 10)
        category = self.data.get('category', 'defenders')
        folder = anim_data.get('folder', self.data.get('type'))

        for anim_type in anim_data:
            if not isinstance(anim_data[anim_type], list):
                continue

            self.animations[anim_type] = []
            frame_index = 0
            while True:
                filename = f"{anim_type}_{frame_index}.png"
                path = os.path.join(category, folder, filename)

                try:
                    img = load_image(path, DEFAULT_COLORS.get(self.data['type']), size, raise_on_error=True)
                    self.animations[anim_type].append(img)
                    frame_index += 1
                except (FileNotFoundError, pygame.error):
                    break

            # Резервный вариант на случай, если для анимации не было загружено ни одного кадра
            if not self.animations.get(anim_type):
                fallback_surface = pygame.Surface(size, pygame.SRCALPHA)
                fallback_surface.fill((0, 0, 0, 0))
                self.animations[anim_type] = [fallback_surface]

    def animate(self):
        """Управляет сменой кадров текущей анимации."""
        if not self.animations or not self.animations.get(self.current_animation):
            return

        anim_sequence = self.animations[self.current_animation]

        # Принудительно включаем анимацию 'hit', если юнита едят
        if self.is_being_eaten and self.current_animation != 'hit':
            if 'hit' in self.animations and self.animations['hit']:
                self.current_animation = 'hit'
                self.frame_index = 0
        elif not self.is_being_eaten and self.current_animation == 'hit':
            pass

        now = pygame.time.get_ticks()
        if now - self.last_anim_update > self.anim_speed * 1000:
            self.last_anim_update = now
            self.image = anim_sequence[int(self.frame_index)]
            self.frame_index += 1
            # Если анимация дошла до конца
            if self.frame_index >= len(anim_sequence):
                # Цикличные анимации (attack, hit) возвращаются к idle
                if self.current_animation in ['attack', 'hit']:
                    self.current_animation = 'idle'
                self.frame_index = 0

    def get_final_damage(self, base_damage):
        """Рассчитывает итоговый урон с учетом всех модификаторов."""
        return base_damage * self.buff_multiplier * self.calamity_damage_multiplier

    def apply_calamity_effect(self, calamity_type):
        """Применяет негативный эффект от "напасти"."""
        if calamity_type == 'epidemic':
            self.calamity_damage_multiplier /= CALAMITY_EPIDEMIC_MULTIPLIER
            self.health /= CALAMITY_EPIDEMIC_MULTIPLIER

    def revert_calamity_effect(self, calamity_type):
        """Отменяет эффект от "напасти"."""
        if calamity_type == 'epidemic':
            self.calamity_damage_multiplier *= CALAMITY_EPIDEMIC_MULTIPLIER

    def update(self, **kwargs):
        """Обновляет состояние защитника каждый кадр."""
        # Сбрасываем состояние "поедания", если атакующий враг исчез
        if self.is_being_eaten and (not self.attacker or not self.attacker.alive()):
            self.is_being_eaten = False
            self.attacker = None

        self.animate()
        if self.is_animate:
            self.manage_scream_sound()
        if self.health <= 0:
            self.kill()

    def manage_scream_sound(self):
        """Управляет воспроизведением и остановкой звука крика."""
        # Если юнита едят и звук еще не играет, запускаем его
        if self.is_being_eaten and not (self.scream_channel and self.scream_channel.get_busy()):
            self.scream_channel = self.sound_manager.play_sfx('scream')
        # Если юнита перестали есть, останавливаем звук
        elif not self.is_being_eaten and self.scream_channel:
            self.scream_channel.stop()
            self.scream_channel = None

    def draw_aura(self, surface):
        """Рисует ауру под юнитом, если он улучшен. (В текущей версии не используется)."""
        if self.is_upgraded:
            aura_surf = pygame.Surface(self.rect.size, pygame.SRCALPHA)
            pygame.draw.ellipse(aura_surf, AURA_PINK, aura_surf.get_rect())
            surface.blit(aura_surf, self.rect.topleft)

    def kill(self):
        """Переопределенный метод уничтожения спрайта для дополнительной логики."""
        if not self.alive(): return
        # Убеждаемся, что звук крика прекращается при смерти
        if self.scream_channel:
            self.scream_channel.stop()
            self.scream_channel = None
        if self.is_animate:
            self.sound_manager.play_sfx('hero_dead')
        super().kill()


class ProgrammerBoy(Defender):
    """Стандартный стрелок, атакующий врагов на своей линии."""
    def __init__(self, x, y, groups, data, sound_manager, all_sprites, projectile_group, enemies_group):
        super().__init__(x, y, groups, data, sound_manager)
        self.all_sprites = all_sprites
        self.projectile_group = projectile_group
        self.attack_cooldown = self.data['cooldown'] * 1000
        self.last_shot = pygame.time.get_ticks()

    def update(self, **kwargs):
        super().update(**kwargs)
        enemies_group = kwargs.get('enemies_group')
        if not enemies_group: return

        if self.is_being_eaten: return

        now = pygame.time.get_ticks()
        # Проверяем, есть ли враг на линии справа от юнита
        has_enemy_in_row = any(
            enemy.rect.centery == self.rect.centery and enemy.rect.left >= self.rect.left
            for enemy in enemies_group)

        # Если есть враг и перезарядка прошла, стреляем
        if self.alive() and has_enemy_in_row and now - self.last_shot > self.attack_cooldown:
            self.last_shot = now
            damage = self.get_final_damage(self.data['damage'])
            random_projectile_type = random.choice(PROGRAMMER_PROJECTILE_TYPES)
            projectile_image = PROJECTILE_IMAGES[random_projectile_type]
            Bracket(self.rect.right, self.rect.centery, (self.all_sprites, self.projectile_group), damage,
                    projectile_image)
            self.current_animation = 'attack'
            self.frame_index = 0


class BotanistGirl(Defender):
    """Юнит, атакующий по области вокруг самого "сильного" врага."""
    def __init__(self, x, y, groups, data, sound_manager, all_sprites, enemies_group):
        super().__init__(x, y, groups, data, sound_manager)
        self.all_sprites = all_sprites
        self.enemies_group = enemies_group
        self.attack_cooldown = self.data['cooldown'] * 1000
        self.last_attack = pygame.time.get_ticks()
        self.explosion_radius = self.data['radius']

    def update(self, **kwargs):
        super().update(**kwargs)
        enemies_group = kwargs.get('enemies_group')
        if not enemies_group or self.is_being_eaten: return

        now = pygame.time.get_ticks()
        if self.alive() and now - self.last_attack > self.attack_cooldown:
            target = self.find_strongest_enemy(enemies_group)
            if target:
                self.last_attack = now
                self.attack(target, enemies_group)
                self.current_animation = 'attack'
                self.frame_index = 0

    def find_strongest_enemy(self, enemies_group):
        """Находит врага с наибольшим текущим здоровьем."""
        if not enemies_group:
            return None
        return max(enemies_group, key=lambda e: e.health)

    def attack(self, target, enemies_group):
        """Наносит урон по области вокруг цели."""
        damage = self.get_final_damage(self.data['damage'])
        explosion_center = target.rect.center
        pixel_radius = self.explosion_radius * CELL_SIZE_W
        BookAttackEffect(explosion_center, self.all_sprites, pixel_radius * 2)
        # Проверяем каждого врага на попадание в радиус взрыва
        for enemy in enemies_group:
            if pygame.math.Vector2(enemy.rect.center).distance_to(explosion_center) <= pixel_radius:
                enemy.get_hit(damage)


class CoffeeMachine(Defender):
    """Юнит, генерирующий ресурсы (кофе). Не атакует."""
    def __init__(self, x, y, groups, data, sound_manager, all_sprites, coffee_bean_group):
        super().__init__(x, y, groups, data, sound_manager)
        self.all_sprites = all_sprites
        self.coffee_bean_group = coffee_bean_group
        self.production_cooldown = self.data['cooldown'] * 1000
        self.last_production = pygame.time.get_ticks()
        self.is_producing = False
        self.producing_timer = 0
        self.producing_duration = COFFEE_MACHINE_PRODUCING_DURATION
        # Кэшируем кадр анимации производства для производительности
        self.producing_frame = self.animations.get('attack', [None])[0] or self.animations.get('idle', [None])[0]

    def kill(self):
        """У Кофемашины нет звука смерти героя, поэтому используется базовый kill."""
        pygame.sprite.Sprite.kill(self)

    def manage_scream_sound(self):
        """Кофемашина не кричит, когда ее атакуют."""
        pass

    def get_hit(self, damage):
        """Переопределено, чтобы убедиться, что звук 'damage' играется."""
        super().get_hit(damage)

    def animate(self):
        """Особая логика анимации: во время производства показывается один кадр."""
        if self.is_producing and self.producing_frame:
            self.image = self.producing_frame
        else:
            super().animate()

    def update(self, **kwargs):
        self.animate()
        now = pygame.time.get_ticks()

        if self.is_producing and now - self.producing_timer > self.producing_duration:
            self.is_producing = False

        if not self.is_producing and self.alive() and now - self.last_production > self.production_cooldown:
            self.last_production = now
            CoffeeBean(self.rect.centerx, self.rect.top, (self.all_sprites, self.coffee_bean_group),
                       self.data['production'])
            self.is_producing = True
            self.producing_timer = now

        if self.health <= 0:
            self.kill()


class Activist(Defender):
    """Юнит поддержки, создающий ауру, усиливающую урон союзников."""
    def __init__(self, x, y, groups, data, sound_manager, all_sprites):
        super().__init__(x, y, groups, data, sound_manager)
        self.all_sprites = all_sprites
        # При создании Активиста сразу создается связанный с ним спрайт Ауры
        AuraEffect((self.all_sprites,), self)


class Guitarist(Defender):
    """Атакует всех врагов на своей линии проникающей звуковой волной."""
    def __init__(self, x, y, groups, data, sound_manager, all_sprites, enemies_group):
        super().__init__(x, y, groups, data, sound_manager)
        self.all_sprites = all_sprites
        self.attack_cooldown = self.data['cooldown'] * 1000
        self.last_attack = pygame.time.get_ticks()

    def update(self, **kwargs):
        super().update(**kwargs)
        enemies_group = kwargs.get('enemies_group')
        if not enemies_group or self.is_being_eaten: return

        now = pygame.time.get_ticks()
        has_enemy_in_row = any(
            e.rect.centery == self.rect.centery and e.rect.left >= self.rect.left
            for e in enemies_group)

        if self.alive() and has_enemy_in_row and now - self.last_attack > self.attack_cooldown:
            self.last_attack = now
            damage = self.get_final_damage(self.data['damage'])
            speed = self.data.get('projectile_speed', SOUNDWAVE_PROJECTILE_SPEED)
            SoundWave(self.rect.center, (self.all_sprites,), damage, self.rect.centery, speed)
            self.current_animation = 'attack'
            self.frame_index = 0


class Medic(Defender):
    """Юнит поддержки, лечащий союзников в радиусе за счет своего запаса здоровья."""
    def __init__(self, x, y, groups, data, sound_manager, defenders_group):
        super().__init__(x, y, groups, data, sound_manager)
        self.heal_pool = self.data['heal_amount'] # "Мана" для лечения
        self.heal_radius = self.data['radius']
        self.heal_tick_amount = MEDIC_HEAL_TICK_AMOUNT
        self.heal_cooldown = MEDIC_HEAL_COOLDOWN_MS
        self.last_heal_time = pygame.time.get_ticks()

    def update(self, **kwargs):
        super().update(**kwargs)
        defenders_group = kwargs.get('defenders_group')
        if not defenders_group or not self.alive(): return

        if self.is_being_eaten: return

        now = pygame.time.get_ticks()
        if now - self.last_heal_time > self.heal_cooldown:
            self.last_heal_time = now
            healed = self.heal(defenders_group)
            # Запускаем анимацию, только если лечение произошло
            if healed and self.heal_pool > 0:
                self.current_animation = 'attack'
                self.frame_index = 0
        # Медик исчезает, когда его "мана" заканчивается
        if self.heal_pool <= 0:
            self.kill()

    def find_most_wounded_ally_in_range(self, defenders_group):
        """Находит союзника с наименьшим процентом здоровья в радиусе."""
        pixel_radius = self.heal_radius * CELL_SIZE_W
        allies_in_range = [
            d for d in defenders_group
            if d.alive() and d is not self and d.health < d.max_health and
               pygame.math.Vector2(self.rect.center).distance_to(d.rect.center) <= pixel_radius
        ]
        if not allies_in_range:
            return None
        # Ключ для сортировки - процент здоровья, чтобы лечить наиболее раненых
        return min(allies_in_range, key=lambda d: d.health / d.max_health)

    def heal(self, defenders_group):
        """Лечит найденную цель."""
        target = self.find_most_wounded_ally_in_range(defenders_group)
        if target:
            heal_amount = min(self.heal_tick_amount, self.heal_pool)
            target.health = min(target.max_health, target.health + heal_amount)
            self.heal_pool -= heal_amount
            return True
        return False


class Artist(Defender):
    """Стрелок, чьи атаки замедляют врагов."""
    def __init__(self, x, y, groups, data, sound_manager, all_sprites, projectile_group, enemies_group):
        super().__init__(x, y, groups, data, sound_manager)
        self.all_sprites = all_sprites
        self.projectile_group = projectile_group
        self.attack_cooldown = self.data['cooldown'] * 1000
        self.last_shot = pygame.time.get_ticks()

    def update(self, **kwargs):
        super().update(**kwargs)
        enemies_group = kwargs.get('enemies_group')
        if not enemies_group: return

        if self.is_being_eaten: return

        now = pygame.time.get_ticks()
        has_enemy_in_row = any(
            enemy.rect.centery == self.rect.centery and enemy.rect.left >= self.rect.left
            for enemy in enemies_group)

        if self.alive() and has_enemy_in_row and now - self.last_shot > self.attack_cooldown:
            self.last_shot = now
            damage = self.get_final_damage(self.data['damage'])
            # Создаем особый снаряд, который несет в себе ссылку на художника
            PaintSplat(self.rect.right, self.rect.centery, (self.all_sprites, self.projectile_group), damage, self)
            self.current_animation = 'attack'
            self.frame_index = 0


class Fashionista(Defender):
    """Юнит-камикадзе, который ищет ближайшего врага и взрывается."""
    def __init__(self, x, y, groups, data, sound_manager, all_sprites, enemies_group):
        super().__init__(x, y, groups, data, sound_manager)
        self.all_sprites = all_sprites
        self.speed = data['speed']
        self.explosion_radius = data['radius']
        self.damage = data['damage']
        self.state = 'SEEKING'  # Начальное состояние - поиск цели
        self.target = None

    def update(self, **kwargs):
        enemies_group = kwargs.get('enemies_group')
        if not enemies_group or not self.alive():
            return

        # Если уже столкнулся с врагом, взрывается
        if pygame.sprite.spritecollideany(self, enemies_group):
            self.explode(enemies_group)
            return

        if self.state == 'SEEKING':
            self.target = self.find_closest_enemy(enemies_group)
            if self.target:
                self.state = 'WALKING'
        elif self.state == 'WALKING':
            # Если цель исчезла, ищем новую
            if not self.target or not self.target.alive():
                self.state = 'SEEKING'
                return
            # Движемся в направлении цели
            direction = pygame.math.Vector2(self.target.rect.center) - pygame.math.Vector2(self.rect.center)
            if direction.length() > 0:
                self.rect.move_ip(direction.normalize() * self.speed)

        super().update(**kwargs)

    def find_closest_enemy(self, enemies_group):
        """Находит ближайшего врага на всем поле."""
        closest_enemy = None
        min_dist = float('inf')
        for enemy in enemies_group:
            dist = pygame.math.Vector2(self.rect.center).distance_to(enemy.rect.center)
            if dist < min_dist:
                min_dist = dist
                closest_enemy = enemy
        return closest_enemy

    def explode(self, enemies_group):
        """Создает эффект взрыва и наносит урон всем врагам в радиусе."""
        if not self.alive(): return

        self.sound_manager.play_sfx('explosion')

        pixel_radius = self.explosion_radius * CELL_SIZE_W
        ExplosionEffect(self.rect.center, pixel_radius, self.all_sprites)
        for enemy in enemies_group:
            if pygame.math.Vector2(self.rect.center).distance_to(enemy.rect.center) <= pixel_radius:
                enemy.get_hit(self.damage)
        self.kill()

    def kill(self):
        """Переопределенный метод, чтобы убрать стандартный звук смерти героя."""
        if self.alive():
             pygame.sprite.Sprite.kill(self)