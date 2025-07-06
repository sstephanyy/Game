from states.GameState import GameState
from constants.global_func import *
from constants.global_imports import *
from constants.global_var import *
from constants.global_func import Fall

pygame.init()
screen = pygame.display.set_mode(config.window_size)


class Tutorial(GameState):
    def __init__(self):
        super().__init__()
        self.fall = Fall(100)

    def start(self):
        self.selected = 0
        self.last_time = pygame.time.get_ticks()

    def update(self, surf=screen):
        dt, self.last_time = delta_time(self.last_time)
        self.fall.update(-3, 0)
        vertical(surf, False, BACKGROUND_COLOR_MENU_1, BACKGROUND_COLOR_MENU_2)

        self.desenhar_texto(surf)

    def get_event(self, event):
        if event.type == KEYDOWN and event.key in CONTROLS['START']:
            pygame.mixer.Sound.play(pygame.mixer.Sound('assets/forceField_001.mp3'))
            self.next_state = 'Menu'
            self.done = True
        elif event.type == KEYDOWN and event.key in CONTROLS['ESC']:
            pygame.mixer.Sound.play(pygame.mixer.Sound('assets/impactMetal_002.ogg'))
            self.next_state = 'Menu'
            self.done = True

    def draw(self, surf):
        self.fall.draw(surf, (200, 200, 200))

    def desenhar_texto(self, surf):
        linhas = [
            "COMO JOGAR",
            "",
            "- SETAS (pra cima, para o lado, para direita, para esquerda) ou (W, A, S, D): mover o jogador",
            "- ESPAÇO: atirar",
            "- ESC: pausar o jogo",
            "",
            "→ Pressione ENTER ou ESC para voltar ao menu ←"
        ]
        base_y = config.window_size[1] // 4  # começa a desenhar a partir de 1/4 da altura da tela
        espacamento = 50  # aumenta o espaçamento vertical entre linhas

        for i, linha in enumerate(linhas):
            fonte = pygame.font.SysFont('arial', 32)
            render = fonte.render(linha, True, (255, 255, 255))
            rect = render.get_rect(center=(config.window_size[0] // 2, base_y + i * espacamento))
            surf.blit(render, rect)
