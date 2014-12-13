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

import random

from helldebris import HellDebris

from orbitable import GCD_Singleton

class HellDebrisCollection():
    def __init__(self, players_spawn, planet, min=6, max=20):
        self.debris = []
        self.planet = planet
        self.spawn = (-players_spawn[0], players_spawn[1])
        self.max = max
        self.min = min
        self.generate()

    def generate(self):
        cnt = random.randint(0,self.max-self.min)
        #print "%d pieces of hell generated" % cnt
        for i in xrange(cnt):
            d = HellDebris(self.spawn[0] + random.randint(0,300)-150, self.spawn[1] + random.randint(0,100)-50, 0, 0)
            d.initialspeed(self.planet.m, self.planet.x, self.planet.y)
            self.debris.append(d)

    def objectslist(self):
        return self.debris

    def step(self):
        for d in self.debris:
            if d.GCD_REMOVE_ME_FLAG:
                self.debris.remove(d)
            while len(d.children) > 0:
                chichild = d.children.pop()
                self.debris.append(chichild)
            d.affected(self.planet.m, self.planet.x, self.planet.y)
            d.step()
        if len(self.debris) <= self.min and not GCD_Singleton.loosening:
            if random.randint(0, 220) == 0:
                self.generate()