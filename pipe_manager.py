from pipe import Pipe
from constants import *

class PipeManager:
    def __init__(self, pipe_distance):
        self.pipe_distance = pipe_distance
        self.pipes = [Pipe()]
        self.passed_count = 0
        self.current_speed = BASE_PIPE_SPEED

    def calculate_speed(self):
        speed_multiplier = 1 + (0.05 * (self.passed_count // 5))
        self.current_speed = BASE_PIPE_SPEED * speed_multiplier

    def update(self):
        if len(self.pipes) == 0 or self.pipes[-1].x <= SCREEN_WIDTH - self.pipe_distance:
            self.pipes.append(Pipe())

        self.calculate_speed()

        for pipe in self.pipes:
            pipe.move(self.current_speed)

        for pipe in self.pipes:
            if pipe.off_screen():
                self.passed_count += 1

        self.pipes = [pipe for pipe in self.pipes if not pipe.off_screen()]

    def get_next_pipe(self, bird_x):
        for pipe in self.pipes:
            if pipe.x + PIPE_WIDTH > bird_x:
                return pipe
        return self.pipes[0] if self.pipes else None

    def draw(self, screen, pipe_img, pipe_img_flipped):
        for pipe in self.pipes:
            pipe.draw(screen, pipe_img, pipe_img_flipped)

    def reset(self):
        self.__init__(self.pipe_distance)
