# entities/defenders.py

import pygame
import os
import random
from data.settings import *
from data.assets import PROJECTILE_IMAGES, load_image
from data.settings import PROGRAMMER_PROJECTILE_TYPES
from entities.base_sprite import BaseSprite, ExplosionEffect, BookAttackEffect
from entities.projectiles import Bracket, PaintSplat, SoundWave
from entities.other_sprites import CoffeeBean, AuraEffect


class Defender(BaseSprite):
    def __init__(self, x, y, groups, data, sound_manager):
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

        self.is_being_eaten = False
        self.scream_channel = None
        self.attacker = None
        self.is_upgraded = False
        self.buff_multiplier = 1.0
        self.calamity_damage_multiplier = 1.0

    def get_hit(self, damage):
        self.health -= damage
        self.sound_manager.play_sfx('damage')
        if 'hit' in self.animations and self.animations['hit']:
            self.current_animation = 'hit'
            self.frame_index = 0

    def load_animations(self):
        anim_data = self.data.get('animation_data')
        if not anim_data:
            return

        size = (CELL_SIZE_W - 10, CELL_SIZE_H - 10)
        category = self.data.get('category', 'defenders')
        folder = anim_data.get('folder', self.data.get('type'))

        for anim_type in anim_data:
            if anim_type not in ['folder', 'speed']:
                self.animations[anim_type] = []
                path_to_folder = os.path.join(IMAGES_DIR, category, folder)
                if os.path.exists(path_to_folder):
                    filenames = sorted(
                        [f for f in os.listdir(path_to_folder) if f.startswith(f"{anim_type}_") and f.endswith('.png')])
                    for filename in filenames:
                        path = os.path.join(category, folder, filename)
                        img = load_image(path, DEFAULT_COLORS.get(self.data['type']), size)
                        self.animations[anim_type].append(img)

                if not self.animations[anim_type]:
                    fallback_surface = pygame.Surface(size, pygame.SRCALPHA)
                    fallback_surface.fill((0, 0, 0, 0))
                    self.animations[anim_type].append(fallback_surface)

    def animate(self):
        if not self.animations or not self.animations.get(self.current_animation):
            return

        anim_sequence = self.animations[self.current_animation]

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

            if self.frame_index >= len(anim_sequence):
                if self.current_animation in ['attack', 'hit']:
                    self.current_animation = 'idle'
                self.frame_index = 0

    def get_final_damage(self, base_damage):
        return base_damage * self.buff_multiplier * self.calamity_damage_multiplier

    def apply_calamity_effect(self, calamity_type):
        if calamity_type == 'epidemic':
            self.calamity_damage_multiplier /= 2
            self.health /= 2

    def revert_calamity_effect(self, calamity_type):
        if calamity_type == 'epidemic':
            self.calamity_damage_multiplier *= 2

    def update(self, **kwargs):
        if self.is_being_eaten and (not self.attacker or not self.attacker.alive()):
            self.is_being_eaten = False
            self.attacker = None

        self.animate()
        if self.is_animate:
            self.manage_scream_sound()
        if self.health <= 0:
            self.kill()

    def manage_scream_sound(self):
        if self.is_being_eaten and not (self.scream_channel and self.scream_channel.get_busy()):
            self.scream_channel = self.sound_manager.play_sfx('scream')
        elif not self.is_being_eaten and self.scream_channel:
            self.scream_channel.stop()
            self.scream_channel = None

    def draw_aura(self, surface):
        if self.is_upgraded:
            aura_surf = pygame.Surface(self.rect.size, pygame.SRCALPHA)
            pygame.draw.ellipse(aura_surf, AURA_PINK, aura_surf.get_rect())
            surface.blit(aura_surf, self.rect.topleft)

    def kill(self):
        if not self.alive():
            return
        if self.scream_channel:
            self.scream_channel.stop()
            self.scream_channel = None
        if self.is_animate:
            self.sound_manager.play_sfx('hero_dead')
        super().kill()


class ProgrammerBoy(Defender):
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
        # --- ИСПРАВЛЕНИЕ: Добавлена проверка положения врага по горизонтали ---
        has_enemy_in_row = any(
            enemy.rect.centery == self.rect.centery and enemy.rect.left >= self.rect.left
            for enemy in enemies_group)

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
        if not enemies_group: return

        if self.is_being_eaten: return

        now = pygame.time.get_ticks()
        if self.alive() and now - self.last_attack > self.attack_cooldown:
            target = self.find_strongest_enemy(enemies_group)
            if target:
                self.last_attack = now
                self.attack(target, enemies_group)
                self.current_animation = 'attack'
                self.frame_index = 0

    def find_strongest_enemy(self, enemies_group):
        if not enemies_group:
            return None
        return max(enemies_group, key=lambda e: e.health)

    def attack(self, target, enemies_group):
        damage = self.get_final_damage(self.data['damage'])
        explosion_center = target.rect.center
        pixel_radius = self.explosion_radius * CELL_SIZE_W
        BookAttackEffect(explosion_center, self.all_sprites, pixel_radius * 2)
        for enemy in enemies_group:
            if pygame.math.Vector2(enemy.rect.center).distance_to(explosion_center) <= pixel_radius:
                enemy.get_hit(damage)


class CoffeeMachine(Defender):
    def __init__(self, x, y, groups, data, sound_manager, all_sprites, coffee_bean_group):
        super().__init__(x, y, groups, data, sound_manager)
        self.all_sprites = all_sprites
        self.coffee_bean_group = coffee_bean_group
        self.production_cooldown = self.data['cooldown'] * 1000
        self.last_production = pygame.time.get_ticks()
        self.is_producing = False
        self.producing_timer = 0
        self.producing_duration = 500
        self.producing_frame = self.animations.get('attack', [None])[0] or self.animations.get('idle', [None])[0]

    def kill(self):
        pygame.sprite.Sprite.kill(self)

    def manage_scream_sound(self):
        pass

    def get_hit(self, damage):
        super().get_hit(damage)

    def animate(self):
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
    def __init__(self, x, y, groups, data, sound_manager, all_sprites):
        super().__init__(x, y, groups, data, sound_manager)
        self.all_sprites = all_sprites
        AuraEffect((self.all_sprites,), self)


class Guitarist(Defender):
    def __init__(self, x, y, groups, data, sound_manager, all_sprites, enemies_group):
        super().__init__(x, y, groups, data, sound_manager)
        self.all_sprites = all_sprites
        self.attack_cooldown = self.data['cooldown'] * 1000
        self.last_attack = pygame.time.get_ticks()

    def update(self, **kwargs):
        super().update(**kwargs)
        enemies_group = kwargs.get('enemies_group')
        if not enemies_group: return

        if self.is_being_eaten: return

        now = pygame.time.get_ticks()
        # --- ИСПРАВЛЕНИЕ: Добавлена проверка положения врага по горизонтали ---
        has_enemy_in_row = any(
            e.rect.centery == self.rect.centery and e.rect.left >= self.rect.left
            for e in enemies_group)

        if self.alive() and has_enemy_in_row and now - self.last_attack > self.attack_cooldown:
            self.last_attack = now
            damage = self.get_final_damage(self.data['damage'])
            speed = self.data.get('projectile_speed', 5)
            SoundWave(self.rect.center, (self.all_sprites,), damage, self.rect.centery, speed)
            self.current_animation = 'attack'
            self.frame_index = 0


class Medic(Defender):
    def __init__(self, x, y, groups, data, sound_manager, defenders_group):
        super().__init__(x, y, groups, data, sound_manager)
        self.heal_pool = self.data['heal_amount']
        self.heal_radius = self.data['radius']
        self.heal_tick_amount = 75
        self.heal_cooldown = self.data['cooldown'] * 3000
        self.last_heal_time = pygame.time.get_ticks()

    def update(self, **kwargs):
        super().update(**kwargs)
        defenders_group = kwargs.get('defenders_group')
        if not defenders_group or not self.alive(): return

        if self.is_being_eaten: return

        now = pygame.time.get_ticks()
        if now - self.last_heal_time > self.heal_cooldown:
            self.last_heal_time = now
            self.heal(defenders_group)
            if self.heal_pool > 0:
                self.current_animation = 'attack'
                self.frame_index = 0
        if self.heal_pool <= 0:
            self.kill()

    def find_most_wounded_ally_in_range(self, defenders_group):
        pixel_radius = self.heal_radius * CELL_SIZE_W
        allies_in_range = [
            d for d in defenders_group
            if d.alive() and d is not self and d.health < d.max_health and
               pygame.math.Vector2(self.rect.center).distance_to(d.rect.center) <= pixel_radius
        ]
        if not allies_in_range:
            return None
        return min(allies_in_range, key=lambda d: d.health / d.max_health)

    def heal(self, defenders_group):
        target = self.find_most_wounded_ally_in_range(defenders_group)
        if target:
            heal_amount = min(self.heal_tick_amount, self.heal_pool)
            target.health = min(target.max_health, target.health + heal_amount)
            self.heal_pool -= heal_amount


class Artist(Defender):
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
        # --- ИСПРАВЛЕНИЕ: Добавлена проверка положения врага по горизонтали ---
        has_enemy_in_row = any(
            enemy.rect.centery == self.rect.centery and enemy.rect.left >= self.rect.left
            for enemy in enemies_group)

        if self.alive() and has_enemy_in_row and now - self.last_shot > self.attack_cooldown:
            self.last_shot = now
            damage = self.get_final_damage(self.data['damage'])
            PaintSplat(self.rect.right, self.rect.centery, (self.all_sprites, self.projectile_group), damage, self)
            self.current_animation = 'attack'
            self.frame_index = 0


class Fashionista(Defender):
    def __init__(self, x, y, groups, data, sound_manager, all_sprites, enemies_group):
        super().__init__(x, y, groups, data, sound_manager)
        self.all_sprites = all_sprites
        self.speed = data['speed']
        self.explosion_radius = data['radius']
        self.damage = data['damage']
        self.state = 'SEEKING'
        self.target = None

    def update(self, **kwargs):
        enemies_group = kwargs.get('enemies_group')
        if not enemies_group or not self.alive():
            return

        if pygame.sprite.spritecollideany(self, enemies_group):
            self.explode(enemies_group)
            return

        if self.state == 'SEEKING':
            self.target = self.find_closest_enemy(enemies_group)
            if self.target:
                self.state = 'WALKING'
        elif self.state == 'WALKING':
            if not self.target or not self.target.alive():
                self.state = 'SEEKING'
                return
            direction = pygame.math.Vector2(self.target.rect.center) - pygame.math.Vector2(self.rect.center)
            if direction.length() > 0:
                self.rect.move_ip(direction.normalize() * self.speed)

        super().update(**kwargs)

    def find_closest_enemy(self, enemies_group):
        closest_enemy = None
        min_dist = float('inf')
        for enemy in enemies_group:
            dist = pygame.math.Vector2(self.rect.center).distance_to(enemy.rect.center)
            if dist < min_dist:
                min_dist = dist
                closest_enemy = enemy
        return closest_enemy

    def explode(self, enemies_group):
        if not self.alive(): return

        self.sound_manager.play_sfx('explosion')

        pixel_radius = self.explosion_radius * CELL_SIZE_W
        ExplosionEffect(self.rect.center, pixel_radius, self.all_sprites)
        for enemy in enemies_group:
            if pygame.math.Vector2(self.rect.center).distance_to(enemy.rect.center) <= pixel_radius:
                enemy.get_hit(self.damage)
        self.kill()

    def kill(self):
        pygame.sprite.Sprite.kill(self)