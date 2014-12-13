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
import os

from attachment import Attachment 
from static_functions import *

class Thruster(Attachment):
    def __init__(self, ref, thruster_keys, r, distx, disty):
        Attachment.__init__(self, ref, r, distx, disty)
        self.sprite = pil_process(os.path.join("images", "thrust.png"))
        self.sprite_r = self.sprite.get_width()/2
        self.sprite_scaling = 1.5
        self.thruster_keys = thruster_keys
        self.repr = "Thruster"
        self.dist = self.dist+self.r*self.sprite_scaling
        
    def draw(self, screen, t_x, t_y, t_ang, t_zoom):
        if self.ref.spawned:
            k = [self.ref.thrusters_on[key] for key in self.thruster_keys]
            t_zoom = t_zoom*self.r/float(self.sprite_r)*self.sprite_scaling
            
            if sum(k) > 0:
                self.derivative = better_rotozoom(self.sprite, t_ang, t_zoom, (0,0))[0]
                #print offsets
                #self.derivative.set_colorkey(Color(ck))
                screen.blit(self.derivative, (t_x-t_zoom*self.sprite_r, t_y-t_zoom*self.sprite_r))