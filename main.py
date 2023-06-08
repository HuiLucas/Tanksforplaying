# only allowed to use: pygame, matplotlib, numpy, numba
import random
import numba

import pygame as pg
import numpy as np

import classes as custom

# set up constants
display_height = 700
display_width = 1200
cool_off_time = 800  # minimum time between shots (in ms)
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
    boundary_angle = np.arcsin(display_width / (2 * planet.radius)) - np.pi/100
else:
    boundary_angle = -10  # -10 is an impossible value, so it's recognizable

# create the tanks
tank = custom.Tank(-np.pi / 2 - 0.2, (20, 30), 8, RED, boundary_angle, False)
tank.cool_off_time = cool_off_time

# AI tanks
AI_tank = custom.Tank(-np.pi / 2 + 0.1, (20, 30), 8, WHITE, boundary_angle, True)
AI_tank2 = custom.Tank(-np.pi / 2 +0.3, (20, 30), 8, GREEN, boundary_angle, True)
AI_tank3 = custom.Tank(-np.pi / 2, (20, 30), 8, GREEN, boundary_angle, True)
AI_tank4 = custom.Tank(-np.pi / 2 +0.2, (20, 30), 8, GREEN, boundary_angle, True)

# provide the AI tanks with the cool_off_time
for tanks1 in custom.Tanklist:
    if tanks1.AI == True:
        tanks1.cool_off_time = cool_off_time


# create the crosshair
crosshair = custom.Crosshairs((0, 0), (50, 50))

# list containing all the bullets, because we're going to have quite a lot of them
bullets = []

# start the cool-off timer
tank.cooloff_timer = pg.time.get_ticks()
for Tanks2 in custom.Tanklist:
    if Tanks2.AI == True:
        Tanks2.cooloff_timer = pg.time.get_ticks() + 2000



menu_running = True # is the menu screen running
running = True # is the main program itself running
dev_mode = False

# buttons
play_button = custom.Button([display_width/2, display_height/4], [300, 100], WHITE, "Play", BLACK, font1)
controls_button = custom.Button([display_width/2, display_height/4*2], [300, 100], WHITE, "How to play", BLACK, font1)
exit_button = custom.Button([display_width/2, display_height/4*3], [300, 100], WHITE, "Exit", BLACK, font1)
dev_mode_button = custom.Button([display_width/2 + 400, display_height/4*3], [300, 100], WHITE, "Dev Mode", BLACK, font1)

# main menu
while menu_running:
    pg.event.pump()

    for event in pg.event.get():
        if event.type == pg.QUIT:
            running = False
            menu_running = False

    # press escape to quickly quit the game
    keys = pg.key.get_pressed()
    if keys[pg.K_ESCAPE]:
        running = False
        menu_running = False
        break
    screen.fill(BLACK)

    # display buttons
    # play button
    pg.draw.rect(screen, play_button.color, play_button.rect)
    screen.blit(play_button.text_surf, play_button.text_rect)
    # how to play button
    pg.draw.rect(screen, controls_button.color, controls_button.rect)
    screen.blit(controls_button.text_surf, controls_button.text_rect)
    # exit button
    pg.draw.rect(screen, exit_button.color, exit_button.rect)
    screen.blit(exit_button.text_surf, exit_button.text_rect)
    # dev mode button
    pg.draw.rect(screen, dev_mode_button.color, dev_mode_button.rect)
    screen.blit(dev_mode_button.text_surf, dev_mode_button.text_rect)

    # get mouse click
    if pg.mouse.get_pressed()[0]:
        # buttons
        mouse_pos = pg.mouse.get_pos()
        print("AAAAAAAAAAA")

        # check if mouse click is in play button
        if play_button.is_clicked(mouse_pos):
            menu_running = False
            running = True
            break

        # check if mouse click is in exit button
        if exit_button.is_clicked(mouse_pos):
            pg.quit()
            running = False
            menu_running = False
            break

        # check if mouse click is in dev mode button
        if dev_mode_button.is_clicked(mouse_pos):
            menu_running = False
            running = True
            dev_mode = True
            break

    pg.display.flip()
    clock.tick(framerate)

# main program (the game itself)
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
        tank.move(1, pg.time.get_ticks())
        tank.cooloff_timer = pg.time.get_ticks()
    elif keys[pg.K_LEFT]:
        screen.blit(font1.render("Left arrow key pressed", False, WHITE), (100, 100))
        tank.move(-1, pg.time.get_ticks())
        tank.cooloff_timer = pg.time.get_ticks()
    else:
        tank.move(0, pg.time.get_ticks())

    # move AI Tanks
    for tanks3 in custom.Tanklist:
        if tanks3.AI == True:
           tanks3.AI_move(bullets, planet)

    # If development mode is on, use an indicator to know where the bullet is predicted to hit
    if dev_mode:
        screen.blit(font1.render("wheh", False, WHITE), (AI_tank.predictposition, 200))

    # text with misc content for debugging
    screen.blit(font1.render(str(AI_tank.health), False, WHITE), (200, 200))
    screen.blit(font1.render(str(AI_tank.ishit), False, WHITE), (500, 200))
    if pg.time.get_ticks() - tank.cooloff_timer >= tank.cool_off_time:
        screen.blit(font1.render(str(pg.time.get_ticks() - tank.cooloff_timer), False, GREEN), (200, 250))
    else:
        screen.blit(font1.render(str(pg.time.get_ticks() - tank.cooloff_timer), False, RED), (200, 250))
    screen.blit(font2.render("Artwork by Stable Diffusion and DALL-E", False, MARS_RED), (0, 0))

    # display the planet, which consist of a transparent atmosphere, and some shadow circles in front
    background_planet = pg.Surface((display_width, display_height), pg.SRCALPHA)
    pg.draw.circle(background_planet, (150, 100, 100, 30), planet.pos, planet.radius + 60)
    pg.draw.circle(background_planet, (150, 100, 100, 50), planet.pos, planet.radius + 45)
    pg.draw.circle(background_planet, (125, 75, 75, 100), planet.pos, planet.radius + 20)
    pg.draw.circle(background_planet, (100, 50, 50, 150), planet.pos, planet.radius + 8)
    screen.blit(background_planet, (0, 0))
    pg.draw.circle(screen, (255, 230, 230), planet.pos, planet.radius)
    pg.draw.circle(screen, (180, 130, 130), planet.pos, planet.radius - 7)
    pg.draw.circle(screen, planet.color, planet.pos, planet.radius - 18)

    # displaying the tanks.
    tank.display(planet, screen)
    for tanks4 in custom.Tanklist:
        if tanks4.AI == True:
            tanks4.display(planet, screen)


    # deal with bullets
    for bullet in bullets:
        # delete bullets if too far out
        if bullet.pos[0] > display_width * 2 or bullet.pos[0] < - display_width or bullet.pos[1] > display_height * 2 or \
                bullet.pos[1] < - display_height:
            bullets.remove(bullet)
            del bullet
        else:
            # update and display
            # if the bullet is not completely faded in, it does not shoot
            # makes sense since you won't get to point-blank, and you do not want the bullet to explode in the
            # shooting tank itself.
            if pg.time.get_ticks() - bullet.firetime < 200:
                bullet.armed = False
                bullet.surface.set_alpha(100)
            else:
                # Make the bullet appear when it is armed and not under the ground
                bullet.armed = True
                if not bullet.underground:
                    bullet.surface.set_alpha(255)
                    bullet.delete_timer = pg.time.get_ticks()
                else:
                    # stop the bullet
                    # not [0,0] because weird math not written by me (maurizio)
                    bullet.vel = pg.math.Vector2(0.01, 0.01)

                    # let the explosion stay around for a bit
                    if pg.time.get_ticks() - bullet.delete_timer > 100:
                        del bullet
                        continue
            bullet.attraction(planet.pos)
            bullet.move()
            screen.blit(bullet.rotated_surface, bullet.rotated_rect)
            bullet.collision(planet)

    # display the crosshair
    crosshair.pos = pg.mouse.get_pos()
    screen.blit(crosshair.surface, crosshair.surface.get_rect(center=crosshair.pos))

    # make hits visible without killing any of the tanks, by changing the color of the barrel
    if dev_mode == True:
        if AI_tank.ishit == True:
            AI_tank.color = (random.randint(0,255), random.randint(0, 255), random.randint(0, 255))
        if tank.ishit == True:
            tank.color = (random.randint(0,255), random.randint(0, 255), random.randint(0, 255))
        AI_tank.ishit = False
        tank.ishit = False

    # some stuff to visualize variables to debug them, this is not important and can be removed later
    if dev_mode and not len(bullets) == 0:
        AI_tank.cooloff_timer = pg.time.get_ticks()
        if bullets[-1].angle > 0:
            angle3 = np.arctan2(np.sin(bullets[-1].angle)*bullets[-1].vel.length(), np.cos(bullets[-1].angle)*bullets[-1].vel.length()*1.3)
            angle_visualizer = pg.Surface((np.abs(bullets[-1].pos[1] - bullets[-1].Tank.y)/np.sin(angle3), 10), pg.SRCALPHA)
            angle_visualizer.fill(RED)
            angle_visualizer = pg.transform.rotate(angle_visualizer, -angle3 * 180 / np.pi)
            screen.blit(angle_visualizer, bullets[-1].pos)
            #print(angle3)
        surfaceeht = pg.Surface((10, 10))
        surfaceeht.fill(GREEN)
        screen.blit(surfaceeht, bullets[-1].predicted_landing_spot(planet))
        #print(len(bullets))

    pg.display.flip()
    clock.tick(framerate)

pg.quit()


# to do
# main menu
# textures
# health bars
    # a small bar under each tank
# ammo?
# bullet imprecision (random errors)
# multiple ai tanks
# level implementation

# boom sound effect for boom.png and firing and tank hit and tank destroyed

# tank blink on hit for 0.3 seconds to stop tank from taking multiple damage
# make the bullet appear at the end of the barrel
# remove the bullet fading at the beginning, it's kinda pointless
