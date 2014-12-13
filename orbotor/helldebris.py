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

from debris import Debris, Spark
from static_functions import *
from orbitable import Orbitable, GCD_Singleton

helldebris_sprites = [imitate_debris(HELLDEBRIS_COLORS[0], HELLDEBRIS_COLORS[1], int(DEBRIS_R*DEBRIS_SCALING)) for i in xrange(30)]

class HellDebris(Debris):
    
    def __init__(self, x, y, dx, dy):
         Debris.__init__(self, x, y, dx, dy)
         self.sprite = random.choice(helldebris_sprites)
    
    def initialspeed(self, mass, x, y):
        R = math.sqrt((x-self.x)**2 + (y-self.y)**2)
        aang = math.atan2(-(y-self.y), x-self.x)
        vang = aang-math.pi/2
        v = math.sqrt(G*mass/(R))

        self.dx = v * math.cos(vang) + (random.randint(0,40)-20)/80.0
        self.dy = - v * math.sin(vang) + (random.randint(0,40)-20)/80.0

    def get_collision(self, other, vel, ang):
        if other.repr != "Spark" not GCD_Singleton.loosening:
            if random.randint(0,2) == 0:
                m = 0
                for i in xrange(random.randint(2, 4)):
                    m += 5
                    self.children.append(HellDebris(self.x, self.y, self.dx, self.dy))
                for i in xrange(random.randint(0,3)):
                    self.children.append(Spark(self.x, self.y, self.dx, self.dy, vel*other.m, ang))
                self.m = m
                Orbitable.get_collision(self, other, vel, ang)
            self.destroy()