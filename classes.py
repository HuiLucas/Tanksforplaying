import random

import pygame as pg
import numpy as np

import numba

# constants for the classes
agility_multiplier = 1e-1
movement_dampening = 1.2
dt = 1 / 60  # time step
gravity = 9.80665e9  # 1e10  # gravity for the bullets. IDK why it has to be so absurdly high (real life G is ~10^-11)
immunity_time = 500
Tank_list = []  # list of the tanks
health_bar_size = [60, 5]

pgvec = pg.math.Vector2

# planet class is pretty bare-bones, but it helps a lot with organization
class Planet:
    def __init__(self, pos, radius, color):
        self.pos = pg.math.Vector2(pos)
        self.radius = radius
        self.color = color


# tank class. lots of stuff in here.
class Tank:
    def __init__(self, angle, size, agility, color, boundary_angle, AI, max_health, reload_time):
        self.angle = angle  # where are you on the planet?
        self.angvel = 0  # how fast are you going?
        self.size = size
        self.agility = agility  # how fast can you move?
        self.AI = AI  # stores whether the tank is ai
        self.barrel_angle = 0
        self.barrel_tip = pg.math.Vector2(0, 0)  # this is just for initialization
        self.color = color
        self.invisible_mode = False
        self.cool_off_time = reload_time
        self.cool_off_timer = 0
        self.time_since_last_shot = 10
        self.is_hit = False  # stores whether it is hit
        self.predict_position = 0  # stores the predicted location of its bullet
        self.index_in_Tank_list = len(Tank_list)
        Tank_list.append(self)

        # to make sure the tank doesn't leave the screen
        self.boundary_angle = boundary_angle
        if boundary_angle == -10:  # there are no boundaries, the entire planet is on screen
            self.lower_angle_boundary = -4000 * np.pi
            self.upper_angle_boundary = 4000 * np.pi
        else:
            # the tank cannot go further than the screen
            self.lower_angle_boundary = - np.pi / 2 - boundary_angle
            self.upper_angle_boundary = - np.pi / 2 + boundary_angle

        # the surface for the tank to be drawn on
        self.surface = pg.Surface((60, 40), pg.SRCALPHA, 32)
        # self.surface.set_colorkey((0, 0, 0))  # do NOT remove this line. IDK what it does exactly, but it all turns
        # funny if you delete it. # Sorry but I commented it, I made the background transparent instead
        if self.color == (255, 0, 0):
            tank_image = pg.image.load('Artwork/tankred.png')
        elif self.color == (255, 255, 255):
            tank_image = pg.image.load('Artwork/tankwhite.png')
        else:
            tank_image = pg.image.load('Artwork/tankgreen.png')
        tank_image.convert()
        tank_image = pg.transform.scale_by(tank_image, 0.3)
        tank_image = pg.transform.rotate(tank_image, -90)
        self.surface.blit(tank_image, (35, -3))

        # putting these here for other objects to interact with Tank
        self.x = 0
        self.y = 0
        self.posxy = pg.math.Vector2(self.x, self.y)
        self.vel = pg.math.Vector2([0, 0])

        # AI variables/preferences
        self.wantstoshootnow = False
        # health
        self.max_health = max_health
        self.health = self.max_health
        self.last_hit_time = 0

        # health and reload bar
        self.health_bar = Bar((self.x, self.y), health_bar_size, (255, 0, 0), (0, 255, 0), self.health, self.max_health)
        self.reload_bar = Bar((self.x, self.y + 10), health_bar_size, (255, 255, 255), (80, 80, 80), self.time_since_last_shot, self.cool_off_time)

    def display(self, planet1, scr):  # function to display tank
        # get direction of cannon barrel
        if not self.AI:
            barrel_direction = pg.mouse.get_pos() - pg.math.Vector2(self.x, self.y)
            self.barrel_angle = np.arctan2(barrel_direction[1], barrel_direction[0]) * 180 / np.pi
        else:
            self.barrel_angle = 225

        # create cannon barrel
        cannon = pg.Surface((4, 23), pg.SRCALPHA)
        cannon.fill(self.color)
        cannon = pg.transform.rotate(cannon, -self.barrel_angle - 90)
        cannon_rect = cannon.get_rect()
        if self.barrel_angle >= -90:
            cannon_rect.bottomleft = (25, 25)
        else:
            cannon_rect.bottomright = (25, 25)

        # cannot tip position for shooting bullets
        self.barrel_tip = self.posxy + 23 * pg.math.Vector2(np.cos(np.radians(self.barrel_angle)), np.sin(np.radians(self.barrel_angle)))

        # put everything on its place in a mini surface
        tank_surface_results = self.get_surf(planet1.pos, planet1.radius)
        newtanksurface = pg.Surface((60, 50), pg.SRCALPHA)
        newtanksurface.blit(tank_surface_results[0], (10, 20))
        newtanksurface.blit(cannon, cannon_rect)

        # put the mini surface on the screen
        if self.invisible_mode:
            newtanksurface.set_alpha(50)

        # if tank is destroyed
        if self.health <= 0:
            self.surface.set_alpha(0)
        # if the tank is blinking, so should the barrel
        newtanksurface.set_alpha(self.surface.get_alpha())

        # health bar stuff (at the end to avoid the set_alpha)
        self.health_bar.update(self.health)
        newtanksurface.blit(self.health_bar.surface, self.health_bar.rect)

        self.reload_bar.update(int(np.max((0, np.min((self.cool_off_time, self.time_since_last_shot))))))
        newtanksurface.blit(self.reload_bar.surface, self.reload_bar.rect)

        scr.blit(newtanksurface, tank_surface_results[1].center)

    # this method acts like a sort of update function
    def move(self, movement, current_time):
        self.angvel += self.agility * movement * agility_multiplier * dt
        self.angle += self.angvel * dt

        # dampen the motion
        self.angvel /= movement_dampening

        # it's unreasonable to let angvel go down below 1e-5
        if self.angvel ** 2 < 1e-10:
            self.angvel = 0

        # to make sure the tank doesn't leave the screen
        if self.angle > self.upper_angle_boundary:
            self.angle = self.upper_angle_boundary
        elif self.angle < self.lower_angle_boundary:
            self.angle = self.lower_angle_boundary

        # if the tank is hit, decrease its health
        hit_time = current_time - self.last_hit_time
        if self.is_hit and hit_time > immunity_time and self.health > 0:
            print(f"is hit, health now {self.health}")
            # 0.5 because the bullet hits twice for some reason,
            # i'm too lazy to fix it now
            self.health -= 0.5
            self.is_hit = False
            self.last_hit_time = current_time
        # when hit, the tank flashes
        elif hit_time < immunity_time and self.health > 0:
            if hit_time < immunity_time / 4:
                self.surface.set_alpha(20)
            elif hit_time < 2 * immunity_time / 4:
                self.surface.set_alpha(255)
            elif hit_time < 3 * immunity_time / 4:
                self.surface.set_alpha(20)
            elif hit_time < 4 * immunity_time / 4:
                self.surface.set_alpha(255)

        if self.health <= 0:
            self.cool_off_time = 1e10

        self.posxy = pg.math.Vector2(self.x, self.y)
        self.time_since_last_shot = current_time - self.cool_off_timer

    def AI_move(self, Bulletlist2, planet4, current_time=1e10):
        # only if the tank is AI:
        if self.AI == True:
            # only consider bullets that are still in the air
            Bulletlist = []
            for bullet in Bulletlist2:
                if bullet.underground == False:
                    Bulletlist.append(bullet)
            # if there is one bullet in the air, evade that one:
            if len(Bulletlist) == 1:
                predpos = Bulletlist[-1].predicted_landing_spot(planet4)  # calculate landing spot of bullet
                if np.abs(predpos[0] - self.x) < 100:  # if bullet lands close to tank, move
                    if predpos[0] < self.x:
                        self.move(1, current_time)
                        self.wantstoshootnow = True  # After moving, the tank may shoot

                    else:
                        self.move(-1, current_time)
                        self.wantstoshootnow = True
            # Do the same for the second Bullet in the air if there is one
            elif len(Bulletlist) >= 2:
                predpos = Bulletlist[-2].predicted_landing_spot(planet4)
                if np.abs(predpos[0] - self.x) < 100:
                    if predpos[0] < self.x:
                        self.move(1, current_time)
                        self.wantstoshootnow = True
                    else:
                        self.move(-1, current_time)
                        self.wantstoshootnow = True
            # AI tank shoots using the following code
            if self.wantstoshootnow == True:
                # It shoots only if the timer allows it:
                if pg.time.get_ticks() - self.cool_off_timer > self.cool_off_time:
                    self.cool_off_timer = pg.time.get_ticks()
                    # create a list of the other tanks, and select one of them as a target
                    # list_of_other_tanks = []
                    # for Tankthing in Tank_list:
                    #     list_of_other_tanks.append(Tankthing)
                    # list_of_other_tanks.pop(self.index_in_Tank_list)
                    # randindex = random.randint(0, len(list_of_other_tanks) - 1)
                    # other_tank = list_of_other_tanks[randindex]

                    # i decided to remove the ai tank targets ai tank feature because it makes the game too easy
                    other_tank = Tank_list[0]

                    # this is the target for the bullet:
                    goal = pg.math.Vector2(other_tank.x, other_tank.y) - pg.math.Vector2(self.x, self.y)
                    # come up with an initial guess for the bullet direction
                    if goal[0] < 0:
                        direction = pg.math.Vector2(-300, -300)
                    else:
                        direction = pg.math.Vector2(300, -300)
                    if not goal[0] == 0:
                        if (goal[1] - goal[0] * np.sign(goal[0])) == 0:
                            bullet_speed = 13.4 * np.sqrt(
                                -9.81 * (goal[0]) ** 2 / (goal[1] - goal[0] * np.sign(goal[0]) + 0.01)) - \
                                           goal[1] * 1.2 - 3000 * 1 / goal[0]
                        else:
                            bullet_speed = 13.4 * np.sqrt(
                                -9.81 * (goal[0]) ** 2 / (goal[1] - goal[0] * np.sign(goal[0]))) - \
                                           goal[1] * 1.2 - 3000 * 1 / goal[0]
                    else:
                        if (goal[1] - goal[0] * np.sign(goal[0])) == 0:
                            bullet_speed = 13.4 * np.sqrt(
                                -9.81 * (goal[0]) ** 2 / (goal[1] - goal[0] * np.sign(goal[0]) + 0.01)) - \
                                           goal[1] * 1.2
                        else:
                            bullet_speed = 13.4 * np.sqrt(
                                -9.81 * (goal[0]) ** 2 / (goal[1] - goal[0] * np.sign(goal[0]))) - \
                                           goal[1] * 1.2
                    direction = direction.normalize()
                    # use a negative feedback loop to change the bullet speed, such that it hits the target:
                    deviation = 11
                    i = 0
                    direction_of_shooting = -np.sign(self.x - other_tank.x)
                    while np.abs(deviation) > 10 and i <= 100:
                        # simulate the bullet and find out where it lands:
                        Virtualbullet = Bullet((self.x, self.y), (15, 5), direction * bullet_speed + self.vel, \
                                               (0, 255, 0), pg.time.get_ticks())
                        deviation = \
                        (pg.math.Vector2(other_tank.x, other_tank.y) - Virtualbullet.predicted_landing_spot(planet4))[0]
                        # deviation2 =(pg.math.Vector2(other_tank.x, other_tank.y) - Virtualbullet.predicted_landing_spot(planet4))[1]
                        # bullet_speed += 0.05 * deviation2
                        # change the bullet speed to reduce the deviation. The direction of shooting is there to use
                        # the right sign, depending on what direction it shoots.
                        bullet_speed += 0.05 * deviation * direction_of_shooting
                        i += 1
                    # print(deviation, other_tank.x, other_tank.y, Virtualbullet.predicted_landing_spot(planet4), deviation2)
                    # Launch the bullet with the given bullet_speed and direction
                    Bulletlist2.append(
                        Bullet((self.x, self.y), (15, 5), direction * bullet_speed + self.vel, (0, 255, 0),
                               pg.time.get_ticks()))
                    # Designate the target tank as a property of the bullet
                    # Bulletlist2[-1].Tank = other_tank  # i commented because this .Tank doesn't seem to do anything

                    pg.mixer.Channel(1).play(pg.mixer.Sound("shoot.mp3"))

            self.move(0, current_time)

    def get_surf(self, planet_pos, planet_radius):
        # find the tank's x, y coordinates in terms of its angle and stuff
        self.x = (planet_radius + self.size[1] / 4) * np.cos(self.angle) + planet_pos[0]
        self.y = (planet_radius + self.size[1] / 4) * np.sin(self.angle) + planet_pos[1]
        # useful for others
        self.vel = self.angvel * planet_radius * pg.math.Vector2([-np.sin(self.angle), np.cos(self.angle)])

        # rotate the tank along with the surface it's on
        rotated_surface = pg.transform.rotate(self.surface, -np.degrees(self.angle))
        rotated_rect = rotated_surface.get_rect(center=(self.x - 25, self.y - 38))
        rotated_rect = rotated_rect.scale_by(2, 2)

        return rotated_surface, rotated_rect


# simple class for the crosshair. similar to Planet, it's here only to help with tidiness.
class Crosshairs:
    def __init__(self, pos, size):
        self.pos = pos
        self.size = size

        self.surface = pg.Surface(size)
        self.surface.set_colorkey((0, 0, 0))
        # put the crosshair image
        self.surface.blit(pg.transform.scale(pg.image.load("inverted-crosshair-icon.png"), size), (0, 0))
        # main.py takes care of where to put the crosshair


# the Bullet class has to deal with gravity and collisions (to be added)
class Bullet:
    def __init__(self, pos, size, vel, color, firetime):
        self.pos = pg.math.Vector2(pos)
        self.size = size
        self.vel = pg.math.Vector2(vel)
        self.angle = np.arctan2(self.vel[1], self.vel[0])
        self.acceleration = pg.math.Vector2([0, 0])
        self.firetime = firetime
        self.armed = False  # to make sure that the bullet does not explode directly after launching, it starts off as
        # not armed
        self.underground = False

        self.surface = pg.Surface(size)
        self.surface.set_colorkey((50, 50, 50))
        self.surface.fill(color)

        self.rotated_surface = pg.transform.rotate(self.surface, -np.degrees(self.angle))
        self.rotated_rect = self.rotated_surface.get_rect(center=self.pos)

        # used for a little delay between collision and deletion for the boom
        self.delete_timer = 0

    def move(self):
        # these things are similar to the ones above and should be self-explanatory
        self.pos += self.vel * dt
        self.angle = np.arctan2(self.vel[1], self.vel[0])

        self.rotated_surface = pg.transform.rotate(self.surface, -np.degrees(self.angle))
        self.rotated_rect = self.rotated_surface.get_rect(center=self.pos)

    def attraction(self, planet_pos):
        # newton's law of gravitation, pretty simple stuff
        rel_dist = pg.math.Vector2(planet_pos - self.pos)
        self.acceleration = gravity * rel_dist / rel_dist.magnitude() ** 3
        self.vel += self.acceleration * dt

    def collision(self, planet2):
        # idk why this self.armed exists # RE:The reason is to not activate the bullet when it is still close to the
        # shooting tank, otherwise it would just explode directly after shooting, destroying the shooting tank. Instead,
        # the bullet is armed after a few milliseconds after being launched.
        if self.armed:
            # check for every tank whether it hits it:
            if not len(Tank_list) == 0:
                for tankk in Tank_list:
                    if pg.math.Vector2((tankk.x, tankk.y) - self.pos).length() <= 25:
                        self.boom()
                        tankk.is_hit = True
                        self.underground = True
                    # if it hits the planet
                    if pg.math.Vector2(planet2.pos - self.pos).length() <= planet2.radius:
                        self.boom()
                        self.underground = True

    # just put in the boom image
    def boom(self):
        self.surface = pg.Surface((50, 50))
        self.surface.set_colorkey((50, 50, 50))
        self.surface.fill((255, 0, 0))

        # use image as explosion
        boom_image = pg.image.load("Artwork/boom.png")
        boom_image.convert()
        self.surface.blit(boom_image, (-25, -30))

        pg.mixer.Channel(2).play(pg.mixer.Sound("hq-explosion-6288.mp3"))


    def predicted_landing_spot(self, planet):
        # inititate the initial landing position and velocity. Bit of a workaround with the [0,0] lists, because we cannot use deepcopy
        pos = [0, 0]
        vel = [0, 0]
        pos += self.pos
        vel += self.vel
        time = 0
        rel_dist2 = pg.math.Vector2(planet.pos - pos)
        # as long as the bullet is in the air, simulate the trajectory
        while rel_dist2.magnitude() > planet.radius:
            rel_dist2 = pg.math.Vector2(planet.pos - pos)
            acceleration = gravity * rel_dist2 / rel_dist2.magnitude() ** 3
            vel += acceleration * 1 / 60
            pos += vel * 1 / 60
        return pos  # return the landing spot


# button class includes a bunch of stuff for positioning and color,
# but it does not include any functionality
class Button:
    def __init__(self, center, size, color, text, textcolor, font):
        self.center = pg.math.Vector2(center)
        self.size = pg.math.Vector2(size)
        self.color = color
        self.text = text
        self.textcolor = textcolor
        self.activated = False
        # self.Tank = None  # this doesn't seem to do anything

        self.pos = self.center - self.size / 2
        self.rect = pg.Rect(self.pos, self.size)
        self.text_surf = font.render(self.text, True, self.textcolor)
        self.text_rect = self.text_surf.get_rect(center=self.center)

    # literally checks if the mouse is inside the button Rect
    def is_clicked(self, mouse_pos):
        if self.rect.left < mouse_pos[0] < self.rect.right and self.rect.bottom > mouse_pos[1] > self.rect.top:
            self.activated = True
            return self.activated
        return False


# this Bar class is used for ammo, health.
class Bar:
    def __init__(self, pos, size, color_full, color_empty, value, max_value):
        self.pos = pg.math.Vector2(pos)
        self.size = pg.math.Vector2(size)
        self.color_full = color_full
        self.color_empty = color_empty
        self.value = value
        self.max_value = max_value

        self.surface = pg.Surface(self.size)
        self.rect = pg.Rect(self.pos - self.size / 2, self.size)
        self.surface.fill(self.color_empty)

        self.surface_full = pg.Surface(pg.math.Vector2(self.size[0] * self.value / self.max_value, self.size[1]))
        self.surface_full.fill(self.color_full)
        self.surface.blit(self.surface_full, (0, 0))

    def update(self, value):
        self.value = value

        self.surface = pg.Surface(self.size)
        self.rect = pg.Rect(self.pos, self.size)
        self.surface.fill(self.color_empty)

        self.surface_full = pg.Surface((int(self.size[0] * self.value / self.max_value), self.size[1]))
        self.surface_full.fill(self.color_full)
        self.surface.blit(self.surface_full, (0, 0))
