#    Orbotor - arcade with orbit mechanics
#    Copyright (C) 2014 mr555ru
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.

import math

import pygame
from pygame import *

from static_functions import *
from gcd import GlobalCollisionDetector
from soundsystem import SoundSystem
import camera, quadtree
                     
GCD_Singleton = GlobalCollisionDetector()
SoundSystem_Singleton = SoundSystem()

class Orbitable(camera.Camerable, quadtree.QuadTreeObject):
    def __init__(self, x, y, r, m, ang=0, dang=0, dx=0, dy=0, nocollidesteps=0, colliding=True):
        global GCD_Singleton
        quadtree.QuadTreeObject.__init__(self)
        camera.Camerable.__init__(self)
        self.x = float(x)
        self.y = float(y)
        self.m = float(m)
        self.r = r
        self.ang = ang
        self.dang = dang
        self.dx = dx
        self.dy = dy
        self.colliding = colliding
        self.repr = "blank"
        GCD_Singleton.be_added(self)
        self.GCD_REMOVE_ME_FLAG = False
        self.sprite = None #Surface
        self.derivative = None
        self.nocollide = nocollidesteps
        self.maxnocollide = nocollidesteps
        
        self.sprite_off_x = 0
        self.sprite_off_y = 0
        
        self.drawdx = 0
        self.drawdy = 0
        self.is_circle = False
        
        self.soundsys = SoundSystem_Singleton
        
    def set_drawdelta(self):
        self.drawdx = self.sprite.get_width()/2
        self.drawdy = self.sprite.get_height()/2
        
           
    def affected(self, mass, x, y):
        R = math.sqrt((x-self.x)**2 + (y-self.y)**2)
        a = G*mass/(R**2)

        ax = a * (x-self.x)/R
        ay = a * (y-self.y)/R

        self.dx += ax
        self.dy += ay

    def initialspeed(self, mass, x, y):
        R = math.sqrt((x-self.x)**2 + (y-self.y)**2)
        aang = math.atan2(-(y-self.y), x-self.x)
        vang = aang+math.pi/2
        v = math.sqrt(G*mass/(R))

        self.dx = v * math.cos(vang)
        self.dy = - v * math.sin(vang)
        
    def focus(self, camera):
        camera.x = self.x
        camera.y = self.y
        camera.ang = self.ang-math.pi/2
        
    def step(self):
        self.x += self.dx
        self.y += self.dy
        self.ang += self.dang
        if self.nocollide > 1:
            self.nocollide -= 1
        elif self.nocollide == 1:
            self.nocollide = 0
            self.colliding = True
        
    def draw(self, screen, t_x, t_y, t_ang, t_zoom):
        self.derivative, offsets = better_rotozoom(self.sprite, t_ang, t_zoom, (self.sprite_off_x, self.sprite_off_y), self.is_circle)
        screen.blit(self.derivative, (t_x-self.drawdx*t_zoom-offsets[0], t_y-self.drawdy*t_zoom-offsets[1]))
        
        
        
    
    def get_collision(self, other, vel, ang):
        self.dx += other.m/float(self.m) * vel * math.cos(ang)
        self.dy += other.m/float(self.m) * vel * math.sin(ang)

    def get_too_close(self):
        pass

    def get_too_far(self):
        pass
    
    def way_too_far(self):
        self.exclude()

    def exclude(self):
        self.colliding = False
        self.GCD_REMOVE_ME_FLAG = True