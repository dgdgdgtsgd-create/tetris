import pygame
from game import Game

WIDTH, HEIGHT = 820, 680
FPS = 60


def main():
    pygame.mixer.pre_init(44100, -16, 2, 512)
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Тетрис • Neon Blocks")
    clock = pygame.time.Clock()
    game = Game()

    running = True
    while running:
        dt = clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            else:
                game.handle_event(event)

        game.update(dt)
        screen.fill((16, 19, 31))
        game.draw(screen)
        pygame.display.flip()

    game.save_best()
    pygame.quit()


if __name__ == "__main__":
    main()
