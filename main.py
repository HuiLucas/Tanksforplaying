# only allowed to use: pygame, matplotlib, numpy, numba
import random

import pygame as pg
import numpy as np

import classes as custom

# set up constants
display_height = 700
display_width = 1200
cool_off_time = 800  # minimum time between shots (in ms)
bullet_speed = 1200
end_level = 10

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
pg.mixer.init()
pg.display.set_caption("Tanks for Playing!")
clock = pg.time.Clock()
screen = pg.display.set_mode((display_width, display_height), pg.DOUBLEBUF)
pg.display.set_icon(pg.image.load("Glyphish-Glyphish-23-bird.32.png"))


# font (for writing, obvs)
pg.font.init()
font1 = pg.font.SysFont("Comic Sans MS", 45)
font2 = pg.font.SysFont("Comic Sans MS", 90)

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
    boundary_angle = np.arcsin(display_width / (2 * planet.radius)) - np.pi/200
else:
    boundary_angle = -10  # -10 is an impossible value, so it's recognizable


menu_running = True # is the menu screen running
dev_mode = False

# buttons
play_button = custom.Button([display_width/2, display_height/4], [300, 100], WHITE, "Play", BLACK, font1)
controls_button = custom.Button([display_width/2, display_height/4*2], [300, 100], WHITE, "How to play", BLACK, font1)
exit_button = custom.Button([display_width/2, display_height/4*3], [300, 100], WHITE, "Exit", BLACK, font1)
# dev_mode_button = custom.Button([display_width/2 + 400, display_height/4*3], [300, 100], WHITE, "Dev Mode", BLACK, font1)
infinite_mode_button = custom.Button([display_width/2 - 400, display_height/4*3], [300, 100], WHITE, "Infinite Mode", BLACK, font1)

restart_button = custom.Button([display_width/2, display_height/4*2], [300, 100], WHITE, "Restart", BLACK, font1)

upgrade_hull_button = custom.Button([display_width/2, display_height/5*2], [300, 100], WHITE, "HULL", BLACK, font1)
upgrade_gun_button = custom.Button([display_width/2, display_height/5*3], [300, 100], WHITE, "GUN", BLACK, font1)
upgrade_engine_button = custom.Button([display_width/2, display_height/5*4], [300, 100], WHITE, "ENGINE", BLACK, font1)


pg.mixer.music.load("epic-dramatic-action-trailer-99525.mp3")
pg.mixer.music.play()
# ================== MAIN MENU ==================
show_how_to_play = False
howtoplay_timer = pg.time.get_ticks()  # these are here because i'm rushing and i can't think of a better way
while menu_running:
    pg.event.pump()

    for event in pg.event.get():
        if event.type == pg.QUIT:
            running = False
            menu_running = False
            pg.quit()

    # press escape to quickly quit the game
    keys = pg.key.get_pressed()
    if keys[pg.K_ESCAPE]:
        running = False
        menu_running = False
        break
    screen.fill(BLACK)

    howtoplayimage = pg.image.load("Artwork/war-and-army-tank-wallpaper-preview.jpg")
    howtoplayimage.convert()
    howtoplayimage = pg.transform.scale(howtoplayimage, (display_width, display_height))
    screen.blit(howtoplayimage, howtoplayimage.get_rect(center=(display_width / 2, display_height / 2)))

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
    pg.draw.rect(screen, infinite_mode_button.color, infinite_mode_button.rect)
    screen.blit(infinite_mode_button.text_surf, infinite_mode_button.text_rect)

    # get mouse click
    if pg.mouse.get_pressed()[0]:
        # buttons
        mouse_pos = pg.mouse.get_pos()
        # print("AAAAAAAAAAA")

        # check if mouse click is in play button
        if play_button.is_clicked(mouse_pos) and (not show_how_to_play) and pg.time.get_ticks() - howtoplay_timer > 500:
            menu_running = False
            running = True
            break

        # check if mouse click is in howtoplay button
        if controls_button.is_clicked(mouse_pos) and (not show_how_to_play) and pg.time.get_ticks() - howtoplay_timer > 500:
            howtoplay_timer = pg.time.get_ticks()
            show_how_to_play = True

        # check if mouse click is in exit button
        if exit_button.is_clicked(mouse_pos) and (not show_how_to_play) and pg.time.get_ticks() - howtoplay_timer > 500:
            pg.quit()
            running = False
            menu_running = False
            break

        # check if mouse click is in dev mode button
        if infinite_mode_button.is_clicked(mouse_pos) and (not show_how_to_play) and pg.time.get_ticks() - howtoplay_timer > 500:
            menu_running = False
            running = True
            end_level = 100
            break

    if show_how_to_play:
        howtoplayimage = pg.image.load("howtoplay.png")
        howtoplayimage.convert()
        howtoplayimage = pg.transform.scale(howtoplayimage, (display_width, display_height))
        screen.blit(howtoplayimage, howtoplayimage.get_rect(center=(display_width/2, display_height/2)))

        if pg.time.get_ticks() - howtoplay_timer > 500:
            if pg.mouse.get_pressed()[0]:
                show_how_to_play = False
                howtoplay_timer = pg.time.get_ticks()

    pg.display.flip()
    clock.tick(framerate)

# =========================== ACTUAL GAME ===============================

pg.mixer.music.load("metal-dark-matter-111451.mp3")
pg.mixer.music.play(1000)
pg.mixer.music.set_volume(0.4)

pg.mixer.Channel(2).set_volume(0.3)  # channel 2 is for bullet explosions, they're way too loud

# player tank stat modifiers (upgradeable)
player_hull = 1
player_gun = 1
player_engine = 1

running = True  # is the main program itself running
have_to_restart = False
next_level = True
# level implementation. there are 10 levels, each level one more enemy appears
level = 1
while next_level <= end_level + 1:

    if not running:
        break
    if have_to_restart:
        print("Had to restart")
        have_to_restart = False
        level = 1
        player_gun = 1
        player_engine = 1
        player_hull = 1
    print(f"Next level, now at level {level}")

    # create the tanks
    custom.Tank_list = []

    player_tank = custom.Tank(-np.pi / 2 - 0.2, (20, 30), 8 * player_engine, RED, boundary_angle, False, 5 * player_hull, cool_off_time * player_gun)
    # AI tank list
    AI_tank_list = np.empty(0)
    print(level)
    for i in range(level):
        AI_tank_list = np.append(AI_tank_list, [custom.Tank(-np.pi / 2 + random.random()/3, (20, 30), 8, WHITE, boundary_angle, True, 5, cool_off_time)])
    # AI_tank = custom.Tank(-np.pi / 2 + 0.1, (20, 30), 8, WHITE, boundary_angle, True, 5, cool_off_time)
    # AI_tank2 = custom.Tank(-np.pi / 2 +0.3, (20, 30), 8, GREEN, boundary_angle, True, 5, cool_off_time)
    # AI_tank3 = custom.Tank(-np.pi / 2, (20, 30), 8, GREEN, boundary_angle, True, 5, cool_off_time)
    # AI_tank4 = custom.Tank(-np.pi / 2 +0.2, (20, 30), 8, GREEN, boundary_angle, True, 5, cool_off_time)

    # create the crosshair
    crosshair = custom.Crosshairs((0, 0), (50, 50))

    # list containing all the bullets, because we're going to have quite a lot of them
    bullets = []

    # start the cool-off timer
    player_tank.cool_off_timer = pg.time.get_ticks()
    for Tanks2 in custom.Tank_list:
        if Tanks2.AI:
            Tanks2.cool_off_timer = pg.time.get_ticks() + 2000

    level_won = False

    while running:
        pg.event.pump()

        # event listening. quitting and shooting.
        for event in pg.event.get():
            if event.type == pg.QUIT:
                running = False
                break

            # shoot the bullet
            if pg.mouse.get_pressed()[0]:
                if pg.time.get_ticks() - player_tank.cool_off_timer > player_tank.cool_off_time:
                    # reset the cool off timer
                    player_tank.cool_off_timer = pg.time.get_ticks()

                    pg.mixer.Channel(0).play(pg.mixer.Sound("shoot.mp3"))

                    # find direction to shoot
                    direction = pg.mouse.get_pos() - pg.math.Vector2(player_tank.x, player_tank.y)
                    bullet_speed = 50 * np.sqrt(np.linalg.norm(direction))
                    direction = direction.normalize()

                    bullet_direction = pg.math.Vector2(player_tank.posxy) + pg.math.Vector2(5, -15) + 23 * pg.math.Vector2(np.cos(np.radians(player_tank.barrel_angle)), np.sin(np.radians(player_tank.barrel_angle)))
                    # print(str(bullet_direction))
                    # create a bullet with init velocity and direction
                    bullets.append(custom.Bullet(bullet_direction, (15, 5), direction * bullet_speed + player_tank.vel, GREEN,
                                                 pg.time.get_ticks()))
                    # bullets[-1].Tank = AI_tank  # this doesn't seem to do anything so i commented it

        screen.fill(BLACK)
        screen.blit(background, background_rect)

        # press escape to close the game
        keys = pg.key.get_pressed()
        if keys[pg.K_ESCAPE]:
            running = False
            break

        # move the tank (1 is right, -1 is left. don't change these, they act like booleans)
        if keys[pg.K_RIGHT]:
            # screen.blit(font1.render("Right arrow key pressed", False, WHITE), (100, 100))
            player_tank.move(1, pg.time.get_ticks())
            # player_tank.cool_off_timer = pg.time.get_ticks()  # i commented this because i don't want the player to not
            # be able to shoot while moving.
        elif keys[pg.K_LEFT]:
            # screen.blit(font1.render("Left arrow key pressed", False, WHITE), (100, 100))
            player_tank.move(-1, pg.time.get_ticks())
            # player_tank.cool_off_timer = pg.time.get_ticks()  # i commented this because i don't want the player to not
            # be able to shoot while moving.
        else:
            player_tank.move(0, pg.time.get_ticks())

        # move AI Tanks
        for tanks3 in custom.Tank_list:
            if tanks3.AI:
                tanks3.AI_move(bullets, planet, pg.time.get_ticks())

        # If development mode is on, use an indicator to know where the bullet is predicted to hit
        if dev_mode:
            screen.blit(font1.render("wheh", False, WHITE), (AI_tank.predict_position, 200))

            # text with misc content for debugging
            if pg.time.get_ticks() - player_tank.cool_off_timer >= player_tank.cool_off_time:
                screen.blit(font1.render(str(pg.time.get_ticks() - player_tank.cool_off_timer), False, GREEN), (200, 250))
            else:
                screen.blit(font1.render(str(pg.time.get_ticks() - player_tank.cool_off_timer), False, RED), (200, 250))

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
        player_tank.display(planet, screen)
        for tanks4 in custom.Tank_list:
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

        # display level number
        screen.blit(font1.render(f"Level {level}", False, (200, 200, 200)), (0, 0))

        # make hits visible without killing any of the tanks, by changing the color of the barrel
        if dev_mode == True:
            for AI_tank in AI_tank_list:
                if AI_tank.is_hit == True:
                    AI_tank.color = (random.randint(0,255), random.randint(0, 255), random.randint(0, 255))
                if player_tank.is_hit == True:
                    player_tank.color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
                AI_tank.is_hit = False
                player_tank.is_hit = False

        # some stuff to visualize variables to debug them, this is not important and can be removed later
        if dev_mode and not len(bullets) == 0:
            AI_tank.cool_off_timer = pg.time.get_ticks()
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

        # check if player tank is destroyed. if yes, show some game over text and restart and quit buttons.
        if player_tank.health <= 0:
            game_over_text = font2.render("GAME OVER! :(", False, WHITE)
            screen.blit(game_over_text, (display_width/2 - game_over_text.get_width()/2, 100))
            for AI_tank in AI_tank_list:
                AI_tank.cool_off_timer = 1e10

            # exit button
            pg.draw.rect(screen, exit_button.color, exit_button.rect)
            screen.blit(exit_button.text_surf, exit_button.text_rect)
            # restart button
            pg.draw.rect(screen, restart_button.color, restart_button.rect)
            screen.blit(restart_button.text_surf, restart_button.text_rect)

            # get mouse click
            if pg.mouse.get_pressed()[0]:
                # buttons
                mouse_pos = pg.mouse.get_pos()

                # check if mouse click is in exit button
                if exit_button.is_clicked(mouse_pos):
                    pg.quit()
                    running = False
                    menu_running = False
                    break

                # check if mouse click is in play button
                if restart_button.is_clicked(mouse_pos):
                    level = 1
                    have_to_restart = True
                    break

        level_won_check = True
        # for tank in ai tanks: if they're not destroyed, level won check = false
        for AI_Tank in AI_tank_list:
            if AI_Tank.health > 0:
                level_won_check = False

        if level_won_check and player_tank.health > 0:
            if level > end_level:
                break
            # the level has been won, time for upgrades
            level_won_text = font2.render("LEVEL WON!", False, WHITE)
            screen.blit(level_won_text, (display_width/2 - level_won_text.get_width()/2, 50))

            choose_upgrade_text = font1.render("Choose upgrade:", False, WHITE)
            screen.blit(choose_upgrade_text, (display_width / 2 - choose_upgrade_text.get_width() / 2, 150))

            # upgrade hull button
            pg.draw.rect(screen, upgrade_hull_button.color, upgrade_hull_button.rect)
            screen.blit(upgrade_hull_button.text_surf, upgrade_hull_button.text_rect)

            # upgrade gun button
            pg.draw.rect(screen, upgrade_gun_button.color, upgrade_gun_button.rect)
            screen.blit(upgrade_gun_button.text_surf, upgrade_gun_button.text_rect)

            # upgrade engine button
            pg.draw.rect(screen, upgrade_engine_button.color, upgrade_engine_button.rect)
            screen.blit(upgrade_engine_button.text_surf, upgrade_engine_button.text_rect)

            # get mouse click
            if pg.mouse.get_pressed()[0]:
                # buttons
                mouse_pos = pg.mouse.get_pos()

                # check if mouse click is in exit button
                if upgrade_hull_button.is_clicked(mouse_pos):
                    player_hull *= 1.5
                    break

                # check if mouse click is in play button
                if upgrade_gun_button.is_clicked(mouse_pos):
                    player_gun /= 1.5
                    break

                # check if mouse click is in play button
                if upgrade_engine_button.is_clicked(mouse_pos):
                    player_engine *= 1.5
                    break


        pg.display.flip()
        clock.tick(framerate)

    won_time = pg.time.get_ticks()

    if level > end_level and running:
        # game won
        print("game won")
        end_screen_running = True
        while end_screen_running:
            pg.event.pump()

            for event in pg.event.get():
                if event.type == pg.QUIT:
                    running = False
                    end_screen_running = False
                    pg.quit()
                    menu_running = False

            # press escape to quickly quit the game
            keys = pg.key.get_pressed()
            if keys[pg.K_ESCAPE]:
                running = False
                menu_running = False
                break
            screen.fill(BLACK)

            howtoplayimage = pg.image.load("Artwork/fires_artifice_fireworks_colorful_feast_new_year's_eve_fair_night-1115992.jpeg")
            howtoplayimage.convert()
            howtoplayimage = pg.transform.scale(howtoplayimage, (display_width, display_height))
            screen.blit(howtoplayimage, howtoplayimage.get_rect(center=(display_width / 2, display_height / 2)))

            # display buttons
            # restart button
            pg.draw.rect(screen, restart_button.color, restart_button.rect)
            screen.blit(restart_button.text_surf, restart_button.text_rect)
            # exit button
            pg.draw.rect(screen, exit_button.color, exit_button.rect)
            screen.blit(exit_button.text_surf, exit_button.text_rect)

            # get mouse click
            if pg.mouse.get_pressed()[0] and pg.time.get_ticks() - won_time > 1000:
                # buttons
                mouse_pos = pg.mouse.get_pos()
                # print("AAAAAAAAAAA")

                # check if mouse click is in play button
                if restart_button.is_clicked(mouse_pos):
                    end_screen_running = False
                    running = True
                    have_to_restart = True
                    break

                # check if mouse click is in exit button
                if exit_button.is_clicked(mouse_pos):
                    pg.quit()
                    running = False
                    menu_running = False
                    break

            level_won_text = font2.render("YOU WON THE GAME!", False, WHITE)
            screen.blit(level_won_text, (display_width / 2 - level_won_text.get_width() / 2, 50))

            pg.display.flip()
            clock.tick(framerate)

    level += 1

pg.quit()


# to do
# level implementation
