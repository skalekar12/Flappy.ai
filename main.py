import pygame
import numpy as np
from constants import *
from button import Button
from bird import Bird
from pipe_manager import PipeManager

# Initialize Pygame
pygame.init()

# Set up the game window
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Flappy Bird - AI/Human Mode")

# Load and process images
def load_image_without_background(path, size=None):
    img = pygame.image.load(path).convert_alpha()
    if size:
        img = pygame.transform.scale(img, size)
    return img

# Load images with proper transparency
BIRD_IMG = load_image_without_background("index.png", (BIRD_SIZE, BIRD_SIZE))
PIPE_IMG = load_image_without_background("pipe.png", (PIPE_WIDTH, PIPE_HEIGHT))
PIPE_IMG_FLIPPED = pygame.transform.flip(PIPE_IMG, False, True)
BG_IMG = pygame.image.load("background.png").convert()
BG_IMG = pygame.transform.scale(BG_IMG, (SCREEN_WIDTH, SCREEN_HEIGHT))

# Set up fonts
font = pygame.font.SysFont(None, 36)
large_font = pygame.font.SysFont(None, 72)

def draw_menu(selected_option):
    screen.blit(BG_IMG, (0, 0))
    title = large_font.render("Flappy Bird", True, BLACK)
    title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 200))
    screen.blit(title, title_rect)

    # Define the buttons for AI mode and Human mode
    ai_button = Button(SCREEN_WIDTH // 2 - 100, 300, 200, 50, "Play AI Mode", BLUE)
    human_button = Button(SCREEN_WIDTH // 2 - 100, 400, 200, 50, "Play Human Mode", RED)

    # Draw the buttons
    ai_button.draw(screen, font)
    human_button.draw(screen, font)

    # Draw a border around the selected option
    if selected_option == 0:
        pygame.draw.rect(screen, WHITE, ai_button.rect, 4)
    elif selected_option == 1:
        pygame.draw.rect(screen, WHITE, human_button.rect, 4)

    return ai_button, human_button

def play_human_mode():
    pipe_manager = PipeManager(PIPE_DISTANCE)
    bird = Bird(is_human=True)
    score = 0
    clock = pygame.time.Clock()
    game_started = False
    game_over = False

    # Instructions text
    start_text = font.render("Click to Start!", True, BLACK)
    start_text_rect = start_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
    controls_text = font.render("Click anywhere to jump", True, BLACK)
    controls_text_rect = controls_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50))

    while True:
        clock.tick(60)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return MENU
            elif event.type == pygame.MOUSEBUTTONDOWN2:
                if not game_started:
                    game_started = True
                elif not game_over:
                    bird.jump()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return MENU

        if game_started and not game_over:
            pipe_manager.update()
            bird.update()

            # Check collisions
            for pipe in pipe_manager.pipes:
                if pipe.collide(bird):
                    game_over = True
                    break

            if not bird.alive:
                game_over = True

        screen.blit(BG_IMG, (0, 0))
        pipe_manager.draw(screen, PIPE_IMG, PIPE_IMG_FLIPPED)
        bird.draw(screen, BIRD_IMG)

        score = pipe_manager.passed_count
        score_text = font.render(f"Score: {score}", True, BLACK)
        screen.blit(score_text, (10, 10))

        if not game_started:
            screen.blit(start_text, start_text_rect)
            screen.blit(controls_text, controls_text_rect)
        elif game_over:
            game_over_text = large_font.render("Game Over!", True, RED)
            game_over_rect = game_over_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
            final_score_text = font.render(f"Final Score: {score}", True, BLACK)
            final_score_rect = final_score_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50))
            restart_text = font.render("Press ESC for menu", True, BLACK)
            restart_rect = restart_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 100))

            screen.blit(game_over_text, game_over_rect)
            screen.blit(final_score_text, final_score_rect)
            screen.blit(restart_text, restart_rect)

        pygame.display.flip()

        if game_over:
            pygame.time.wait(500)
            waiting_for_restart = True
            while waiting_for_restart:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        return MENU
                    elif event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_ESCAPE:
                            return MENU

def evaluate_population(birds, pipe_manager):
    birds_alive = 0
    for bird in birds:
        if bird.alive:
            birds_alive += 1
            next_pipe = pipe_manager.get_next_pipe(bird.x)
            bird.think(next_pipe)
            bird.update()
            for pipe in pipe_manager.pipes:
                if pipe.collide(bird):
                    bird.alive = False
                    break
    return birds, birds_alive

def select_and_breed(birds):
    birds.sort(key=lambda b: (b.score, b.fitness), reverse=True)
    best_bird = birds[0]
    second_best_bird = birds[1]
    new_birds = []

    for i in range(BIRD_COUNT):
        mutation_strength = 0.1 if i < 50 else 0.2
        parent = best_bird if i < 75 else second_best_bird
        new_bird = Bird(parent.weights)
        new_bird.weights += np.random.normal(0, mutation_strength, size=new_bird.weights.shape)
        new_birds.append(new_bird)

    return new_birds

def play_ai_mode():
    clock = pygame.time.Clock()
    generation = 0
    pipe_manager = PipeManager(PIPE_DISTANCE)
    birds = [Bird() for _ in range(BIRD_COUNT)]
    all_time_max_score = 0
    generations_without_improvement = 0
    birds_alive = BIRD_COUNT

    while True:
        clock.tick(65)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return MENU
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return MENU
                elif event.key == pygame.K_UP:
                    pipe_manager.pipe_distance += 50
                elif event.key == pygame.K_DOWN:
                    pipe_manager.pipe_distance = max(200, pipe_manager.pipe_distance - 50)

        pipe_manager.update()
        birds, birds_alive = evaluate_population(birds, pipe_manager)
        current_score = pipe_manager.passed_count

        if birds_alive == 0:
            if current_score > all_time_max_score:
                all_time_max_score = current_score
                generations_without_improvement = 0
            else:
                generations_without_improvement += 1

            if generations_without_improvement >= 10:
                return MENU

            generation += 1
            birds = select_and_breed(birds)
            birds_alive = BIRD_COUNT
            pipe_manager = PipeManager(pipe_manager.pipe_distance)

        screen.blit(BG_IMG, (0, 0))
        pipe_manager.draw(screen, PIPE_IMG, PIPE_IMG_FLIPPED)

        for bird in birds:
            if bird.alive:
                bird.draw(screen, BIRD_IMG)

        # Draw stats
        texts = [
            f"Generation: {generation}",
            f"Current Score: {current_score}",
            f"All-Time Max Score: {all_time_max_score}",
            f"Birds Alive: {birds_alive}",
            f"Generations without improvement: {generations_without_improvement}",
            f"Pipe Distance: {pipe_manager.pipe_distance}",
            f"Current Speed: {pipe_manager.current_speed:.1f}",
            "Press ESC to return to menu"
        ]

        for i, text in enumerate(texts):
            draw_text = font.render(text, True, BLACK)
            screen.blit(draw_text, (10, 10 + i * 40))

        pygame.display.flip()

def main():
    game_state = MENU
    selected_option = 0  # 0 for AI, 1 for Human

    while True:
        if game_state == MENU:
            ai_button, human_button = draw_menu(selected_option)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:
                        selected_option = (selected_option - 1) % 2
                    elif event.key == pygame.K_DOWN:
                        selected_option = (selected_option + 1) % 2
                    elif event.key == pygame.K_RETURN:
                        if selected_option == 0:
                            game_state = PLAYING_AI
                        elif selected_option == 1:
                            game_state = PLAYING_HUMAN

            pygame.display.flip()

        elif game_state == PLAYING_AI:
            game_state = play_ai_mode()

        elif game_state == PLAYING_HUMAN:
            game_state = play_human_mode()

if __name__ == "__main__":
    main()