from classes.Bullet import Bullet
from classes.Enemy import *
from classes.Player import Player

from states.Menu import Menu
from states.Pause import *
from states.GameState import GameState
from states.Options import Options
from states.GameOver import *
from constants.global_imports import *
from constants.global_var import *
from constants.global_func import *


pygame.init()
clock = pygame.time.Clock()

if config.set_fullscreen:
    screen = pygame.display.set_mode(config.window_size, pygame.FULLSCREEN, vsync=True)
else:                       
    screen = pygame.display.set_mode(config.window_size, vsync=True)

last_time = time()

pygame.mixer.init()
pygame.mixer.music.load("assets/Mercury.wav")
pygame.mixer.music.play(-1)
pygame.mixer.music.set_volume(0.3)


class Jogo(GameState):
    level = 1

    def __init__(self, screen=screen):
        super().__init__()
        self.player = Player((config.window_size[0] / 2, (config.window_size[1] / 2) + 150))
        self.background_fall = Fall(300)
        self.bullets = Bullet(self.player.rect[0] + SPRITE_SIZE, self.player.rect[1] + SPRITE_SIZE / 2, 5)

        self.next_state = "Pause"
        self.last_time = last_time
        self.level = 1
        self.enemies_spawned = False
        
        self.backgrounds = []
        for i in range(1, 10):  # tenta carregar de bg1.png até bg9.png
            path = f"assets/backgrounds/bg{i}.png"
            try:
                bg = pygame.image.load(path).convert()
                self.backgrounds.append(bg)
            except FileNotFoundError:
                break  # para de tentar se não encontrar mais arquivos

        self.bg_scroll_y = 0
        self.bg_speed = 1
        
        self.heart_img = pygame.image.load('assets/heart.png').convert_alpha()
        self.heart_img = pygame.transform.scale(self.heart_img, (40, 40))

    def start(self):
        if Player.getLife(self.player) <= 0:
            del self.player
            [instance.kill() for instance in Enemy1.instancelist]
            [instance.kill() for instance in Enemy2.instancelist]
            [instance.kill() for instance in Enemy3.instancelist]
            self.level = 1
            self.player = Player((config.window_size[0] / 2, (config.window_size[1] / 2) + 150))
            self.next_state = "Pause"
            self.enemies_spawned = False

    def get_event(self, event):
        if event.type == KEYDOWN:
            self.player.get_input(event)
            if event.key in CONTROLS['ESC']:
                self.done = True
        if event.type == KEYUP:
            self.player.get_input_keyup(event)

    def update(self, surf=screen):
        dt, self.last_time = delta_time(self.last_time)
        
        # Atualiza fundo com rolagem vertical
        self.bg_scroll_y += self.bg_speed
        if self.bg_scroll_y >= config.window_size[1]:
            self.bg_scroll_y = 0

        self.bullets.update(dt, surf)
        self.player.update(dt, self.last_time)
        self.background_fall.update(gravity=self.level * 3 / 3)

        if Enemy1.instancelist:
            for instance in Enemy1.instancelist:
                instance.update(dt, self.last_time, surf, self.player)
        if Enemy2.instancelist:
            for instance in Enemy2.instancelist:
                instance.update(dt, self.last_time, surf, self.player)
        if Enemy3.instancelist:
            for instance in Enemy3.instancelist:
                instance.update(dt, self.last_time, surf, self.player)

        # Verifica se todos os inimigos morreram
        if not Enemy1.instancelist and not Enemy2.instancelist and not Enemy3.instancelist:
            if self.enemies_spawned:  # Sobe de fase só uma vez
                self.level += 1
                self.enemies_spawned = False

        # Gera os inimigos apenas se ainda não gerou para esta fase
        if not self.enemies_spawned:
            EnemyBase.spawn_enemy(self.level * 5, Enemy1)
            EnemyBase.spawn_enemy(self.level * 2, Enemy2)
            EnemyBase.spawn_enemy(self.level * 1, Enemy3)
            self.enemies_spawned = True

        if self.player.getLife() <= 0:
            self.next_state = "GameOver"
            self.done = True

    def draw(self, surf=screen):
        
        # Fundo com rolagem vertical contínua
        bg = self.backgrounds[(self.level - 1) % len(self.backgrounds)]
        bg = pygame.transform.scale(bg, config.window_size)

        surf.blit(bg, (0, -config.window_size[1] + self.bg_scroll_y))
        surf.blit(bg, (0, self.bg_scroll_y))

        self.player.draw(surf)

        vida_x = config.window_size[0] - 190
        vida_y = config.window_size[1] - 60

        text('Vida:', vida_x, vida_y, color=(255, 255, 255), original_font=False)

        # Pega o número de vidas
        vidas = self.player.getLife()

        espaco_entre_coracoes = 40

        for i in range(vidas):
            heart_pos_x = vida_x + 50 + i * espaco_entre_coracoes
            heart_pos_y = vida_y - 25
            surf.blit(self.heart_img, (heart_pos_x, heart_pos_y))

        fase_x = vida_x
        fase_y = vida_y + 30
        text(f'Fase {self.level}', fase_x, fase_y, original_font=False)


class GameRunner(object):
    def __init__(self, screen, states, start_state):
        self.screen = screen
        self.states = states
        self.start_state = start_state
        self.state = self.states[self.start_state]

        self.state.start()
        self.run()

    def run(self):
        running = True
        while running:
            self.get_events()
            self.update()
            self.draw()

    def get_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.quit()

            self.state.get_event(event)

    def update(self):
        self.state.update()
        if self.state.done:
            self.next_state()

    def next_state(self):
        next_state = self.state.next_state
        self.state.done = False
        self.state_name = next_state
        self.state = self.states[self.state_name]
        self.state.start()

    def quit(self):
        pygame.quit()
        sys.exit()

    def draw(self):
        pygame.display.set_caption(f'Shoot \'em Up. FPS: {int(clock.get_fps())}')
        clock.tick(FRAME_RATE)
        pygame.display.update()
        self.state.draw(self.screen)


if __name__ == "__main__":
    states = {
        "Menu":     Menu(),
        "Game":     Jogo(),
        "Pause":    Pause(),
        "Exit":     Exit(),
        "Options":  Options(),
        "GameOver": GameOver()
    }
    game = GameRunner(screen, states, "Menu")