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

from camera import Camerable
from static_functions import *


class Attachment(Camerable):
    def __init__(self, ref, r, distx, disty):
        Camerable.__init__(self)
        self.ref = ref
        self.r = r
        
        self.dist = math.sqrt(distx**2 + disty**2)
        
        self.att_ang = math.atan2(-disty, distx)
        
        # self.upd()
        
        self.sprite = None  # Surface
        self.derivative = None
        
    def upd(self):
        self.ang = self.att_ang+self.ref.ang
        self.x = self.ref.x+self.dist*math.cos(self.ang)
        self.y = self.ref.y+self.dist*math.sin(self.ang)
        
    def draw(self, screen, t_x, t_y, t_ang, t_zoom):
        if self.ref.spawned:
            self.derivative = pygame.transform.rotozoom(self.sprite, t_ang, t_zoom)
            # self.derivative.set_colorkey(Color(ck))
            screen.blit(self.derivative, (t_x-self.r*t_zoom, t_y-self.r*t_zoom))

    def step(self):
        pass
