# -*- coding: utf-8 -*-
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

from orbitable import SoundSystem_Singleton

from game_constants import STATS_FONT

class SimpleStats():
    def __init__(self, team1, team2, player):
        self.team1 = team1
        self.team2 = team2
        self.player = player

        self.font = pygame.font.Font(STATS_FONT, 18)
        
        self.bg = Surface((350,160), flags=SRCALPHA)
        
        self.soundsys = SoundSystem_Singleton
        
        self.soundsys.initsound('warn','warning.wav')


    def draw(self, screen):
        string1 = "%s: %d" % (self.team1.name, self.team2.deaths)
        string2 = "%s: %d" % (self.team2.name, self.team1.deaths)
        string3 = "You: %d frags, %d deaths" % (self.player.frags, self.player.deaths)
        string4 = "Fuel: %.4f, ammo %d, mass %.2f" % (self.player.fuel, self.player.ammo, self.player.m)
        if self.player.spawned:
            string5 = "Alive for %.2fs, record %.2fs" % ((pygame.time.get_ticks() - self.player.spawntime)/1000.0, self.player.max_alive/1000.0)
            string6 = "peri %d, apo %d, now %d, ano %d" % (self.player.peri, self.player.apo, self.player.height, math.degrees(self.player.anomaly))
            string6 += "º"[1]
            if self.player.apo >= self.player.planet.r2:
                string7 = "     WARNING: ORBIT TOO HIGH!"
                sprite7 = self.font.render(string7, True, Color("#DD0000"))
                self.soundsys.loopsound('warn')
            elif self.player.peri <= self.player.planet.r:
                string7 = "     WARNING: ORBIT TOO LOW!"
                sprite7 = self.font.render(string7, True, Color("#DD0000"))
                self.soundsys.loopsound('warn')
            else:
                string7 = "             ORBIT OK"
                sprite7 = self.font.render(string7, True, Color("#007700"))
                self.soundsys.removelooped('warn')
        else:
            self.soundsys.removelooped('warn')
            string5 = "Orbited %.2fs, record %.2fs" % ((self.player.deathtime - self.player.spawntime)/1000.0, self.player.max_alive/1000.0)
            string6 = " "
            string7 = " "
            sprite7 = self.font.render(string7, True, Color("#DD0000"))
        
        sprite1 = self.font.render(string1, True, Color(self.team1.color))
        sprite2 = self.font.render(string2, True, Color(self.team2.color))
        sprite3 = self.font.render(string3, True, self.player.color)
        sprite4 = self.font.render(string4, True, self.player.color)
        sprite5 = self.font.render(string5, True, self.player.color)
        sprite6 = self.font.render(string6, True, self.player.color)
        #sprite7
        self.bg.fill(Color("#FFFFFFAA"))
        self.bg.blit(sprite1, (5, -5))
        self.bg.blit(sprite2, (5, 12))
        self.bg.blit(sprite3, (5, 39))
        self.bg.blit(sprite4, (5, 56))
        self.bg.blit(sprite5, (5, 73))
        self.bg.blit(sprite6, (5, 100))
        self.bg.blit(sprite7, (5, 127))
        screen.blit(self.bg, (10,10))