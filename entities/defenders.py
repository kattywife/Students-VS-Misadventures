# entities/defenders.py

import pygame
import os
import random
from data.settings import *
from data.assets import SOUNDS, load_image, PROJECTILE_IMAGES
from data.settings import PROGRAMMER_PROJECTILE_TYPES
from entities.base_sprite import BaseSprite, ExplosionEffect, BookAttackEffect
from entities.projectiles import Bracket, PaintSplat, SoundWave
from entities.other_sprites import CoffeeBean, AuraEffect


class Defender(BaseSprite):
    def __init__(self, x, y, groups, data):
        super().__init__(groups)
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
        self.anim_speed = self.data.get('animation_data', {}).get('speed', 0.2)

        self._layer = self.rect.bottom
        self.is_animate = 'animation_data' in self.data

        self.is_being_eaten = False
        self.scream_channel = None
        self.is_upgraded = False
        self.buff_multiplier = 1.0
        self.calamity_damage_multiplier = 1.0

    def load_animations(self):
        anim_data = self.data.get('animation_data')
        if not anim_data:
            return

        size = (CELL_SIZE_W - 10, CELL_SIZE_H - 10)
        category = self.data.get('category', 'defenders')
        folder = anim_data.get('folder', self.data.get('type'))

        for anim_type, frame_count in anim_data.items():
            if anim_type not in ['folder', 'speed']:
                self.animations[anim_type] = []
                for i in range(frame_count):
                    filename = f"{anim_type}_{i}.png"
                    path = os.path.join(category, folder, filename)
                    img = load_image(path, DEFAULT_COLORS.get(self.data['type']), size)
                    self.animations[anim_type].append(img)

    def animate(self):
        if not self.animations or self.current_animation not in self.animations:
            return
        if self.is_being_eaten and 'hit' in self.animations:
            self.current_animation = 'hit'
        elif not self.is_being_eaten and self.current_animation == 'hit':
            self.current_animation = 'idle'
        now = pygame.time.get_ticks()
        if now - self.last_anim_update > self.anim_speed * 1000:
            self.last_anim_update = now
            self.frame_index += 1
            anim_sequence = self.animations[self.current_animation]
            if self.frame_index >= len(anim_sequence):
                if self.current_animation == 'attack':
                    self.current_animation = 'idle'
                self.frame_index = 0
            self.image = self.animations[self.current_animation][self.frame_index]

    def get_final_damage(self, base_damage):
        return base_damage * self.buff_multiplier * self.calamity_damage_multiplier

    def apply_calamity_effect(self, calamity_type):
        if calamity_type == 'epidemic':
            self.calamity_damage_multiplier /= 2
            self.health /= 2

    def revert_calamity_effect(self, calamity_type):
        if calamity_type == 'epidemic':
            self.calamity_damage_multiplier *= 2

    def update(self, *args, **kwargs):
        self.animate()
        if self.is_animate:
            self.manage_scream_sound()
        if self.health <= 0:
            if self.is_animate and SOUNDS.get('hero_dead'): SOUNDS['hero_dead'].play()
            self.stop_scream()
            self.kill()

    def manage_scream_sound(self):
        scream_sound = SOUNDS.get('scream')
        if not scream_sound: return
        if self.is_being_eaten and not (self.scream_channel and self.scream_channel.get_busy()):
            self.scream_channel = pygame.mixer.find_channel()
            if self.scream_channel: self.scream_channel.play(scream_sound, -1)
        elif not self.is_being_eaten and self.scream_channel:
            self.stop_scream()

    def stop_scream(self):
        if self.scream_channel:
            self.scream_channel.stop()
            self.scream_channel = None

    def draw_aura(self, surface):
        if self.is_upgraded:
            aura_surf = pygame.Surface(self.rect.size, pygame.SRCALPHA)
            pygame.draw.ellipse(aura_surf, AURA_PINK, aura_surf.get_rect())
            surface.blit(aura_surf, self.rect.topleft)


class ProgrammerBoy(Defender):
    def __init__(self, x, y, groups, data, all_sprites, projectile_group, enemies_group):
        super().__init__(x, y, groups, data)
        self.all_sprites = all_sprites
        self.projectile_group = projectile_group
        self.enemies_group = enemies_group
        self.attack_cooldown = self.data['cooldown'] * 1000
        self.last_shot = pygame.time.get_ticks()

    def update(self, *args, **kwargs):
        super().update(*args, **kwargs)
        now = pygame.time.get_ticks()
        has_enemy_in_row = any(
            enemy.rect.centery == self.rect.centery and enemy.rect.right < SCREEN_WIDTH for enemy in self.enemies_group)
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
    def __init__(self, x, y, groups, data, all_sprites, enemies_group):
        super().__init__(x, y, groups, data)
        self.all_sprites = all_sprites
        self.enemies_group = enemies_group
        self.attack_cooldown = self.data['cooldown'] * 1000
        self.last_attack = pygame.time.get_ticks()
        self.explosion_radius = self.data['radius']

    def update(self, *args, **kwargs):
        super().update(*args, **kwargs)
        now = pygame.time.get_ticks()
        if self.alive() and now - self.last_attack > self.attack_cooldown:
            target = self.find_strongest_enemy()
            if target:
                self.last_attack = now
                self.attack(target)
                self.current_animation = 'attack'
                self.frame_index = 0

    def find_strongest_enemy(self):
        visible_enemies = [e for e in self.enemies_group if e.rect.right < SCREEN_WIDTH]
        if not visible_enemies: return None
        return max(visible_enemies, key=lambda e: e.health)

    def attack(self, target):
        damage = self.get_final_damage(self.data['damage'])
        explosion_center = target.rect.center
        BookAttackEffect(explosion_center, self.all_sprites, self.explosion_radius * 2)
        for enemy in self.enemies_group:
            if pygame.math.Vector2(enemy.rect.center).distance_to(explosion_center) <= self.explosion_radius:
                enemy.get_hit(damage)


class CoffeeMachine(Defender):
    def __init__(self, x, y, groups, data, all_sprites, coffee_bean_group):
        super().__init__(x, y, groups, data)
        self.all_sprites = all_sprites
        self.coffee_bean_group = coffee_bean_group
        self.production_cooldown = self.data['cooldown'] * 1000
        self.last_production = pygame.time.get_ticks()
        self.is_producing = False
        self.producing_timer = 0
        self.producing_duration = 500
        self.producing_frame = self.animations.get('attack', [None])[0]

    def animate(self):
        if self.is_producing:
            self.image = self.producing_frame
        else:
            now = pygame.time.get_ticks()
            if now - self.last_anim_update > self.anim_speed * 1000:
                self.last_anim_update = now
                self.frame_index = (self.frame_index + 1) % len(self.animations['idle'])
                self.image = self.animations['idle'][self.frame_index]

    def update(self, *args, **kwargs):
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
    def __init__(self, x, y, groups, data, all_sprites):
        super().__init__(x, y, groups, data)
        self.all_sprites = all_sprites
        AuraEffect((self.all_sprites,), self)


class Guitarist(Defender):
    def __init__(self, x, y, groups, data, all_sprites, enemies_group):
        super().__init__(x, y, groups, data)
        self.all_sprites = all_sprites
        self.enemies_group = enemies_group
        self.attack_cooldown = self.data['cooldown'] * 1000
        self.last_attack = pygame.time.get_ticks()

    def update(self, *args, **kwargs):
        super().update(*args, **kwargs)
        now = pygame.time.get_ticks()
        if self.alive() and now - self.last_attack > self.attack_cooldown:
            has_enemy_in_row = any(
                e.rect.centery == self.rect.centery and e.rect.right < SCREEN_WIDTH for e in self.enemies_group)
            if has_enemy_in_row:
                self.last_attack = now
                damage = self.get_final_damage(self.data['damage'])
                speed = self.data.get('projectile_speed', 5)
                SoundWave(self.rect.center, (self.all_sprites,), damage, self.rect.centery, speed)
                self.current_animation = 'attack'
                self.frame_index = 0


class Medic(Defender):
    def __init__(self, x, y, groups, data, defenders_group):
        super().__init__(x, y, groups, data)
        self.defenders_group = defenders_group
        self.heal_pool = self.data['heal_amount']
        self.heal_radius = self.data['radius']
        self.heal_tick_amount = 20
        self.heal_cooldown = self.data['cooldown'] * 1000
        self.last_heal_time = pygame.time.get_ticks()

    def update(self, *args, **kwargs):
        super().update(*args, **kwargs)
        if not self.alive(): return
        now = pygame.time.get_ticks()
        if now - self.last_heal_time > self.heal_cooldown:
            self.last_heal_time = now
            self.heal()
            if self.heal_pool > 0:
                self.current_animation = 'attack'
                self.frame_index = 0
        if self.heal_pool <= 0:
            self.kill()

    def find_most_wounded_ally_in_range(self):
        most_wounded = None
        min_health_ratio = 1.0
        allies_in_range = [
            d for d in self.defenders_group
            if d.alive() and d is not self and d.health < d.max_health and
               pygame.math.Vector2(self.rect.center).distance_to(d.rect.center) <= self.heal_radius
        ]
        if not allies_in_range:
            return None
        return min(allies_in_range, key=lambda d: d.health / d.max_health)

    def heal(self):
        target = self.find_most_wounded_ally_in_range()
        if target:
            heal_amount = min(self.heal_tick_amount, self.heal_pool)
            target.health = min(target.max_health, target.health + heal_amount)
            self.heal_pool -= heal_amount


class Artist(Defender):
    def __init__(self, x, y, groups, data, all_sprites, projectile_group, enemies_group):
        super().__init__(x, y, groups, data)
        self.all_sprites = all_sprites
        self.projectile_group = projectile_group
        self.enemies_group = enemies_group
        self.attack_cooldown = self.data['cooldown'] * 1000
        self.last_shot = pygame.time.get_ticks()

    def update(self, *args, **kwargs):
        super().update(*args, **kwargs)
        now = pygame.time.get_ticks()
        has_enemy_in_row = any(enemy.rect.centery == self.rect.centery for enemy in self.enemies_group)
        if self.alive() and has_enemy_in_row and now - self.last_shot > self.attack_cooldown:
            self.last_shot = now
            damage = self.get_final_damage(self.data['damage'])
            PaintSplat(self.rect.right, self.rect.centery, (self.all_sprites, self.projectile_group), damage, self)
            self.current_animation = 'attack'
            self.frame_index = 0


class Fashionista(Defender):
    def __init__(self, x, y, groups, data, all_sprites, enemies_group):
        super().__init__(x, y, groups, data)
        self.all_sprites = all_sprites
        self.enemies_group = enemies_group
        self.speed = data['speed']
        self.explosion_radius = data['radius']
        self.damage = data['damage']
        self.state = 'SEEKING'
        self.target = None

    def update(self, *args, **kwargs):
        super().update(*args, **kwargs)
        if not self.alive(): return
        if self.state == 'SEEKING':
            self.target = self.find_closest_enemy()
            if self.target:
                self.state = 'WALKING'
        elif self.state == 'WALKING':
            if not self.target or not self.target.alive():
                self.state = 'SEEKING'
                return
            direction = pygame.math.Vector2(self.target.rect.center) - pygame.math.Vector2(self.rect.center)
            if direction.length() > 0:
                self.rect.move_ip(direction.normalize() * self.speed)
            if self.rect.colliderect(self.target.rect):
                self.explode()

    def find_closest_enemy(self):
        closest_enemy = None
        min_dist = float('inf')
        visible_enemies = [e for e in self.enemies_group if e.rect.right < SCREEN_WIDTH]
        for enemy in visible_enemies:
            dist = pygame.math.Vector2(self.rect.center).distance_to(enemy.rect.center)
            if dist < min_dist:
                min_dist = dist
                closest_enemy = enemy
        return closest_enemy

    def explode(self):
        if SOUNDS.get('explosion'):
            SOUNDS['explosion'].play()
        ExplosionEffect(self.rect.center, self.explosion_radius, self.all_sprites)
        for enemy in self.enemies_group:
            if pygame.math.Vector2(self.rect.center).distance_to(enemy.rect.center) <= self.explosion_radius:
                enemy.get_hit(self.damage)
        self.kill()