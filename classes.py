import pygame as pg
import numpy as np
import pygame.math

# constants for the classes
agility_multiplier = 1e-4
movement_dampening = 1.2

class Planet:
    def __init__(self, pos, radius, color):
        self.pos = pg.math.Vector2(pos)
        self.radius = radius
        self.color = color

class TankBody:
    def __init__(self, angle, size, agility, color):
        self.angle = angle
        self.angvel = 0
        self.size = size
        self.agility = agility

        self.surface = pg.Surface(size)
        self.surface.set_colorkey((0, 0, 0))
        self.surface.fill(color)

        # putting these here for other objects to interact with TankBody
        self.x = 0
        self.y = 0

    def move(self, movement=0):
        self.angvel += self.agility * movement * agility_multiplier
        self.angle += self.angvel

        # dampen the motion
        self.angvel /= movement_dampening

        # it's unreasonable to let angvel go down below 1e-5
        if self.angvel**2 < 1e-10:
            self.angvel = 0

    def get_surf(self, planet_pos, planet_radius):
        self.x = (planet_radius + self.size[1]/4) * np.cos(self.angle) + planet_pos[0]
        self.y = (planet_radius + self.size[1]/4) * np.sin(self.angle) + planet_pos[1]

        rotated_surface = pg.transform.rotate(self.surface, -np.degrees(self.angle))
        rotated_rect = rotated_surface.get_rect(center=(self.x, self.y))

        return rotated_surface, rotated_rect
