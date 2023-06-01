# only allowed to use: pygame, matplotlib, numpy, scipy
import pygame as pg
import numpy as np

import classes as custom

# set up constants
display_height = 700
display_width = 1200
cool_off_time = 500  # minimum time between shots (in ms)
bullet_speed = 1200

planet_radius = 4  # these values don't actually mean anything, just fiddle with them until they're okay
terrain_height = 0.75

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (50, 50, 50)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
LIGHT_BLUE = (100, 100, 255)
LIGHT_RED = (255, 100, 100)

framerate = 60

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

# create the planet
planet = custom.Planet((display_width / 2, display_height * planet_radius),
                       display_height * (planet_radius - terrain_height), BLUE)

# set up movement boundaries for the tank
if display_width < planet.radius * 2:
    boundary_angle = np.arcsin(display_width / (2 * planet.radius))
else:
    boundary_angle = -10  # -10 is an impossible value, so it's recognizable

# create the tank
tank = custom.TankBody(-np.pi / 2, (20, 30), 8, RED, boundary_angle)

# create the crosshair
crosshair = custom.Crosshairs((0, 0), (50, 50))

# list containing all the bullets, because we're going to have quite a lot of them
bullets = [custom.Bullet((100, 100), (40, 10), (1, 1), GREEN)]

# start the cool-off timer
cooloff_timer = pg.time.get_ticks()

running = True

while running:
    pg.event.pump()

    for event in pg.event.get():
        if event.type == pg.QUIT:
            running = False

        # shoot the bullet
        if pg.mouse.get_pressed()[0]:
            if pg.time.get_ticks() - cooloff_timer > cool_off_time:
                # reset the cool off timer
                cooloff_timer = pg.time.get_ticks()

                # find direction to shoot
                direction = pg.mouse.get_pos() - pg.math.Vector2(tank.x, tank.y)
                direction = direction.normalize()

                # create a bullet with init velocity and direction
                bullets.append(custom.Bullet((tank.x, tank.y), (15, 5), direction * bullet_speed + tank.vel, GREEN))

    screen.fill(BLACK)

    # press escape to close the game
    keys = pg.key.get_pressed()
    if keys[pg.K_ESCAPE]:
        running = False
        break

    # move the tank (1 is right, -1 is left. don't change these, they act like booleans)
    if keys[pg.K_RIGHT]:
        screen.blit(font1.render("Right arrow key pressed", False, WHITE), (100, 100))
        tank.move(1)
    elif keys[pg.K_LEFT]:
        screen.blit(font1.render("Left arrow key pressed", False, WHITE), (100, 100))
        tank.move(-1)
    else:
        tank.move(0)

    # text with misc content for debugging
    screen.blit(font1.render(str(pg.time.get_ticks()), False, WHITE), (200, 200))

    # display the planet
    pg.draw.circle(screen, planet.color, planet.pos, planet.radius)

    # displaying the tank. this needs quite a bit of stuff, so it has to be like this, afaik.
    tank_surface_results = tank.get_surf(planet.pos, planet.radius)
    screen.blit(tank_surface_results[0], tank_surface_results[1])

    # deal with bullets
    for bullet in bullets:
        # delete bullets if too far out
        if bullet.pos[0] > display_width * 2 or bullet.pos[0] < - display_width or bullet.pos[1] > display_height * 2 or \
                bullet.pos[1] < - display_height:
            del bullet
        else:
            # update and display
            bullet.attraction(planet.pos)
            bullet.move()
            screen.blit(bullet.rotated_surface, bullet.rotated_rect)

    # display the crosshair
    crosshair.pos = pg.mouse.get_pos()
    screen.blit(crosshair.surface, crosshair.surface.get_rect(center=crosshair.pos))

    pg.display.flip()
    clock.tick(framerate)

pg.quit()
