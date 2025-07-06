from elementos.Bala import Bala
from elementos.Inimigo import *
from elementos.Jogador import Player

from states.Menu import Menu
from states.Tutorial import Tutorial
from states.Pausa import *
from states.GameState import GameState
from states.GameOver import *
from constants.global_imports import *
from constants.global_var import *
from constants.global_func import *

pygame.init()
clock = pygame.time.Clock()

# Define o modo de exibição da janela (tela cheia ou janela comum)
if config.set_fullscreen:
    tela = pygame.display.set_mode(config.window_size, pygame.FULLSCREEN, vsync=True)
else:
    tela = pygame.display.set_mode(config.window_size, vsync=True)

ultimo_tempo = time()

# Música de fundo
pygame.mixer.init()
pygame.mixer.music.load("assets/Mercury.wav")
pygame.mixer.music.play(-1)
pygame.mixer.music.set_volume(0.3)


class Jogo(GameState):
    fase = 1

    def __init__(self, tela=tela):
        super().__init__()
        self.jogador = Player((config.window_size[0] / 2, (config.window_size[1] / 2) + 150))
        self.efeito_fundo = Fall(300)
        self.balas = Bala(self.jogador.rect[0] + SPRITE_SIZE, self.jogador.rect[1] + SPRITE_SIZE / 2, 5)

        self.next_state = "Pausa"
        self.ultimo_tempo = ultimo_tempo
        self.fase = 1
        self.inimigos_criados = False

        self.fundos = []
        for i in range(1, 10):  # Tenta carregar bg1.png até bg9.png
            caminho = f"assets/backgrounds/bg{i}.png"
            try:
                imagem_fundo = pygame.image.load(caminho).convert()
                self.fundos.append(imagem_fundo)
            except FileNotFoundError:
                break  # Para ao não encontrar mais imagens

        self.scroll_y = 0
        self.velocidade_scroll = 1

        self.img_coracao = pygame.image.load('assets/heart.png').convert_alpha()
        self.img_coracao = pygame.transform.scale(self.img_coracao, (40, 40))

    def start(self):
        if Player.getLife(self.jogador) <= 0:
            del self.jogador
            [instancia.eliminar() for instancia in InimigoMenor.lista_instancias[:]]
            [instancia.eliminar() for instancia in InimigoMedio.lista_instancias[:]]
            [instancia.eliminar() for instancia in InimigoGrande.lista_instancias[:]]
            self.fase = 1
            self.jogador = Player((config.window_size[0] / 2, (config.window_size[1] / 2) + 150))
            self.next_state = "Pausa"
            self.inimigos_criados = False

    def get_event(self, evento):
        if evento.type == KEYDOWN:
            self.jogador.get_input(evento)
            if evento.key in CONTROLS['ESC']:
                self.done = True
        elif evento.type == KEYUP:
            self.jogador.get_input_keyup(evento)

    def update(self, surf=tela):
        dt, self.ultimo_tempo = delta_time(self.ultimo_tempo)

        # Animação de fundo com rolagem contínua
        self.scroll_y += self.velocidade_scroll
        if self.scroll_y >= config.window_size[1]:
            self.scroll_y = 0

        self.balas.atualizar(dt, surf)
        self.jogador.update(dt, self.ultimo_tempo)
        self.efeito_fundo.update(gravity=self.fase)

        for inimigos in (InimigoMenor.lista_instancias, InimigoMedio.lista_instancias, InimigoGrande.lista_instancias):
            for instancia in inimigos:
                instancia.update(dt, self.ultimo_tempo, surf, self.jogador)

        # Verifica se todos os inimigos foram derrotados
        if not InimigoMenor.lista_instancias and not InimigoMedio.lista_instancias and not InimigoGrande.lista_instancias:
            if self.inimigos_criados:
                self.fase += 1
                self.inimigos_criados = False

        if not self.inimigos_criados:
            InimigoBase.gerar_inimigos(self.fase * 5, InimigoMenor)
            InimigoBase.gerar_inimigos(self.fase * 2, InimigoMedio)
            InimigoBase.gerar_inimigos(self.fase * 1, InimigoGrande)
            self.inimigos_criados = True

        if self.jogador.getLife() <= 0:
            self.next_state = "GameOver"
            self.done = True

    def draw(self, surf=tela):
        fundo_atual = self.fundos[(self.fase - 1) % len(self.fundos)]
        fundo_atual = pygame.transform.scale(fundo_atual, config.window_size)

        surf.blit(fundo_atual, (0, -config.window_size[1] + self.scroll_y))
        surf.blit(fundo_atual, (0, self.scroll_y))

        self.jogador.draw(surf)

        pos_x_vida = config.window_size[0] - 190
        pos_y_vida = config.window_size[1] - 60

        text('Vida:', pos_x_vida, pos_y_vida, color=(255, 255, 255), original_font=False)

        qtd_vidas = self.jogador.getLife()
        espacamento = 40

        for i in range(qtd_vidas):
            coracao_x = pos_x_vida + 50 + i * espacamento
            coracao_y = pos_y_vida - 25
            surf.blit(self.img_coracao, (coracao_x, coracao_y))

        text(f'Fase {self.fase}', pos_x_vida, pos_y_vida + 30, original_font=False)


class ExecutorDoJogo:
    def __init__(self, tela, estados, estado_inicial):
        self.tela = tela
        self.estados = estados
        self.estado_atual = self.estados[estado_inicial]

        self.estado_atual.start()
        self.executar()

    def executar(self):
        ativo = True
        while ativo:
            self.tratar_eventos()
            self.atualizar()
            self.renderizar()

    def tratar_eventos(self):
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                self.encerrar()
            self.estado_atual.get_event(evento)

    def atualizar(self):
        self.estado_atual.update()
        if self.estado_atual.done:
            self.mudar_estado()

    def mudar_estado(self):
        proximo = self.estado_atual.next_state
        self.estado_atual.done = False
        self.estado_atual = self.estados[proximo]
        self.estado_atual.start()

    def encerrar(self):
        pygame.quit()
        sys.exit()

    def renderizar(self):
        pygame.display.set_caption('Tiro Certeiro')
        clock.tick(FRAME_RATE)
        pygame.display.update()
        self.estado_atual.draw(self.tela)


if __name__ == "__main__":
    estados = {
        "Menu":     Menu(),
        "Game":     Jogo(),
        "Pausa":    Pausa(),
        "Exit":     Exit(),
        "GameOver": GameOver(),
        "Tutorial": Tutorial() 
    }
    ExecutorDoJogo(tela, estados, "Menu")
