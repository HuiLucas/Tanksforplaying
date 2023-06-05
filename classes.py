import pygame as pg
import numpy as np

# constants for the classes
agility_multiplier = 1e-1
movement_dampening = 1.2
dt = 0.02  # time step
gravity = 1e10  # gravity for the bullets. IDK why it has to be so absurdly high (real life G is ~10^-11)


# planet class is pretty bare-bones, but it helps a lot with organization
class Planet:
    def __init__(self, pos, radius, color):
        self.pos = pg.math.Vector2(pos)
        self.radius = radius
        self.color = color



# tank class. lots of stuff in here. should probably be renamed to Tank,
# since I'm planning on including the tank gun in this class as well.
class TankBody:
    def __init__(self, angle, size, agility, color, boundary_angle, AI):
        self.angle = angle
        self.angvel = 0
        self.size = size
        self.agility = agility
        self.AI = AI
        self.barrel_angle = 0
        self.color = color
        self.invisible_mode = False
        self.cool_off_time = 0
        self.cooloff_timer = 0

        # to make sure the tank doesn't leave the screen
        self.boundary_angle = boundary_angle
        if boundary_angle == -10:  # there are no boundaries, the entire planet is on screen
            self.lower_angle_boundary = -4 * np.pi
            self.upper_angle_boundary = 4 * np.pi
        else:
            # the tank cannot go further than the screen
            self.lower_angle_boundary = - np.pi / 2 - boundary_angle
            self.upper_angle_boundary = - np.pi / 2 + boundary_angle

        # the surface for the tank to be drawn on
        self.surface = pg.Surface((60,40), pg.SRCALPHA, 32)
        #self.surface.set_colorkey((0, 0, 0))  # do NOT remove this line. IDK what it does exactly, but it all turns
        # funny if you delete it. # Sorry but I commented it, I made the background transparent instead
        if self.color == (255, 0, 0):
            tankimage = pg.image.load('Artwork/tankred.png')
        elif self.color == (255, 255, 255):
            tankimage = pg.image.load('Artwork/tankwhite.png')
        else:
            tankimage = pg.image.load('Artwork/tankgreen.png')
        tankimage.convert()
        tankimage = pg.transform.scale_by(tankimage, 0.3)
        tankimage = pg.transform.rotate(tankimage, -90)
        self.surface.blit(tankimage, (35, -3))


        # putting these here for other objects to interact with TankBody
        self.x = 0
        self.y = 0
        self.vel = pg.math.Vector2([0, 0])

        # AI variables/preferences
        self.wantstoshootnow = False

    def display(self, planet1, scr): #function to display tank
        # get direction of cannon barrel
        barrel_direction = pg.mouse.get_pos() - pg.math.Vector2(self.x, self.y)
        self.barrel_angle = np.arctan2(barrel_direction[1], barrel_direction[0]) * 180 /np.pi

        # create cannon barrel
        cannon = pg.Surface((4, 23), pg.SRCALPHA)
        cannon.fill((0, 0, 0))
        cannon = pg.transform.rotate(cannon, -self.barrel_angle - 90)
        cannon_rect = cannon.get_rect()
        if self.barrel_angle >= -90:
            cannon_rect.bottomleft = (25, 25)
        else:
            cannon_rect.bottomright = (25, 25)

        # put everything on its place in a mini surface
        tank_surface_results = self.get_surf(planet1.pos, planet1.radius)
        newtanksurface = pg.Surface((60, 50), pg.SRCALPHA)
        newtanksurface.blit(tank_surface_results[0], (10, 20))
        newtanksurface.blit(cannon, cannon_rect)

        # put the mini surface on the screen
        if self.invisible_mode == True:
            newtanksurface.set_alpha(50)
        scr.blit(newtanksurface, tank_surface_results[1].center)

    def move(self, movement=0):
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

    def AI_move(self):
        # insert AI code here
        if self.AI == True:
            if self.wantstoshootnow == True:
                # shoot
                print("pew!")
            else:
                # move in the best direction
                self.move(0)

    def get_surf(self, planet_pos, planet_radius):
        # find the tank's x, y coordinates in terms of its angle and stuff
        self.x = (planet_radius + self.size[1] / 4) * np.cos(self.angle) + planet_pos[0]
        self.y = (planet_radius + self.size[1] / 4) * np.sin(self.angle) + planet_pos[1]
        # useful for others
        self.vel = self.angvel * planet_radius * pg.math.Vector2([-np.sin(self.angle), np.cos(self.angle)])

        # rotate the tank along with the surface it's on
        rotated_surface = pg.transform.rotate(self.surface, -np.degrees(self.angle))
        rotated_rect = rotated_surface.get_rect(center=(self.x - 25, self.y - 38))
        rotated_rect = rotated_rect.scale_by(2)

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
    def __init__(self, pos, size, vel, color):
        self.pos = pg.math.Vector2(pos)
        self.size = size
        self.vel = pg.math.Vector2(vel)
        self.angle = np.arctan2(self.vel[1], self.vel[0])
        self.acceleration = pg.math.Vector2([0, 0])

        self.surface = pg.Surface(size)
        self.surface.set_colorkey((50, 50, 50))
        self.surface.fill(color)

        self.rotated_surface = pg.transform.rotate(self.surface, -np.degrees(self.angle))
        self.rotated_rect = self.rotated_surface.get_rect(center=self.pos)

    def move(self):
        # these things are similar to the ones above and should be self explanatory
        self.pos += self.vel * dt
        self.angle = np.arctan2(self.vel[1], self.vel[0])

        self.rotated_surface = pg.transform.rotate(self.surface, -np.degrees(self.angle))
        self.rotated_rect = self.rotated_surface.get_rect(center=self.pos)

    def attraction(self, planet_pos):
        # newton's law of gravitation, pretty simple stuff
        rel_dist = pg.math.Vector2(planet_pos - self.pos)
        self.acceleration = gravity * rel_dist / rel_dist.magnitude() ** 3
        self.vel += self.acceleration * dt
