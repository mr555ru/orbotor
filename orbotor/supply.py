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

from debris import Debris 
from static_functions import *

class FuelSupply(Debris):
    
    def __init__(self, x, y, dx, dy):
         Debris.__init__(self, x, y, dx, dy)
         self.r = 4
         self.sprite = create_color_circle(Color("#B09050"), self.r*self.scaling)
         self.repr = "FuelSupply"
         self.m = 16*FUEL_MASS
         self.is_circle = True
         
    def get_collision(self, other, vel, ang):
        if other.repr == "Sputnik":
            if other.spawned:
                if vel < 2:
                    other.refuel()
                    #print "Bless you with fuel!"
                else:
                    other.destroy(reason=self.repr)
        self.destroy()
        
class AmmoSupply(Debris):
    
    def __init__(self, x, y, dx, dy):
         Debris.__init__(self, x, y, dx, dy)
         self.r = 4
         self.sprite = create_color_circle(Color("#44DDDD"), self.r*self.scaling)
         self.repr = "AmmoSupply"
         self.m = 16*BULLET_MASS
         self.is_circle = True
         
    def get_collision(self, other, vel, ang):
        if other.repr == "Sputnik":
            if other.spawned:
                if vel < 2:
                    other.reload()
                    #print "Bless you with ammo!"
                else:
                    other.destroy(reason=self.repr)
        self.destroy()