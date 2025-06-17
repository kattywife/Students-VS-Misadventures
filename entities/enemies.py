# entities/enemies.py

import pygame
import random
from data.settings import *
from data.assets import load_image, SOUNDS
from entities.base_sprite import BaseSprite
from entities.projectiles import Integral
from entities.defenders import CoffeeMachine


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
        self.original_image = load_image(f'{enemy_type}.png', DEFAULT_COLORS[enemy_type],
                                         (CELL_SIZE_W - 20, CELL_SIZE_H - 10))
        self.image = self.original_image.copy()
        y = GRID_START_Y + row * CELL_SIZE_H + CELL_SIZE_H / 2
        self.rect = self.image.get_rect(midleft=(SCREEN_WIDTH - 1, y))
        self._layer = self.rect.bottom
        self.attack_cooldown = self.data['cooldown'] * 1000 if self.data['cooldown'] else 1000

        self.is_attacking = False
        self.is_hit = False
        self.hit_timer = 0
        self.hit_duration = 100
        self.last_attack_time = 0
        self.eating_channel = None
        self.current_target = None
        self.slow_timer = 0
        self.is_slowed = False
        self.active_calamity_color = None

    def get_hit(self, damage):
        self.health -= damage
        self.is_hit = True
        self.hit_timer = pygame.time.get_ticks()
        if SOUNDS.get('damage'): SOUNDS['damage'].play()

    def apply_calamity_effect(self, calamity_type):
        if calamity_type == 'colloquium':
            self.damage_multiplier *= 1.5
        elif calamity_type == 'internet_down':
            ratio = self.health / self.max_health if self.max_health > 0 else 1
            self.max_health *= 2
            self.health = self.max_health * ratio
        self.active_calamity_color = DEFAULT_COLORS.get(calamity_type)

    def revert_calamity_effect(self, calamity_type):
        if calamity_type == 'colloquium':
            self.damage_multiplier /= 1.5
        elif calamity_type == 'internet_down':
            ratio = self.health / self.max_health if self.max_health > 0 else 1
            self.max_health /= 2
            self.health = max(1, self.max_health * ratio)
        self.active_calamity_color = None

    def draw(self, surface):
        surface.blit(self.image, self.rect)
        if self.active_calamity_color:
            pygame.draw.rect(surface, self.active_calamity_color, self.rect, 4, border_radius=5)

    def manage_hit_flash(self):
        if self.is_hit:
            if pygame.time.get_ticks() - self.hit_timer > self.hit_duration:
                self.is_hit = False
                self.image = self.original_image
            else:
                flash_image = self.original_image.copy()
                flash_image.fill((255, 255, 255, 128), special_flags=pygame.BLEND_RGBA_ADD)
                self.image = flash_image
        else:
            self.image = self.original_image

    def update(self, defenders_group, *args, **kwargs):
        self.manage_hit_flash()
        if self.health <= 0:
            self.kill()
            return
        if self.is_slowed and pygame.time.get_ticks() > self.slow_timer:
            self.speed = self.original_speed
            self.is_slowed = False

        target_found = self.find_and_attack_target(defenders_group)
        if not target_found:
            if self.is_attacking:
                self.is_attacking = False
                self.stop_eating_sound()
                if self.current_target:
                    self.current_target.is_being_eaten = False
                    self.current_target = None
            self.rect.x -= self.speed

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
        self.is_shooting = False

    def update(self, defenders_group, all_sprites, projectiles, *args, **kwargs):
        self.is_shooting = any(d.rect.centery == self.rect.centery for d in defenders_group)
        super().update(defenders_group, *args, **kwargs)

        if self.alive() and self.is_shooting:
            now = pygame.time.get_ticks()
            if now - self.last_shot > self.attack_cooldown:
                self.last_shot = now
                damage = self.damage * self.damage_multiplier
                Integral(self.rect.left, self.rect.centery, (all_sprites, projectiles), damage)

    def find_and_attack_target(self, defenders_group):
        return self.is_shooting


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
    def __init__(self, row, groups):
        super().__init__(row, groups, 'addict')
        self.state = 'SEEKING'
        self.target_defender = None
        self.victim = None

    def find_strongest_defender(self, defenders_group):
        living_defenders = [d for d in defenders_group if d.alive() and not isinstance(d, CoffeeMachine)]
        if not living_defenders:
            return None
        return max(living_defenders, key=lambda d: d.get_final_damage(d.data.get('damage', 0)))

    def update(self, defenders_group, *args, **kwargs):
        self.manage_hit_flash()
        if self.health <= 0:
            self.kill()
            return

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
            if self.rect.centery < self.target_defender.rect.centery - 5:
                self.rect.y += self.speed
            elif self.rect.centery > self.target_defender.rect.centery + 5:
                self.rect.y -= self.speed
            self.rect.x -= self.speed

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
        if self.victim:
            self.victim.is_being_eaten = False
        super().kill()


class Thief(Addict):
    def __init__(self, row, groups):
        super().__init__(row, groups)
        self.enemy_type = 'thief'
        self.data = ENEMIES_DATA[self.enemy_type]

    def find_and_attack_target(self, defenders_group):
        coffee_machines = [d for d in defenders_group if isinstance(d, CoffeeMachine) and d.alive()]
        if not coffee_machines:
            return Enemy.find_and_attack_target(self, defenders_group)

        closest_machine = min(coffee_machines, key=lambda m: abs(m.rect.centery - self.rect.centery) * 100 + abs(
            m.rect.centerx - self.rect.centerx))

        if self.rect.colliderect(closest_machine):
            return Enemy.find_and_attack_target(self, [closest_machine])
        else:
            if self.rect.centery < closest_machine.rect.centery:
                self.rect.y += self.speed / 2
            else:
                self.rect.y -= self.speed / 2

            if self.rect.centerx > closest_machine.rect.centerx:
                self.rect.x -= self.speed
            else:
                self.rect.x += self.speed
        return False