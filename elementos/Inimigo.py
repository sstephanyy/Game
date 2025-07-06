import pygame
from random import choice, randint
from time import time
import pygame.image
import math

from constants.global_func import *
from elementos.Bala import Bala
from elementos.Jogador import Player
from constants.global_func import *
from constants.global_var import *
from constants.global_imports import *


class InimigoBase:
    def __init__(self, posicao, sprites, referencia_lista):
        self.x, self.y = posicao
        self.sprites = sprites
        self.lista_instancias = referencia_lista
        self.lista_instancias.append(self)

        self.sprite_atual = 0
        self.imagem = self.sprites[self.sprite_atual]
        self.retangulo = self.imagem.get_rect(topleft=(self.x, self.y))

        self.direcao_horizontal = choice([True, False])
        self.descendo = False
        self.explosao = Explosion()

        self.ultimo_tempo = time()
        self.ultimo_dano = self.ultimo_tempo
        self.tempo_ultimo_impacto = 0

        self.tempo_frame = 0
        self.intervalo_frame = 0.1

        self.vida = 3
        self.velocidade = config.window_size[1] * 0.005

    def animar(self, dt):
        self.tempo_frame += dt
        if self.tempo_frame >= self.intervalo_frame:
            self.sprite_atual = (self.sprite_atual + 1) % len(self.sprites)
            self.imagem = self.sprites[self.sprite_atual]
            self.tempo_frame = 0

    def eliminar(self):
        try:
            self.lista_instancias.remove(self)
        except:
            pass

    def levar_dano(self):
        if self.vida <= 1:
            self.eliminar()
        else:
            self.vida -= 1

    def verificar_morte(self):
        for proj in Bala.tiros_jogador:
            _, _, _, _, rect = proj
            if self.retangulo.colliderect(rect):
                self.explosao.create(self.retangulo.centerx, self.retangulo.centery - SPRITE_SIZE)
                pygame.mixer.Sound.play(pygame.mixer.Sound('assets/hit.mp3'))
                self.levar_dano()
                Bala.tiros_jogador.remove(proj)
                break  # evita RuntimeError por alterar a lista durante o loop

    def atingir_jogador(self, jogador):
        agora = time()
        caixa_inimigo = self.retangulo.inflate(-self.retangulo.width * 0.3, -self.retangulo.height * 0.3)
        caixa_jogador = jogador.rect.inflate(-jogador.rect.width * 0.3, -jogador.rect.height * 0.3)
        if caixa_inimigo.colliderect(caixa_jogador) and (agora - self.tempo_ultimo_impacto > 1):
            jogador.setLife(jogador.getLife() - 1)
            self.tempo_ultimo_impacto = agora

    def atirar(self, frequencia):
        for _ in range(frequencia):
            if randint(0, 1000) < 2:
                Bala(self.retangulo.centerx, self.retangulo.centery, 3, False)

    def logica_movimento(self, dt, jogador, peso):
        if self.y > (config.window_size[1] - (SCALED_SPRITE_SIZE + 10)):
            jogador.setLife(jogador.getLife() - 1)

        if randint(0, 500 * peso) < 1:
            self.descendo = True
            self.y_antiga = self.y

        if self.descendo:
            if self.y < self.y_antiga + SCALED_SPRITE_SIZE:
                self.y += self.velocidade * dt
            else:
                self.descendo = False
        else:
            if self.direcao_horizontal:
                self.x += self.velocidade * dt
                if self.x > config.window_size[0] - (config.window_size[0] * (peso * 0.1)):
                    self.direcao_horizontal = False
            else:
                self.x -= self.velocidade * dt
                if self.x < (config.window_size[0] * (peso * 0.1)):
                    self.direcao_horizontal = True

    def atualizar(self, dt, ultimo_tempo, tela, jogador, peso):
        self.ultimo_tempo = ultimo_tempo
        self.verificar_morte()
        self.mover(dt, jogador)
        self.atingir_jogador(jogador)
        self.atirar(peso)

        self.explosao.update(dt)
        self.explosao.draw(tela)

        self.retangulo.topleft = (self.x, self.y)

        if (self.x > config.window_size[0] + 100 or self.x < -100 or self.y > config.window_size[1] or self.y < -100) and ((self.ultimo_tempo - self.ultimo_dano) > 1):
            self.ultimo_dano = self.ultimo_tempo
            self.levar_dano()

        self.animar(dt)
        self.desenhar(tela)

    def desenhar(self, tela):
        tela.blit(self.imagem, self.retangulo)

    @staticmethod
    def gerar_inimigos(quantidade, classe_inimigo):
        margem = SCALED_SPRITE_SIZE // 2
        for _ in range(quantidade):
            x = randint(margem, config.window_size[0] - margem)
            y = config.window_size[1] / 2 - 320
            classe_inimigo((x, y))


class InimigoMenor(InimigoBase):
    lista_instancias = []
    sprites_carregados = None

    def __init__(self, posicao):
        if not InimigoMenor.sprites_carregados:
            InimigoMenor.sprites_carregados = self.carregar_sprites(['assets/enemy_idle1.png', 'assets/enemy_idle2.png'])
        super().__init__(posicao, InimigoMenor.sprites_carregados, InimigoMenor.lista_instancias)
        self.vida = 1

    def carregar_sprites(self, arquivos):
        return [self.preparar_sprite(arquivo) for arquivo in arquivos]

    def preparar_sprite(self, arquivo):
        img = pygame.image.load(arquivo).convert()
        img = pygame.transform.flip(img, False, True)
        img = pygame.transform.scale(img, (img.get_width() * SCALE, img.get_height() * SCALE))
        img.set_colorkey((0, 0, 0))
        return img

    def mover(self, dt, jogador):
        self.logica_movimento(dt, jogador, peso=1)

    def update(self, dt, tempo, tela, jogador):
        super().atualizar(dt, tempo, tela, jogador, 1)


class InimigoMedio(InimigoBase):
    lista_instancias = []
    sprites_carregados = None

    def __init__(self, posicao):
        if not InimigoMedio.sprites_carregados:
            InimigoMedio.sprites_carregados = self.carregar_sprites(['assets/enemy_medium1.png', 'assets/enemy_medium2.png'])
        super().__init__(posicao, InimigoMedio.sprites_carregados, InimigoMedio.lista_instancias)
        self.vida = 3
        self.velocidade *= 0.75
        self.sentido_x = 1

    def carregar_sprites(self, arquivos):
        return [self.preparar_sprite(arquivo) for arquivo in arquivos]

    def preparar_sprite(self, arquivo):
        img = pygame.image.load(arquivo).convert()
        img = pygame.transform.flip(img, False, True)
        img = pygame.transform.scale(img, (img.get_width() * SCALE, img.get_height() * SCALE))
        img.set_colorkey((0, 0, 0))
        return img

    def mover(self, dt, jogador):
        t = pygame.time.get_ticks() / 1000.0
        freq = 0.5
        self.x += self.velocidade * dt * math.sin(2 * math.pi * freq * t) * self.sentido_x
        self.y += self.velocidade * dt * math.sin(2 * math.pi * freq * t)

    def update(self, dt, tempo, tela, jogador):
        super().atualizar(dt, tempo, tela, jogador, 2)


class InimigoGrande(InimigoBase):
    lista_instancias = []
    sprites_carregados = None

    def __init__(self, posicao):
        if not InimigoGrande.sprites_carregados:
            InimigoGrande.sprites_carregados = self.carregar_sprites(['assets/enemy_big1.png', 'assets/enemy_big2.png'])
        super().__init__(posicao, InimigoGrande.sprites_carregados, InimigoGrande.lista_instancias)
        self.vida = 5
        self.velocidade *= 0.5
        self.sentido = choice([-1, 1])

    def carregar_sprites(self, arquivos):
        return [self.preparar_sprite(arquivo) for arquivo in arquivos]

    def preparar_sprite(self, arquivo):
        img = pygame.image.load(arquivo).convert()
        img = pygame.transform.flip(img, False, True)
        img = pygame.transform.scale(img, (img.get_width() * SCALE, img.get_height() * SCALE))
        img.set_colorkey((0, 0, 0))
        return img

    def mover(self, dt, jogador):
        t = pygame.time.get_ticks() / 1000.0
        freq = 0.5
        self.x += self.velocidade * dt * math.sin(2 * math.pi * freq * t) * self.sentido
        self.y += self.velocidade * dt * math.cos(2 * math.pi * freq * t) * self.sentido

    def update(self, dt, tempo, tela, jogador):
        super().atualizar(dt, tempo, tela, jogador, 3)
