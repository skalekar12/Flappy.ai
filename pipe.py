import pygame
import random
from constants import *

class Pipe:
    def __init__(self):
        self.x = SCREEN_WIDTH
        self.gap_y = random.randint(100, SCREEN_HEIGHT - 300)
        self.passed = False

    def move(self, speed):
        self.x -= speed

    def draw(self, screen, pipe_img, pipe_img_flipped):
        screen.blit(pipe_img_flipped, (self.x, self.gap_y - PIPE_HEIGHT))
        screen.blit(pipe_img, (self.x, self.gap_y + GAP_SIZE))

    def off_screen(self):
        return self.x + PIPE_WIDTH < 0

    def collide(self, bird):
        bird_rect = pygame.Rect(bird.x + 4, bird.y + 4, BIRD_SIZE - 8, BIRD_SIZE - 8)
        top_pipe_rect = pygame.Rect(self.x, 0, PIPE_WIDTH, self.gap_y)
        bottom_pipe_rect = pygame.Rect(self.x, self.gap_y + GAP_SIZE, PIPE_WIDTH, SCREEN_HEIGHT)
        return bird_rect.colliderect(top_pipe_rect) or bird_rect.colliderect(bottom_pipe_rect)