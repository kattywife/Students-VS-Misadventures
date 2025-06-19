# entities/enemies.py

import pygame
import random
import os
import math
from data.settings import *
from data.assets import load_image, PROJECTILE_IMAGES
from entities.base_sprite import BaseSprite
from entities.projectiles import Integral
from entities.defenders import CoffeeMachine
from entities.other_sprites import CalamityAuraEffect


class Enemy(BaseSprite):
    def __init__(self, row, groups, enemy_type, sound_manager):
        super().__init__(groups)
        self.sound_manager = sound_manager
        self.data = ENEMIES_DATA[enemy_type]
        self.enemy_type = enemy_type
        self.max_health = self.data['health']
        self.health = self.max_health
        self.speed = self.data['speed']
        self.original_speed = self.data['speed']
        self.damage = self.data['damage']
        self.damage_multiplier = 1.0

        self.all_sprites_group = groups[1]
        self.aura_effect = None

        self.animations = {}
        self.load_animations()
        self.current_animation = 'walk'
        self.frame_index = 0
        self.image = self.animations.get(self.current_animation, [pygame.Surface((0, 0))])[0]

        y = GRID_START_Y + row * CELL_SIZE_H + CELL_SIZE_H / 2
        self.rect = self.image.get_rect(center=(SCREEN_WIDTH, y))
        self.float_pos = pygame.math.Vector2(self.rect.center)
        self._layer = self.rect.bottom

        self.anim_speed = self.data.get('animation_data', {}).get('speed', 0.3)
        self.last_anim_update = pygame.time.get_ticks()

        self.attack_cooldown = self.data['cooldown'] * 1000 if self.data['cooldown'] else DEFAULT_ATTACK_COOLDOWN_MS
        self.last_attack_time = 0

        self.current_target = None
        self.slow_timer = 0
        self.is_slowed = False
        self.is_attacking = False

    def load_animations(self):
        anim_data = self.data.get('animation_data')
        if not anim_data: return

        size = (CELL_SIZE_W - 20, CELL_SIZE_H - 10)
        category = self.data.get('category', 'enemies')
        folder = anim_data.get('folder', self.enemy_type)

        for anim_type in anim_data:
            if anim_type not in ['folder', 'speed']:
                self.animations[anim_type] = []
                path_to_folder = os.path.join(IMAGES_DIR, category, folder)
                if os.path.exists(path_to_folder):
                    filenames = sorted(
                        [f for f in os.listdir(path_to_folder) if f.startswith(f"{anim_type}_") and f.endswith('.png')])
                    for filename in filenames:
                        path = os.path.join(category, folder, filename)
                        img = load_image(path, DEFAULT_COLORS.get(self.enemy_type), size)
                        self.animations[anim_type].append(img)

                if not self.animations[anim_type]:
                    fallback_surface = pygame.Surface(size, pygame.SRCALPHA)
                    fallback_surface.fill((0, 0, 0, 0))
                    self.animations[anim_type].append(fallback_surface)

    def set_animation(self, new_animation_type):
        if self.current_animation != new_animation_type and new_animation_type in self.animations:
            self.current_animation = new_animation_type
            self.frame_index = 0

    def animate(self):
        if not self.animations or not self.animations.get(self.current_animation): return

        if self.current_animation != 'hit':
            if self.is_attacking:
                self.set_animation('attack')
            else:
                self.set_animation('walk')

        anim_sequence = self.animations[self.current_animation]
        now = pygame.time.get_ticks()
        if now - self.last_anim_update > self.anim_speed * 1000:
            self.last_anim_update = now
            self.frame_index = (self.frame_index + 1) % len(anim_sequence)
            if self.frame_index == 0 and self.current_animation in ['hit', 'attack']:
                 self.set_animation('walk')

        self.image = anim_sequence[self.frame_index]

    def get_hit(self, damage):
        self.health -= damage
        self.sound_manager.play_sfx('damage')
        if 'hit' in self.animations and self.animations['hit']:
            self.set_animation('hit')

    def apply_calamity_effect(self, calamity_type):
        if calamity_type == 'colloquium':
            self.damage_multiplier *= CALAMITY_COLLOQUIUM_MULTIPLIER
        elif calamity_type == 'internet_down':
            ratio = self.health / self.max_health if self.max_health > 0 else 1.0
            self.max_health *= CALAMITY_INTERNET_DOWN_MULTIPLIER
            self.health = self.max_health * ratio

        if calamity_type != 'big_party' and not self.aura_effect:
            self.aura_effect = CalamityAuraEffect((self.all_sprites_group,), self, calamity_type)

    def revert_calamity_effect(self, calamity_type):
        if calamity_type == 'colloquium':
            self.damage_multiplier /= CALAMITY_COLLOQUIUM_MULTIPLIER
        elif calamity_type == 'internet_down':
            ratio = self.health / self.max_health if self.max_health > 0 else 1.0
            self.max_health /= CALAMITY_INTERNET_DOWN_MULTIPLIER
            self.health = max(1, self.max_health * ratio)

        if self.aura_effect:
            self.aura_effect.kill()
            self.aura_effect = None

    def get_melee_target(self, defenders_group):
        if not defenders_group:
            return None
        for defender in defenders_group:
            if defender.alive() and self.rect.colliderect(defender.rect) and defender.rect.centery == self.rect.centery:
                return defender
        return None

    def perform_melee_attack(self, target):
        self.is_attacking = True
        self.rect.right = target.rect.centerx + ENEMY_ATTACK_OFFSET
        self.float_pos.x = self.rect.centerx
        self._layer = target._layer + 1

        if self.current_target != target:
            if self.current_target:
                self.current_target.is_being_eaten = False
                self.current_target.attacker = None
            self.current_target = target

        if self.current_target:
            self.current_target.is_being_eaten = True
            self.current_target.attacker = self

        now = pygame.time.get_ticks()
        if now - self.last_attack_time > self.attack_cooldown:
            self.last_attack_time = now
            self.sound_manager.play_sfx('eating')
            target.get_hit(self.damage * self.damage_multiplier)

    def update(self, **kwargs):
        defenders_group = kwargs.get('defenders_group')

        self.animate()
        self._layer = self.rect.bottom

        if self.current_target and not self.current_target.alive():
            self.current_target.is_being_eaten = False
            self.current_target = None
            self.is_attacking = False

        if self.health <= 0:
            self.kill()
            return

        if self.is_slowed and pygame.time.get_ticks() > self.slow_timer:
            self.speed = self.original_speed
            self.is_slowed = False

        target = self.get_melee_target(defenders_group)
        if target:
            self.perform_melee_attack(target)
        else:
            self.is_attacking = False
            if self.current_target:
                self.current_target.is_being_eaten = False
                self.current_target = None
            self.float_pos.x -= self.speed
            self.rect.centerx = int(self.float_pos.x)

    def kill(self):
        if self.alive():
            if self.aura_effect:
                self.aura_effect.kill()
                self.aura_effect = None

            self.sound_manager.play_sfx('enemy_dead')
            if self.current_target:
                self.current_target.is_being_eaten = False
            super().kill()

    def slow_down(self, factor, duration):
        if not self.is_slowed:
            self.speed = self.original_speed * factor
            self.is_slowed = True
        self.slow_timer = pygame.time.get_ticks() + duration


class Calculus(Enemy):
    def __init__(self, row, groups, enemy_type, sound_manager):
        super().__init__(row, groups, enemy_type, sound_manager)
        self.last_shot = pygame.time.get_ticks()

    def update(self, **kwargs):
        self.animate()
        self._layer = self.rect.bottom

        if self.health <= 0:
            self.kill()
            return

        if self.is_slowed and pygame.time.get_ticks() > self.slow_timer:
            self.speed = self.original_speed
            self.is_slowed = False

        defenders_group = kwargs.get('defenders_group')
        all_sprites = kwargs.get('all_sprites')
        projectiles = kwargs.get('projectiles')

        is_shooting = False
        if defenders_group:
            is_shooting = any(
                d.alive() and d.rect.centery == self.rect.centery and d.rect.right < self.rect.left
                for d in defenders_group
            ) and self.rect.right < SCREEN_WIDTH

        self.is_attacking = is_shooting

        if is_shooting:
            now = pygame.time.get_ticks()
            if now - self.last_shot > self.attack_cooldown:
                self.last_shot = now
                damage = self.damage * self.damage_multiplier
                random_projectile_type = random.choice(CALCULUS_PROJECTILE_TYPES)
                projectile_image = PROJECTILE_IMAGES[random_projectile_type]
                Integral(self.rect.left, self.rect.centery, (all_sprites, projectiles), damage, projectile_image)
        else:
            self.float_pos.x -= self.speed
            self.rect.centerx = int(self.float_pos.x)


class MathTeacher(Enemy):
    def __init__(self, row, groups, enemy_type, sound_manager):
        super().__init__(row, groups, enemy_type, sound_manager)
        self.state = 'WALKING'
        self.has_jumped = False
        self.original_y = self.float_pos.y

        self.jump_height = MATH_TEACHER_JUMP_HEIGHT
        self.jump_duration = MATH_TEACHER_JUMP_DURATION
        self.jump_timer = 0
        self.jump_start_pos = None
        self.jump_target_pos = None

    def update(self, **kwargs):
        self.animate()
        self._layer = self.rect.bottom
        if self.health <= 0: self.kill(); return

        if self.is_slowed and pygame.time.get_ticks() > self.slow_timer:
            self.speed = self.original_speed
            self.is_slowed = False

        if self.has_jumped:
            super().update(**kwargs)
            return

        defenders_group = kwargs.get('defenders_group')

        if self.state == 'WALKING':
            target = self.find_jump_target(defenders_group)
            if target:
                self.state = 'JUMPING'
                self.is_attacking = True
                self.jump_timer = pygame.time.get_ticks()
                self.jump_start_pos = self.float_pos.copy()
                target_x = target.rect.centerx - CELL_SIZE_W
                self.jump_target_pos = pygame.math.Vector2(target_x, self.original_y)
            else:
                self.float_pos.x -= self.speed
                self.rect.centerx = int(self.float_pos.x)

        elif self.state == 'JUMPING':
            elapsed_time = pygame.time.get_ticks() - self.jump_timer
            progress = min(1.0, elapsed_time / self.jump_duration)

            self.float_pos.x = self.jump_start_pos.x + (self.jump_target_pos.x - self.jump_start_pos.x) * progress
            y_offset = math.sin(progress * math.pi) * self.jump_height
            self.float_pos.y = self.original_y - y_offset
            self.rect.center = (int(self.float_pos.x), int(self.float_pos.y))

            if progress >= 1.0:
                self.float_pos = self.jump_target_pos.copy()
                self.rect.center = (int(self.float_pos.x), int(self.float_pos.y))
                self.state = 'WALKING'
                self.is_attacking = False
                self.has_jumped = True
                self.speed /= 2.0

    def find_jump_target(self, defenders_group):
        for defender in defenders_group:
            if defender.alive() and self.rect.colliderect(defender.rect) and defender.rect.centery == self.rect.centery:
                return defender
        return None


class Addict(Enemy):
    def __init__(self, row, groups, enemy_type, sound_manager):
        super().__init__(row, groups, enemy_type, sound_manager)
        self.state = 'SEEKING'
        self.target_defender = None
        self.victim = None

    def find_strongest_defender(self, defenders_group):
        living_defenders = [d for d in defenders_group if d.alive() and not isinstance(d, CoffeeMachine)]
        if not living_defenders: return None
        return max(living_defenders, key=lambda d: d.get_final_damage(d.data.get('damage', 0)))

    def update(self, **kwargs):
        defenders_group = kwargs.get('defenders_group')

        self.animate()
        self._layer = self.rect.bottom
        if self.health <= 0: self.kill(); return

        if self.is_slowed and pygame.time.get_ticks() > self.slow_timer:
            self.speed = self.original_speed
            self.is_slowed = False

        self.is_attacking = (self.state == 'GRABBING')

        if self.state == 'SEEKING':
            if defenders_group:
                self.target_defender = self.find_strongest_defender(defenders_group)

            if self.target_defender:
                self.state = 'CHASING'
            else:
                self.float_pos.x -= self.speed
                self.rect.centerx = int(self.float_pos.x)

        elif self.state == 'CHASING':
            if not self.target_defender or not self.target_defender.alive():
                self.state = 'SEEKING'
                return
            direction = pygame.math.Vector2(self.target_defender.rect.center) - self.float_pos
            if direction.length() > 0:
                norm_dir = direction.normalize()
                self.float_pos += norm_dir * self.speed
                self.rect.center = (int(self.float_pos.x), int(self.float_pos.y))

            if self.rect.colliderect(self.target_defender.rect):
                self.victim = self.target_defender
                self.state = 'GRABBING'
                if self.victim:
                    self.victim.is_being_eaten = True
                    self.victim.attacker = self

        elif self.state == 'GRABBING':
            if self.victim:
                self.victim.rect.midright = self.rect.midright
            self.state = 'ESCAPING'

        elif self.state == 'ESCAPING':
            self.float_pos.x += self.speed * ADDICT_ESCAPE_SPEED_MULTIPLIER
            self.rect.centerx = int(self.float_pos.x)
            if self.victim:
                self.victim.rect.midright = self.rect.midright
            if self.rect.left > SCREEN_WIDTH:
                if self.victim:
                    self.victim.kill()
                self.kill()

    def kill(self):
        if hasattr(self, 'victim') and self.victim:
            self.victim.is_being_eaten = False
            self.victim.attacker = None

            if self.rect.right > 0:
                victim_center = self.victim.rect.center
                col = max(0, min(GRID_COLS - 1, int((victim_center[0] - GRID_START_X) / CELL_SIZE_W)))
                row = max(0, min(GRID_ROWS - 1, int((victim_center[1] - GRID_START_Y) / CELL_SIZE_H)))

                new_x = GRID_START_X + col * CELL_SIZE_W + CELL_SIZE_W / 2
                new_y = GRID_START_Y + row * CELL_SIZE_H + CELL_SIZE_H / 2

                self.victim.rect.center = (new_x, new_y)
                self.victim._layer = self.victim.rect.bottom
        super().kill()


class Thief(Enemy):
    def __init__(self, row, groups, enemy_type, sound_manager):
        super().__init__(row, groups, enemy_type, sound_manager)
        self.state = 'PLANNING'
        self.machine_targets = []
        self.current_target_machine = None
        self.stealing_damage = self.damage
        self.damage = ENEMIES_DATA['alarm_clock']['damage']

    def update(self, **kwargs):
        defenders_group = kwargs.get('defenders_group')

        self.animate()
        self._layer = self.rect.bottom
        if self.health <= 0:
            self.kill()
            return

        if self.is_slowed and pygame.time.get_ticks() > self.slow_timer:
            self.speed = self.original_speed
            self.is_slowed = False

        if self.current_target_machine and not self.current_target_machine.alive():
            self.current_target_machine = None
            self.state = 'SEEKING'

        if self.state == 'PLANNING':
            if defenders_group:
                self.machine_targets = [d for d in defenders_group if isinstance(d, CoffeeMachine) and d.alive()]

            if self.machine_targets:
                self.machine_targets.sort(key=lambda m: self.float_pos.distance_to(m.rect.center))
                self.state = 'SEEKING'
            else:
                self.state = 'BASIC_ATTACK_MODE'

        elif self.state == 'SEEKING':
            if self.machine_targets:
                self.current_target_machine = self.machine_targets.pop(0)
                self.state = 'CHASING'
            else:
                self.state = 'ESCAPING'

        elif self.state == 'CHASING':
            if self.current_target_machine and self.current_target_machine.alive():
                direction = pygame.math.Vector2(self.current_target_machine.rect.center) - self.float_pos
                if direction.length() < THIEF_STEAL_DISTANCE_THRESHOLD:
                    self.state = 'STEALING'
                else:
                    norm_dir = direction.normalize()
                    self.float_pos += norm_dir * self.speed
                    self.rect.center = (int(self.float_pos.x), int(self.float_pos.y))
            else:
                self.state = 'SEEKING'

        elif self.state == 'STEALING':
            self.is_attacking = True
            if self.current_target_machine and self.current_target_machine.alive():
                self.sound_manager.play_sfx('thief_laugh')
                self.current_target_machine.kill()
                self.current_target_machine = None
            self.is_attacking = False
            self.state = 'SEEKING'

        elif self.state == 'ESCAPING':
            self.float_pos.x += self.speed * THIEF_ESCAPE_SPEED_MULTIPLIER
            self.rect.centerx = int(self.float_pos.x)
            if self.rect.left > SCREEN_WIDTH:
                self.kill()

        elif self.state == 'BASIC_ATTACK_MODE':
            super().update(**kwargs)

    def kill(self):
        if self.current_target_machine and self.current_target_machine.alive():
            self.current_target_machine = None
        super().kill()