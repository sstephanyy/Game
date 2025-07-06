import pygame
import pygame.image

from constants.global_func import *
from constants.global_var import *
from constants.global_imports import *

class Bullet:
    image = pygame.image.load('assets/Bullet.png').convert()
    image.set_colorkey((0, 0, 0))
    image = pygame.transform.scale(image, (SPRITE_SIZE, SPRITE_SIZE))

    enemyimage = pygame.image.load('assets/enemy_bullet.png').convert()
    enemyimage.set_colorkey((0, 0, 0))
    enemyimage = pygame.transform.scale(enemyimage, (SPRITE_SIZE, SPRITE_SIZE))

    locs = []        # balas do jogador
    enemylocs = []   # balas dos inimigos
    speed = 12
    enemyspeed = 4

    def __init__(self, x, y, direction, isFromPlayer=True):
        if direction not in (1, 2, 3, 4):
            return  # direção inválida, não cria a bala

        rect = pygame.Rect(x, y, SPRITE_SIZE, SPRITE_SIZE)
        data = [x, y, direction, isFromPlayer, rect]
        
        if isFromPlayer:
            Bullet.locs.append(data)
        else:
            Bullet.enemylocs.append(data)

    def moveBullets(self, loc, dt, surf):
        x, y, direction, isFromPlayer, rect = loc
        speed = self.speed if isFromPlayer else self.enemyspeed

        # Movimento
        if   direction == 1: y -= round(speed * dt)
        elif direction == 2: x -= round(speed * dt)
        elif direction == 3: y += round(speed * dt)
        elif direction == 4: x += round(speed * dt)

        rect.topleft = (x, y)
        loc[0], loc[1] = x, y  # atualiza loc

        # Fora da tela
        if x > config.window_size[0] or x < -SPRITE_SIZE or y > config.window_size[1] or y < -SPRITE_SIZE:
            if isFromPlayer:
                Bullet.locs.remove(loc)
            else:
                Bullet.enemylocs.remove(loc)
            return

        self.draw(surf, rect, isFromPlayer)

    def update(self, dt, surf):
        for loc in Bullet.locs[:]: 
            self.moveBullets(loc, dt, surf)
        for loc in Bullet.enemylocs[:]:
            self.moveBullets(loc, dt, surf)

    def draw(self, surf, rect, isFromPlayer):
        if isFromPlayer:
            surf.blit(self.image, rect)
        else:
            surf.blit(self.enemyimage, rect)
