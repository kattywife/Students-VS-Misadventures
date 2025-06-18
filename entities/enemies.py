# entities/enemies.py

import pygame
import random
import os
from data.settings import *
from data.assets import load_image, SOUNDS, PROJECTILE_IMAGES
from data.settings import CALCULUS_PROJECTILE_TYPES
from entities.base_sprite import BaseSprite
from entities.projectiles import Integral
from entities.defenders import CoffeeMachine
from entities.other_sprites import CalamityAuraEffect


class Enemy(BaseSprite):
    def __init__(self, row, groups, enemy_type):
        super().__init__(groups)
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
        self._layer = self.rect.bottom

        self.anim_speed = self.data.get('animation_data', {}).get('speed', 0.2)
        self.last_anim_update = pygame.time.get_ticks()

        self.attack_cooldown = self.data['cooldown'] * 1000 if self.data['cooldown'] else 1000
        self.last_attack_time = 0

        self.eating_channel = None
        self.current_target = None
        self.slow_timer = 0
        self.is_slowed = False
        self.is_attacking = False

    def load_animations(self):
        anim_data = self.data.get('animation_data')
        if not anim_data: return

        size = self.data.get('battle_size', (CELL_SIZE_W - 20, CELL_SIZE_H - 10))

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
            self.frame_index += 1
            if self.frame_index >= len(anim_sequence):
                if self.current_animation in ['hit', 'attack']:
                    self.set_animation('walk')
                self.frame_index = 0

        self.image = self.animations[self.current_animation][self.frame_index]

    def get_hit(self, damage):
        self.health -= damage
        if SOUNDS.get('damage'): SOUNDS['damage'].play()
        if 'hit' in self.animations and self.animations['hit']:
            self.set_animation('hit')

    def apply_calamity_effect(self, calamity_type):
        if calamity_type == 'colloquium':
            self.damage_multiplier *= 1.5
        elif calamity_type == 'internet_down':
            ratio = self.health / self.max_health if self.max_health > 0 else 1
            self.max_health *= 2
            self.health = self.max_health * ratio

        if calamity_type != 'big_party' and not self.aura_effect:
            self.aura_effect = CalamityAuraEffect((self.all_sprites_group,), self, calamity_type)

    def revert_calamity_effect(self, calamity_type):
        if calamity_type == 'colloquium':
            self.damage_multiplier /= 1.5
        elif calamity_type == 'internet_down':
            ratio = self.health / self.max_health if self.max_health > 0 else 1
            self.max_health /= 2
            self.health = max(1, self.max_health * ratio)

        if self.aura_effect:
            self.aura_effect.kill()
            self.aura_effect = None

    def update_movement(self, target_found):
        if not target_found:
            self.rect.x -= self.speed

    def update(self, defenders_group, *args, **kwargs):
        self.animate()
        self._layer = self.rect.bottom

        if self.health <= 0:
            self.kill()
            return

        if self.is_slowed and pygame.time.get_ticks() > self.slow_timer:
            self.speed = self.original_speed
            self.is_slowed = False

        target_found = self.find_and_attack_target(defenders_group)
        if not target_found:
            self.is_attacking = False
            self.stop_eating_sound()
            if self.current_target:
                self.current_target.is_being_eaten = False
                self.current_target = None

        self.update_movement(target_found)

    def find_and_attack_target(self, defenders_group):
        collided_defenders = [d for d in defenders_group if
                              self.rect.colliderect(d.rect) and d.rect.centery == self.rect.centery]
        if not collided_defenders:
            return False

        target = collided_defenders[0]
        self.is_attacking = True
        if self.current_target != target:
            if self.current_target:
                self.current_target.is_being_eaten = False
            self.current_target = target
        self.current_target.is_being_eaten = True

        now = pygame.time.get_ticks()
        if now - self.last_attack_time > self.attack_cooldown:
            self.play_eating_sound()
            self.last_attack_time = now
            target.health -= self.damage * self.damage_multiplier
        return True

    def kill(self):
        if self.alive():
            if self.aura_effect:
                self.aura_effect.kill()
                self.aura_effect = None

            if SOUNDS.get('enemy_dead'):
                SOUNDS['enemy_dead'].play()
            self.stop_eating_sound()
            if self.current_target:
                self.current_target.is_being_eaten = False
            super().kill()

    def play_eating_sound(self):
        eating_sound = SOUNDS.get('eating')
        if eating_sound and not (self.eating_channel and self.eating_channel.get_busy()):
            self.eating_channel = pygame.mixer.find_channel()
            if self.eating_channel:
                self.eating_channel.play(eating_sound)

    def stop_eating_sound(self):
        if self.eating_channel:
            self.eating_channel.stop()
            self.eating_channel = None

    def slow_down(self, factor, duration):
        if not self.is_slowed:
            self.speed *= factor
            self.is_slowed = True
        self.slow_timer = pygame.time.get_ticks() + duration


class Calculus(Enemy):
    def __init__(self, row, groups):
        super().__init__(row, groups, 'calculus')
        self.last_shot = pygame.time.get_ticks()

    def update(self, defenders_group, all_sprites, projectiles, *args, **kwargs):
        is_shooting = any(d.rect.centery == self.rect.centery for d in defenders_group)
        self.is_attacking = is_shooting

        self.animate()
        self._layer = self.rect.bottom
        if self.health <= 0: self.kill(); return

        if is_shooting:
            now = pygame.time.get_ticks()
            if now - self.last_shot > self.attack_cooldown:
                self.last_shot = now
                damage = self.damage * self.damage_multiplier
                random_projectile_type = random.choice(CALCULUS_PROJECTILE_TYPES)
                projectile_image = PROJECTILE_IMAGES[random_projectile_type]
                Integral(self.rect.left, self.rect.centery, (all_sprites, projectiles), damage, projectile_image)
        else:
            self.rect.x -= self.speed


class StuffyProf(Enemy):
    def __init__(self, row, groups):
        super().__init__(row, groups, 'professor')


class MathTeacher(Enemy):
    def __init__(self, row, groups):
        super().__init__(row, groups, 'math_teacher')
        self.has_jumped = False

    def update(self, defenders_group, *args, **kwargs):
        if not self.has_jumped:
            for defender in defenders_group:
                if defender.alive() and self.rect.colliderect(defender) and defender.rect.centery == self.rect.centery:
                    self.rect.x = defender.rect.left - self.rect.width - 5
                    self.has_jumped = True
                    self.speed /= 2
                    break
        super().update(defenders_group, *args, **kwargs)


class Addict(Enemy):
    def __init__(self, row, groups, enemy_type='addict'):
        super().__init__(row, groups, enemy_type)
        self.state = 'SEEKING'
        self.target_defender = None
        self.victim = None

    def find_strongest_defender(self, defenders_group):
        living_defenders = [d for d in defenders_group if d.alive() and not isinstance(d, CoffeeMachine)]
        if not living_defenders: return None
        return max(living_defenders, key=lambda d: d.get_final_damage(d.data.get('damage', 0)))

    def update(self, defenders_group, *args, **kwargs):
        self.animate()
        self._layer = self.rect.bottom
        if self.health <= 0: self.kill(); return

        self.is_attacking = (self.state == 'GRABBING')

        if self.state == 'SEEKING':
            self.target_defender = self.find_strongest_defender(defenders_group)
            if self.target_defender:
                self.state = 'CHASING'
            else:
                self.rect.x -= self.speed

        elif self.state == 'CHASING':
            if not self.target_defender or not self.target_defender.alive():
                self.state = 'SEEKING'
                return
            direction = pygame.math.Vector2(self.target_defender.rect.center) - pygame.math.Vector2(self.rect.center)
            if direction.length() > 0:
                norm_dir = direction.normalize()
                self.rect.x += norm_dir.x * self.speed
                self.rect.y += norm_dir.y * self.speed

            if self.rect.colliderect(self.target_defender.rect):
                self.victim = self.target_defender
                self.state = 'GRABBING'
                self.victim.is_being_eaten = True

        elif self.state == 'GRABBING':
            self.victim.rect.center = self.rect.center
            self.state = 'ESCAPING'

        elif self.state == 'ESCAPING':
            self.rect.x += self.speed * 2
            self.victim.rect.center = self.rect.center
            if self.rect.left > SCREEN_WIDTH:
                self.victim.kill()
                self.kill()

    def kill(self):
        if hasattr(self, 'victim') and self.victim:
            self.victim.is_being_eaten = False
        super().kill()


class Thief(Enemy):
    def __init__(self, row, groups):
        super().__init__(row, groups, 'thief')
        self.state = 'INITIALIZING'  # Состояния: INITIALIZING, SEEKING_MACHINE, CHASING_MACHINE, GRABBING_MACHINE, ESCAPING, BASIC_ATTACK_MODE, ESCAPING_EMPTY
        self.target_machine = None
        self.has_stolen = False
        self.stealing_damage = self.damage
        self.damage = ENEMIES_DATA['alarm_clock']['damage']

    def update(self, defenders_group, *args, **kwargs):
        self.animate()
        self._layer = self.rect.bottom
        if self.health <= 0:
            self.kill()
            return

        coffee_machines = [d for d in defenders_group if isinstance(d, CoffeeMachine) and d.alive()]

        if self.state == 'INITIALIZING':
            if coffee_machines:
                self.state = 'SEEKING_MACHINE'
            else:
                self.state = 'BASIC_ATTACK_MODE'

        elif self.state == 'SEEKING_MACHINE':
            self.is_attacking = False
            self.stop_eating_sound()

            if coffee_machines:
                self.target_machine = min(coffee_machines, key=lambda m: pygame.math.Vector2(self.rect.center).distance_to(m.rect.center))
                self.state = 'CHASING_MACHINE'
            else:
                if self.has_stolen:
                    self.state = 'ESCAPING_EMPTY'
                else:
                    self.state = 'BASIC_ATTACK_MODE'

        elif self.state == 'CHASING_MACHINE':
            if not self.target_machine or not self.target_machine.alive():
                self.state = 'SEEKING_MACHINE'
                return

            direction = pygame.math.Vector2(self.target_machine.rect.center) - pygame.math.Vector2(self.rect.center)
            if direction.length() < 10:
                self.state = 'GRABBING_MACHINE'
            else:
                norm_dir = direction.normalize()
                self.rect.x += norm_dir.x * self.speed
                self.rect.y += norm_dir.y * self.speed

        elif self.state == 'GRABBING_MACHINE':
            self.is_attacking = True
            self.current_target = self.target_machine
            self.play_eating_sound()
            self.current_target.is_being_eaten = True
            self.current_target.health -= self.stealing_damage
            self.has_stolen = True
            self.state = 'ESCAPING'

        elif self.state == 'ESCAPING':
            self.rect.x += self.speed * 2
            if self.current_target and self.current_target.alive():
                 self.current_target.rect.center = self.rect.center

            if self.rect.left > SCREEN_WIDTH:
                if self.current_target:
                    self.current_target.kill()
                self.current_target = None
                self.target_machine = None
                self.state = 'SEEKING_MACHINE'

        elif self.state == 'ESCAPING_EMPTY':
            self.rect.x += self.speed * 2
            if self.rect.left > SCREEN_WIDTH:
                self.kill()

        elif self.state == 'BASIC_ATTACK_MODE':
            super().update(defenders_group, *args, **kwargs)

    def kill(self):
        if self.current_target:
            self.current_target.is_being_eaten = False
        super().kill()