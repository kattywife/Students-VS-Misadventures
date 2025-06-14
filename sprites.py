# sprites.py

import pygame
import random
from settings import *
from assets import load_image, SOUNDS


class BaseSprite(pygame.sprite.Sprite):
    def __init__(self, *groups):
        super().__init__(*groups)
        self.last_update = pygame.time.get_ticks()

    def draw(self, surface):
        surface.blit(self.image, self.rect)


class Defender(BaseSprite):
    def __init__(self, x, y, groups, data):
        super().__init__(groups)
        self.data = data
        self.max_health = self.data['health']
        self.health = self.max_health
        self.cost = self.data['cost']
        self.original_image = load_image(f"{self.data['type']}.png", DEFAULT_COLORS[self.data['type']],
                                         (CELL_SIZE_W - 10, CELL_SIZE_H - 10))
        self.image = self.original_image.copy()
        self.rect = self.image.get_rect(center=(x, y))
        self.is_animate = self.data['type'] != 'coffee_machine'

        self.is_being_eaten = False
        self.scream_channel = None
        self.is_upgraded = False
        self.buff_multiplier = 1.0
        self.debuff_multiplier = 1.0
        self.calamity_damage_multiplier = 1.0

    def get_final_damage(self, base_damage):
        return base_damage * self.buff_multiplier * self.debuff_multiplier * self.calamity_damage_multiplier

    def apply_calamity_effect(self, calamity_type):
        if calamity_type == 'epidemic':
            self.calamity_damage_multiplier /= 2
            self.health /= 2

    def revert_calamity_effect(self, calamity_type):
        if calamity_type == 'epidemic':
            self.calamity_damage_multiplier *= 2

    def update(self, *args, **kwargs):
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
        has_enemy_in_row = any(enemy.rect.centery == self.rect.centery for enemy in self.enemies_group)
        if self.alive() and has_enemy_in_row and now - self.last_shot > self.attack_cooldown:
            self.last_shot = now
            damage = self.get_final_damage(self.data['damage'])
            Bracket(self.rect.right, self.rect.centery, (self.all_sprites, self.projectile_group), damage)


class BotanistGirl(Defender):
    def __init__(self, x, y, groups, data, all_sprites, enemies_group):
        super().__init__(x, y, groups, data)
        self.all_sprites = all_sprites
        self.enemies_group = enemies_group
        self.attack_cooldown = self.data['cooldown'] * 1000
        self.last_attack = pygame.time.get_ticks()
        self.attack_radius = self.data['radius']

    def update(self, *args, **kwargs):
        super().update(*args, **kwargs)
        now = pygame.time.get_ticks()
        if self.alive() and now - self.last_attack > self.attack_cooldown:
            target = self.find_strongest_enemy_in_range()
            if target:
                self.last_attack = now
                self.attack(target)

    def find_strongest_enemy_in_range(self):
        enemies_in_range = [e for e in self.enemies_group if
                            pygame.math.Vector2(self.rect.center).distance_to(e.rect.center) < self.attack_radius]
        if not enemies_in_range: return None
        return max(enemies_in_range, key=lambda e: e.health)

    def attack(self, target):
        damage = self.get_final_damage(self.data['damage'])
        BookAttackEffect(target.rect.center, self.all_sprites, 100)
        target.get_hit(damage)


class CoffeeMachine(Defender):
    def __init__(self, x, y, groups, data, all_sprites, coffee_bean_group):
        super().__init__(x, y, groups, data)
        self.all_sprites = all_sprites
        self.coffee_bean_group = coffee_bean_group
        self.production_cooldown = self.data['cooldown'] * 1000
        self.last_production = pygame.time.get_ticks()

    def update(self, *args, **kwargs):
        super().update(*args, **kwargs)
        now = pygame.time.get_ticks()
        if self.alive() and now - self.last_production > self.production_cooldown:
            self.last_production = now
            CoffeeBean(self.rect.centerx, self.rect.top, (self.all_sprites, self.coffee_bean_group),
                       self.data['production'])


class Activist(Defender):
    def __init__(self, x, y, groups, data):
        super().__init__(x, y, groups, data)


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
            has_enemy_in_row = any(e.rect.centery == self.rect.centery for e in self.enemies_group)
            if has_enemy_in_row:
                self.last_attack = now
                damage = self.get_final_damage(self.data['damage'])
                SoundWave(self.rect.center, (self.all_sprites,), damage, self.rect.centery)


class Medic(Defender):
    def __init__(self, x, y, groups, data, defenders_group):
        super().__init__(x, y, groups, data)
        self.defenders_group = defenders_group
        self.heal_amount = self.data['heal_amount']
        self.healed = False

    def update(self, *args, **kwargs):
        super().update(*args, **kwargs)
        if not self.healed:
            self.heal()
            self.healed = True
            self.kill()

    def heal(self):
        most_wounded = None
        min_health_ratio = 1.0
        for d in self.defenders_group:
            if d.health < d.max_health:
                ratio = d.health / d.max_health
                if ratio < min_health_ratio:
                    min_health_ratio = ratio
                    most_wounded = d
        if most_wounded:
            most_wounded.health = min(most_wounded.max_health, most_wounded.health + self.heal_amount)


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


class Bracket(BaseSprite):
    def __init__(self, x, y, groups, damage):
        super().__init__(groups)
        self.damage = damage
        self.image = load_image('bracket.png', DEFAULT_COLORS['bracket'], (30, 30))
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = 10

    def update(self, *args, **kwargs):
        self.rect.x += self.speed
        if self.rect.left > SCREEN_WIDTH:
            self.kill()


class PaintSplat(Bracket):
    def __init__(self, x, y, groups, damage, artist):
        super().__init__(x, y, groups, damage)
        self.artist = artist
        self.image = load_image('paint_splat.png', DEFAULT_COLORS['paint_splat'], (30, 30))


class BookAttackEffect(BaseSprite):
    def __init__(self, center_pos, groups, diameter):
        super().__init__(groups)
        self.image = load_image('book_attack.png', DEFAULT_COLORS['book_attack'], (diameter, diameter))
        self.image.set_alpha(150)
        self.rect = self.image.get_rect(center=center_pos)
        self.spawn_time = pygame.time.get_ticks()
        self.lifetime = 200

    def update(self, *args, **kwargs):
        if pygame.time.get_ticks() - self.spawn_time > self.lifetime:
            self.kill()


class SoundWave(BaseSprite):
    def __init__(self, center, groups, damage, row_y):
        super().__init__(groups)
        self.damage = damage
        self.image = pygame.Surface((20, CELL_SIZE_H - 10), pygame.SRCALPHA)
        self.image.fill(DEFAULT_COLORS['sound_wave'])
        self.rect = self.image.get_rect(center=center)
        self.row_y = row_y
        self.speed = 5
        self.hit_enemies = set()
        self.spawn_time = pygame.time.get_ticks()
        self.lifetime = 2000

    def update(self, *args, **kwargs):
        self.rect.x += self.speed
        if pygame.time.get_ticks() - self.spawn_time > self.lifetime or self.rect.left > SCREEN_WIDTH:
            self.kill()


class Integral(Bracket):
    def __init__(self, x, y, groups, damage):
        super().__init__(x, y, groups, damage)
        self.image = load_image('integral.png', DEFAULT_COLORS['integral'], (30, 30))
        self.speed = -5


class CoffeeBean(BaseSprite):
    def __init__(self, x, y, groups, value):
        super().__init__(groups)
        self.value = value
        self.image = load_image('coffee_bean.png', DEFAULT_COLORS['coffee_bean'], (40, 40))
        self.rect = self.image.get_rect(center=(x, y))
        self.spawn_time = pygame.time.get_ticks()
        self.lifetime = 8000

    def update(self, *args, **kwargs):
        if pygame.time.get_ticks() - self.spawn_time > self.lifetime:
            self.kill()


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
        self.rect = self.image.get_rect(midleft=(SCREEN_WIDTH + random.randint(0, 100), y))
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
        self.find_and_attack_target(defenders_group)
        # Для Calculus вызываем super().update() только если он не стреляет
        if not self.is_shooting:
            super().update(defenders_group, *args, **kwargs)

        if self.alive() and self.is_shooting:
            now = pygame.time.get_ticks()
            if now - self.last_shot > self.attack_cooldown:
                self.last_shot = now
                damage = self.damage * self.damage_multiplier
                Integral(self.rect.left, self.rect.centery, (all_sprites, projectiles), damage)

    def find_and_attack_target(self, defenders_group):
        self.is_shooting = any(
            d.rect.centery == self.rect.centery and d.rect.left > self.rect.right for d in defenders_group)
        if self.is_shooting:
            return True
        return False


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
                if defender.alive() and pygame.sprite.collide_rect(self,
                                                                   defender) and defender.rect.centery == self.rect.centery:
                    if defender.rect.left - self.rect.right < 50:
                        self.rect.x = defender.rect.left - self.rect.width - 5
                        self.has_jumped = True
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
        return max(living_defenders, key=lambda d: d.max_health)

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

    def find_and_attack_target(self, defenders_group):
        coffee_machines = [d for d in defenders_group if isinstance(d, CoffeeMachine)]
        if not coffee_machines:
            return super(Thief, self).find_and_attack_target(defenders_group)

        closest_machine = min(coffee_machines, key=lambda m: abs(m.rect.centery - self.rect.centery) * 100 + abs(
            m.rect.centerx - self.rect.centerx))

        if abs(self.rect.centery - closest_machine.rect.centery) < 10:
            return super(Thief, self).find_and_attack_target([closest_machine])
        else:
            if self.rect.centery < closest_machine.rect.centery:
                self.rect.y += self.speed / 2
            else:
                self.rect.y -= self.speed / 2
        return False


class NeuroMower(BaseSprite):
    def __init__(self, row, groups, mower_type):
        super().__init__(groups)
        self.mower_type = mower_type
        self.data = NEURO_MOWERS_DATA[mower_type]
        self.image = load_image(f'{mower_type}.png', DEFAULT_COLORS[mower_type], (CELL_SIZE_W - 20, CELL_SIZE_H - 20))
        y = GRID_START_Y + row * CELL_SIZE_H + CELL_SIZE_H / 2
        self.rect = self.image.get_rect(center=(GRID_START_X - CELL_SIZE_W / 2, y))
        self.is_active = False
        self.speed = 12

    def activate(self, enemies_group):
        if self.is_active: return
        self.is_active = True

        if self.mower_type == 'deepseek':
            for enemy in sorted(list(enemies_group), key=lambda e: e.rect.left)[:3]:
                enemy.kill()
        elif self.mower_type == 'gemini':
            for enemy in sorted(list(enemies_group), key=lambda e: e.health, reverse=True)[:4]:
                enemy.kill()

    def update(self, *args, **kwargs):
        if self.is_active and self.mower_type == 'chat_gpt':
            self.rect.x += self.speed
            if self.rect.left > SCREEN_WIDTH:
                self.kill()

            enemies_on_line = kwargs.get('enemies_group')
            if enemies_on_line:
                pygame.sprite.spritecollide(self, enemies_on_line, True)

        elif self.is_active and self.mower_type != 'chat_gpt':
            self.kill()