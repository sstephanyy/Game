import pygame
from random import choice, randint
from time import time
import pygame.image
import math

from classes.Bullet import Bullet
from classes.Player import Player
from constants.global_func import *
from constants.global_var import *
from constants.global_imports import *


class EnemyBase:
    def __init__(self, pos, sprites, instancelist_ref):
        self.x, self.y = pos
        self.sprites = sprites
        self.instancelist = instancelist_ref
        self.instancelist.append(self)

        self.current_sprite = 0
        self.image = self.sprites[self.current_sprite]
        self.rect = self.image.get_rect(topleft=(self.x, self.y))

        self.direction = choice([True, False])
        self.y_direction = False
        self.explosion = Explosion()

        self.last_time = time()
        self.last_damage = self.last_time
        self.last_hit_player = 0

        self.frame_timer = 0
        self.frame_delay = 0.1

        self.life = 3
        self.speed = config.window_size[1] * 0.005

    def animate(self, dt):
        self.frame_timer += dt
        if self.frame_timer >= self.frame_delay:
            self.current_sprite = (self.current_sprite + 1) % len(self.sprites)
            self.image = self.sprites[self.current_sprite]
            self.frame_timer = 0

    def kill(self):
        try:
            self.instancelist.remove(self)
        except:
            pass

    def damage(self):
        if self.life <= 1:
            self.kill()
        else:
            self.life -= 1

    def death(self):
        for bloc in Bullet.locs:
            _, _, _, _, rect = bloc
            if self.rect.colliderect(rect):
                self.explosion.create(self.rect.centerx, self.rect.centery - SPRITE_SIZE)
                pygame.mixer.Sound.play(pygame.mixer.Sound('assets/hit.mp3'))
                self.damage()
                Bullet.locs.remove(bloc)
                break  # importante: evita `RuntimeError` por alterar a lista no loop

    def damage_player(self, player):
        now = time()
        enemy_hitbox = self.rect.inflate(-self.rect.width * 0.3, -self.rect.height * 0.3)
        player_hitbox = player.rect.inflate(-player.rect.width * 0.3, -player.rect.height * 0.3)
        if enemy_hitbox.colliderect(player_hitbox) and (now - self.last_hit_player > 1):
            player.setLife(player.getLife() - 1)
            self.last_hit_player = now

    def shoot(self, weight):
        for _ in range(weight):
            if randint(0, 1000) < 2:
                Bullet(self.rect.centerx, self.rect.centery, 3, False)

    def move_logic(self, dt, player, weight):
        if self.y > (config.window_size[1] - (SCALED_SPRITE_SIZE + 10)):
            player.setLife(player.getLife() - 1)

        if randint(0, 500 * weight) < 1:
            self.y_direction = True
            self.old_y = self.y

        if self.y_direction:
            if self.y < self.old_y + SCALED_SPRITE_SIZE:
                self.y += self.speed * dt
            else:
                self.y_direction = False
        else:
            if self.direction:
                self.x += self.speed * dt
                if self.x > config.window_size[0] - (config.window_size[0] * (weight * 0.1)):
                    self.direction = False
            else:
                self.x -= self.speed * dt
                if self.x < (config.window_size[0] * (weight * 0.1)):
                    self.direction = True

    def update(self, dt, last_time, surf, player, weight):
        self.last_time = last_time
        self.death()
        self.move(dt, player)
        self.damage_player(player)
        self.shoot(weight)

        self.explosion.update(dt)
        self.explosion.draw(surf)

        self.rect.topleft = (self.x, self.y)

        if (self.x > config.window_size[0] + 100 or self.x < -100 or self.y > config.window_size[1] or self.y < -100) and ((self.last_time - self.last_damage) > 1):
            self.last_damage = self.last_time
            self.damage()

        self.animate(dt)
        self.draw(surf)

    def draw(self, surf):
        surf.blit(self.image, self.rect)

    @staticmethod
    def spawn_enemy(n, enemy_class):
        margin = SCALED_SPRITE_SIZE // 2
        for _ in range(n):
            x = randint(margin, config.window_size[0] - margin)
            y = config.window_size[1] / 2 - 320
            enemy_class((x, y))


class Enemy1(EnemyBase):
    instancelist = []
    sprites_cache = None

    def __init__(self, pos):
        if not Enemy1.sprites_cache:
            Enemy1.sprites_cache = self.load_sprites(['assets/enemy_idle1.png', 'assets/enemy_idle2.png'])
        super().__init__(pos, Enemy1.sprites_cache, Enemy1.instancelist)
        self.life = 1

    def load_sprites(self, files):
        return [self.prepare_sprite(file) for file in files]

    def prepare_sprite(self, file):
        sprite = pygame.image.load(file).convert()
        sprite = pygame.transform.flip(sprite, False, True)
        sprite = pygame.transform.scale(sprite, (sprite.get_width() * SCALE, sprite.get_height() * SCALE))
        sprite.set_colorkey((0, 0, 0))
        return sprite

    def move(self, dt, player):
        self.move_logic(dt, player, weight=1)

    def update(self, dt, last_time, surf, player):
        super().update(dt, last_time, surf, player, 1)


class Enemy2(EnemyBase):
    instancelist = []
    sprites_cache = None

    def __init__(self, pos):
        if not Enemy2.sprites_cache:
            Enemy2.sprites_cache = self.load_sprites(['assets/enemy_medium1.png', 'assets/enemy_medium2.png'])
        super().__init__(pos, Enemy2.sprites_cache, Enemy2.instancelist)
        self.life = 3
        self.speed *= 0.75
        self.x_direction = 1

    def load_sprites(self, files):
        return [self.prepare_sprite(file) for file in files]

    def prepare_sprite(self, file):
        sprite = pygame.image.load(file).convert()
        sprite = pygame.transform.flip(sprite, False, True)
        sprite = pygame.transform.scale(sprite, (sprite.get_width() * SCALE, sprite.get_height() * SCALE))
        sprite.set_colorkey((0, 0, 0))
        return sprite

    def move(self, dt, player):
        time_elapsed = pygame.time.get_ticks() / 1000.0
        freq = 0.5
        self.x += self.speed * dt * math.sin(2 * math.pi * freq * time_elapsed) * self.x_direction
        self.y += self.speed * dt * math.sin(2 * math.pi * freq * time_elapsed)

    def update(self, dt, last_time, surf, player):
        super().update(dt, last_time, surf, player, 2)


class Enemy3(EnemyBase):
    instancelist = []
    sprites_cache = None

    def __init__(self, pos):
        if not Enemy3.sprites_cache:
            Enemy3.sprites_cache = self.load_sprites(['assets/enemy_big1.png', 'assets/enemy_big2.png'])
        super().__init__(pos, Enemy3.sprites_cache, Enemy3.instancelist)
        self.life = 5
        self.speed *= 0.5
        self.xy_direction = choice([-1, 1])

    def load_sprites(self, files):
        return [self.prepare_sprite(file) for file in files]

    def prepare_sprite(self, file):
        sprite = pygame.image.load(file).convert()
        sprite = pygame.transform.flip(sprite, False, True)
        sprite = pygame.transform.scale(sprite, (sprite.get_width() * SCALE, sprite.get_height() * SCALE))
        sprite.set_colorkey((0, 0, 0))
        return sprite

    def move(self, dt, player):
        time_elapsed = pygame.time.get_ticks() / 1000.0
        freq = 0.5
        self.x += self.speed * dt * math.sin(2 * math.pi * freq * time_elapsed) * self.xy_direction
        self.y += self.speed * dt * math.cos(2 * math.pi * freq * time_elapsed) * self.xy_direction

    def update(self, dt, last_time, surf, player):
        super().update(dt, last_time, surf, player, 3)