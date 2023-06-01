import pygame as pg
import numpy as np

# constants for the classes
agility_multiplier = 1e-4
movement_dampening = 1.2


class Planet:
    def __init__(self, pos, radius, color):
        self.pos = pg.math.Vector2(pos)
        self.radius = radius
        self.color = color


class TankBody:
    def __init__(self, angle, size, agility, color, boundary_angle):
        self.angle = angle
        self.angvel = 0
        self.size = size
        self.agility = agility

        # to make sure the tank doesn't leave the screen
        self.boundary_angle = boundary_angle
        if boundary_angle == -10: # there are no boundaries, the entire planet is on screen
            self.lower_angle_boundary = -4 * np.pi
            self.upper_angle_boundary = 4 * np.pi
        else:
            self.lower_angle_boundary = - np.pi / 2 - boundary_angle
            self.upper_angle_boundary = - np.pi / 2 + boundary_angle

        self.surface = pg.Surface(size)
        self.surface.set_colorkey((0, 0, 0))
        self.surface.fill(color)
        # you can add an image here of the tank body, just blit an pg.image.load over the surface

        # putting these here for other objects to interact with TankBody
        self.x = 0
        self.y = 0

    def move(self, movement=0):
        self.angvel += self.agility * movement * agility_multiplier
        self.angle += self.angvel

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

    def get_surf(self, planet_pos, planet_radius):
        self.x = (planet_radius + self.size[1] / 4) * np.cos(self.angle) + planet_pos[0]
        self.y = (planet_radius + self.size[1] / 4) * np.sin(self.angle) + planet_pos[1]

        rotated_surface = pg.transform.rotate(self.surface, -np.degrees(self.angle))
        rotated_rect = rotated_surface.get_rect(center=(self.x, self.y))

        return rotated_surface, rotated_rect


class Crosshairs:
    def __init__(self, pos, size):
        self.pos = pos
        self.size = size

        self.surface = pg.Surface(size)
        self.surface.set_colorkey((0, 0, 0))
        # put the crosshair image
        self.surface.blit(pg.transform.scale(pg.image.load("inverted-crosshair-icon.png"), size), (0, 0))
