# only allowed to use: pygame, matplotlib, numpy, scipy
import pygame as pg
import numpy as np

# set up constants
display_height = 700
display_width = 1200

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (50, 50, 50)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
LIGHT_BLUE = (100, 100, 255)
LIGHT_RED = (255, 100, 100)

framerate = 1000


# pygame init stuff

# screen and clock
pg.init()
pg.display.set_caption("Tanks for Playing!")
clock = pg.time.Clock()
screen = pg.display.set_mode((display_width, display_height))
pg.display.set_icon(pg.image.load("Glyphish-Glyphish-23-bird.32.png"))

# font (for writing, obvs)
pg.font.init()
font1 = pg.font.SysFont("Comic Sans MS", 45)


running = True

while running:
    pg.event.pump()

    for event in pg.event.get():
        if event.type == pg.QUIT:
            running = False

    screen.fill(BLACK)

    keys = pg.key.get_pressed()
    if keys[pg.K_ESCAPE]:
        running = False
    elif keys[pg.K_RIGHT]:
        screen.blit(font1.render("Right arrow key pressed", False, WHITE), (100, 100))
    pg.display.flip()
    clock.tick(framerate)

pg.quit()
