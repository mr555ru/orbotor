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

from quadtree import *

from game_constants import MAX_OBJECTS

class GlobalCollisionDetector():
    
    def __init__(self):
        self.orbitables = []
        self.planet = None
        self.loosening = False
        self.loosening_limit = MAX_OBJECTS
        
    def set_planet(self, planet):
        self.planet=planet
        bounds = QuadTreeBounds()
        bounds.get_from_planet(planet)
        self.quadtree = QuadTree(1, bounds)
        
    def make_priority(self, obj):
        pass
        
    def be_added(self, orbitable):
        self.orbitables.append(orbitable)
        
    def step(self):
        self.loosening = len(self.orbitables) > self.loosening_limit
        #checking = self.orbitables #+ self.priority
        self.quadtree.reinsertlist(self.orbitables)
        for obj1 in self.orbitables:
            if obj1.GCD_REMOVE_ME_FLAG:
                self.orbitables.remove(obj1)
            else:
                if not (self.planet is None):
                    pl_r = (obj1.x-self.planet.x)**2 + (obj1.y-self.planet.y)**2
                    if pl_r < self.planet.r**2:
                        obj1.get_too_close()
                    elif pl_r > (self.planet.r2**2)*2:
                        obj1.way_too_far()
                    elif pl_r > self.planet.r2**2:
                        obj1.get_too_far()
                for obj2 in self.quadtree.retrieve(obj1):
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
