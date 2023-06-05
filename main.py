# only allowed to use: pygame, matplotlib, numpy, scipy
import random
import numba

import pygame as pg
import numpy as np

import classes as custom

# set up constants
display_height = 700
display_width = 1200
cool_off_time = 1000  # minimum time between shots (in ms)
bullet_speed = 1200

planet_radius = 4  # these values don't actually mean anything, just fiddle with them until they're okay
terrain_height = 0.75

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (50, 50, 50)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
MARS_RED = (160, 50, 50)
RED = (255, 0, 0)
LIGHT_BLUE = (100, 100, 255)
LIGHT_RED = (255, 100, 100)

framerate = 60

# pygame init stuff

# screen and clock
pg.init()
pg.display.set_caption("Tanks for Playing!")
clock = pg.time.Clock()
screen = pg.display.set_mode((display_width, display_height), pg.DOUBLEBUF)
pg.display.set_icon(pg.image.load("Glyphish-Glyphish-23-bird.32.png"))


# font (for writing, obvs)
pg.font.init()
font1 = pg.font.SysFont("Comic Sans MS", 45)
font2 = pg.font.SysFont("Comic Sans MS", 20)

# load background image and convert into proper size
background = pg.image.load('Artwork/Stars-HD-Desktop-Wallpaper-44242.jpg')
background.convert()
background = pg.transform.scale_by(background, 0.55)
# background rect
background_rect = background.get_rect()
background_rect.center = display_width // 2, display_height // 2

# create the planet
planet = custom.Planet((display_width / 2, display_height * planet_radius),
                       display_height * (planet_radius - terrain_height), MARS_RED)

# set up movement boundaries for the tank
if display_width < planet.radius * 2:
    boundary_angle = np.arcsin(display_width / (2 * planet.radius))
else:
    boundary_angle = -10  # -10 is an impossible value, so it's recognizable

# create the tanks
tank = custom.Tank(-np.pi / 2, (20, 30), 8, RED, boundary_angle, False)
tank.cool_off_time = cool_off_time

# AI tank
AI_tank = custom.Tank(-np.pi / 2 + 0.1, (20, 30), 8, WHITE, boundary_angle, True)
AI_tank.cool_off_time = cool_off_time

# create the crosshair
crosshair = custom.Crosshairs((0, 0), (50, 50))

# list containing all the bullets, because we're going to have quite a lot of them
bullets = []

# start the cool-off timer
tank.cooloff_timer = pg.time.get_ticks()
AI_tank.cooloff_timer = pg.time.get_ticks() + 2000

running = True

while running:
    pg.event.pump()

    for event in pg.event.get():
        if event.type == pg.QUIT:
            running = False

        # shoot the bullet
        if pg.mouse.get_pressed()[0]:
            if pg.time.get_ticks() - tank.cooloff_timer > tank.cool_off_time:
                # reset the cool off timer
                tank.cooloff_timer = pg.time.get_ticks()

                # find direction to shoot
                direction = pg.mouse.get_pos() - pg.math.Vector2(tank.x, tank.y)
                bullet_speed = 50 * np.sqrt(np.linalg.norm(direction))
                direction = direction.normalize()

                # create a bullet with init velocity and direction
                bullets.append(custom.Bullet((tank.x, tank.y), (15, 5), direction * bullet_speed + tank.vel, GREEN,
                                             pg.time.get_ticks()))
                bullets[-1].Tank = AI_tank

    screen.fill(BLACK)
    screen.blit(background, background_rect)

    # press escape to close the game
    keys = pg.key.get_pressed()
    if keys[pg.K_ESCAPE]:
        running = False
        break

    # move the tank (1 is right, -1 is left. don't change these, they act like booleans)
    if keys[pg.K_RIGHT]:
        screen.blit(font1.render("Right arrow key pressed", False, WHITE), (100, 100))
        tank.move(1)
        tank.cooloff_timer = pg.time.get_ticks()
    elif keys[pg.K_LEFT]:
        screen.blit(font1.render("Left arrow key pressed", False, WHITE), (100, 100))
        tank.move(-1)
        tank.cooloff_timer = pg.time.get_ticks()
    else:
        tank.move(0)

    # move AI Tank
    AI_tank.wantstoshootnow = True
    AI_tank.AI_move(bullets, tank)

    # text with misc content for debugging
    screen.blit(font1.render(str(pg.time.get_ticks()), False, WHITE), (200, 200))
    if pg.time.get_ticks() - tank.cooloff_timer >= tank.cool_off_time:
        screen.blit(font1.render(str(pg.time.get_ticks() - tank.cooloff_timer), False, GREEN), (200, 250))
    else:
        screen.blit(font1.render(str(pg.time.get_ticks() - tank.cooloff_timer), False, RED), (200, 250))
    screen.blit(font2.render("Artwork by Stable Diffusion and DALL-E", False, MARS_RED), (0, 0))

    # display the planet
    background_planet = pg.Surface((display_width, display_height), pg.SRCALPHA)
    pg.draw.circle(background_planet, (150, 100, 100, 30), planet.pos, planet.radius + 60)
    pg.draw.circle(background_planet, (150, 100, 100, 50), planet.pos, planet.radius + 45)
    pg.draw.circle(background_planet, (125, 75, 75, 100), planet.pos, planet.radius + 20)
    pg.draw.circle(background_planet, (100, 50, 50, 150), planet.pos, planet.radius + 8)
    screen.blit(background_planet, (0, 0))
    pg.draw.circle(screen, (255, 230, 230), planet.pos, planet.radius)
    pg.draw.circle(screen, (180, 130, 130), planet.pos, planet.radius - 7)
    pg.draw.circle(screen, planet.color, planet.pos, planet.radius - 18)

    # displaying the tanks. this needs quite a bit of stuff, so it has to be like this, afaik.
    # AI_tank.invisible_mode = True
    tank.display(planet, screen)
    AI_tank.display(planet, screen)

    # deal with bullets
    for bullet in bullets:
        # delete bullets if too far out
        if bullet.pos[0] > display_width * 2 or bullet.pos[0] < - display_width or bullet.pos[1] > display_height * 2 or \
                bullet.pos[1] < - display_height:
            del bullet
        else:
            # update and display
            if pg.time.get_ticks() - bullet.firetime < 200:
                bullet.armed = False
                bullet.surface.set_alpha(100)
            else:
                bullet.armed = True
                if bullet.underground == False:
                    bullet.surface.set_alpha(255)
            bullet.attraction(planet.pos)
            bullet.move()
            screen.blit(bullet.rotated_surface, bullet.rotated_rect)
            bullet.collision(planet, bullet.Tank)

    # display the crosshair
    crosshair.pos = pg.mouse.get_pos()
    screen.blit(crosshair.surface, crosshair.surface.get_rect(center=crosshair.pos))

    pg.display.flip()
    clock.tick(framerate)

pg.quit()


# to do
# main menu
# health bars
# ammo?
# bullet variability
