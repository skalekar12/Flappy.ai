import numpy as np
from constants import *

class Bird:
    def __init__(self, neural_net=None, is_human=False):
        self.reset_position()
        self.alive = True
        self.score = 0
        self.fitness = 0
        self.is_human = is_human

        if neural_net is not None:
            self.weights = neural_net.copy()
        else:
            self.weights = np.random.randn(2)

    def reset_position(self):
        self.x = 100
        self.y = SCREEN_HEIGHT // 2
        self.velocity = 0

    def think(self, next_pipe):
        if next_pipe is None or self.is_human:
            return

        inputs = np.array([
            (next_pipe.gap_y + GAP_SIZE / 2 - self.y) / SCREEN_HEIGHT,
            (next_pipe.x - self.x) / SCREEN_WIDTH
        ])
        output = np.dot(inputs, self.weights)

        if output > 0:
            self.jump()

    def jump(self):
        self.velocity = JUMP_STRENGTH

    def update(self):
        self.velocity += GRAVITY
        self.y += self.velocity
        self.fitness += 1

        if self.y < 0:
            self.y = 0
            self.velocity = 0
        if self.y + BIRD_SIZE > SCREEN_HEIGHT:
            self.alive = False

    def draw(self, screen, bird_img):
        screen.blit(bird_img, (self.x, self.y))
