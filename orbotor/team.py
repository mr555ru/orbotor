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

from sputnik import Sputnik


class Team():
    def __init__(self, name, color, participants, spawn, planet):
        self.guys = []
        self.deaths = 0
        self.name = name
        self.planet = planet
        self.color = color
        self.maxfrags = 0
        for i in xrange(participants):
            guy = Sputnik(color,
                          spawn[0] + random.randint(0, 300)-100,
                          spawn[1] + random.randint(0, 600)-300,
                          planet, is_ai=True)
            guy.initialspeed(planet.m, planet.x, planet.y)
            print "%s entered %s team" % (guy.name, self.name)
            self.guys.append(guy)
            
    def objectslist(self):
        objects = []
        for guy in self.guys:
            objects.extend(guy.objectslist())
        return objects

    def set_opponent_team(self, team):
        for guy in self.guys:
            guy.set_opponent_team(team)
    
    def step(self):
        for guy in self.guys:
            if guy.team_notice_dead:
                self.deaths += 1
                # print "%s team %d deaths" % (self.name, self.deaths)
                guy.team_notice_dead = False
            guy.affected(self.planet.m, self.planet.x, self.planet.y)
            guy.step()
            if guy.frags > self.maxfrags:
                self.maxfrags = guy.frags
