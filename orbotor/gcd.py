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

class GlobalCollisionDetector():
    
    def __init__(self):
        self.orbitables = []
        self.planet = None
        self.loosening = False
        self.loosening_value = 0
        self.priority = []
        self.loosening_strength = 0
        
    def make_priority(self, obj):
        self.orbitables.remove(obj)
        self.priority.append(obj)
        
    def be_added(self, orbitable):
        self.orbitables.append(orbitable)
        
    def step(self):
        self.loosening = len(self.orbitables) > 100
        self.loosening_strength = len(self.orbitables) % 100 + 1
        if self.loosening:
            self.loosening_value = (self.loosening_value + 1) % self.loosening_strength
        checking = self.orbitables[self.loosening_value if self.loosening else 0::self.loosening_strength if self.loosening else 1]+ self.priority
        for obj1 in checking:
            if obj1.GCD_REMOVE_ME_FLAG:
                if obj1 not in self.priority:
                    self.orbitables.remove(obj1)
                else:
                    self.priority.remove(obj1)
            else:
                if not (self.planet is None):
                    pl_r = (obj1.x-self.planet.x)**2 + (obj1.y-self.planet.y)**2
                    if pl_r < self.planet.r**2:
                        obj1.get_too_close()
                    elif pl_r > (self.planet.r2**2)*2:
                        obj1.way_too_far()
                    elif pl_r > self.planet.r2**2:
                        obj1.get_too_far()
                for obj2 in checking:
                    if not (obj1 is obj2) and obj1.colliding and obj2.colliding:
                        r = (obj1.x-obj2.x)**2+(obj1.y-obj2.y)**2
                        minr = (obj1.r + obj2.r)**2
                        #print "%f <= %f" % (r, minr)
                        if r <= minr:
                            #Collision!
                            
                            vel = abs(math.sqrt((obj2.dx-obj1.dx)**2 + (obj2.dy-obj1.dy)**2))
                            ang = math.atan2(obj2.dy-obj1.dy, obj2.dx-obj1.dx)
                            obj1.get_collision(obj2, vel, ang)
                            obj2.get_collision(obj1, vel, ang-math.pi)