import pygame
import pygame.image

from constants.global_func import *
from constants.global_var import *
from constants.global_imports import *

class Bala:
    imagem_jogador = pygame.image.load('assets/Bullet.png').convert()
    imagem_jogador.set_colorkey((0, 0, 0))
    imagem_jogador = pygame.transform.scale(imagem_jogador, (SPRITE_SIZE, SPRITE_SIZE))

    imagem_inimigo = pygame.image.load('assets/enemy_bullet.png').convert()
    imagem_inimigo.set_colorkey((0, 0, 0))
    imagem_inimigo = pygame.transform.scale(imagem_inimigo, (SPRITE_SIZE, SPRITE_SIZE))

    tiros_jogador = []   # lista de projéteis do jogador
    tiros_inimigos = []  # lista de projéteis dos inimigos

    velocidade_jogador = 12
    velocidade_inimigo = 4

    def __init__(self, x, y, direcao, origem_do_jogador=True):
        if direcao not in (1, 2, 3, 4):
            return  # direção inválida, não cria a bala

        retangulo = pygame.Rect(x, y, SPRITE_SIZE, SPRITE_SIZE)
        dados_tiro = [x, y, direcao, origem_do_jogador, retangulo]

        if origem_do_jogador:
            Bala.tiros_jogador.append(dados_tiro)
        else:
            Bala.tiros_inimigos.append(dados_tiro)

    def mover_tiro(self, dados, delta_tempo, superficie):
        x, y, direcao, origem_do_jogador, ret = dados
        velocidade = self.velocidade_jogador if origem_do_jogador else self.velocidade_inimigo

        if direcao == 1:
            y -= round(velocidade * delta_tempo)
        elif direcao == 2:
            x -= round(velocidade * delta_tempo)
        elif direcao == 3:
            y += round(velocidade * delta_tempo)
        elif direcao == 4:
            x += round(velocidade * delta_tempo)

        ret.topleft = (x, y)
        dados[0], dados[1] = x, y  # atualiza a posição no vetor

        if x > config.window_size[0] or x < -SPRITE_SIZE or y > config.window_size[1] or y < -SPRITE_SIZE:
            if origem_do_jogador:
                Bala.tiros_jogador.remove(dados)
            else:
                Bala.tiros_inimigos.remove(dados)
            return

        self.desenhar(superficie, ret, origem_do_jogador)

    def atualizar(self, delta_tempo, superficie):
        for tiro in Bala.tiros_jogador[:]:
            self.mover_tiro(tiro, delta_tempo, superficie)
        for tiro in Bala.tiros_inimigos[:]:
            self.mover_tiro(tiro, delta_tempo, superficie)

    def desenhar(self, superficie, ret, origem_do_jogador):
        if origem_do_jogador:
            superficie.blit(self.imagem_jogador, ret)
        else:
            superficie.blit(self.imagem_inimigo, ret)
