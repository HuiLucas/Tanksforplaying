import pygame

pygame.init()
clock = pygame.time.Clock()
screen = pygame.display.set_mode((100, 100))

running = True

while running = True:
    pygame.event.pump()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    screen.fill((0, 0, 255))

    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT]:
        running = False
    pygame.display.flip()
    clock.tick(simulation_speed)

pygame.quit()