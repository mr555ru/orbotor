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

import sys  # NOQA
import profile
import ConfigParser

import pygame
from pygame import *

from static_functions import *
import camera as camera
import planet as planet

from orbitable import GCD_Singleton, SoundSystem_Singleton
from helldebris_collection import HellDebrisCollection
from team import Team
from simplestats import SimpleStats


wwidth = 1024
wheight = 768
p1_name = "Player1"
p2_name = "Player2"

config = ConfigParser.RawConfigParser()
config.read('profile.cfg')
wwidth = config.getint("Screen", "width")
wheight = config.getint("Screen", "height")
p1_name = config.get("Player", "P1_name")
p2_name = config.get("Player", "P2_name")

display = (wwidth, wheight)
clock = pygame.time.Clock()


class Profile():
    
    def __init__(self, is_player2_present=False,
                 is_player1_ai=False,
                 is_player2_ai=False,
                 player1_team="Green",
                 player2_team="Red",
                 greenteamsize=8,
                 redteamsize=8,
                 debris_min=6,
                 debris_max=20,
                 draw_planet=False,
                 name=""):
        self.p2 = is_player2_present
        self.p1_ai = is_player1_ai
        self.p2_ai = is_player2_ai
        self.p1_team = player1_team
        self.p2_team = player2_team
        
        mingreen = int(self.p1_team == "Green") + int(self.p2_team == "Green" and self.p2)
        minred = int(self.p1_team == "Red") + int(self.p2_team == "Red" and self.p2)
        self.green = max(mingreen, greenteamsize)
        self.red = max(minred, redteamsize)
        self.hellmin = debris_min
        self.hellmax = debris_max
        self.draw_planet = draw_planet
        self.name = name
        
        self.ERAD = 1000
        self.MAXRAD = 1700
        self.ORBHEIGHT = 350
        
    def game_init(self):
        pygame.init()
    
        self.PROFILESTEP = False
        
        self.UPDAE_GAME = pygame.USEREVENT + 1
        pygame.time.set_timer(self.UPDAE_GAME, GAME_SPEED)
        
        self.screen = pygame.display.set_mode(display)
        
        if self.p2:
            self.bg1 = Surface((wwidth, wheight/2))
            self.bg2 = Surface((wwidth, wheight/2))
            self.cam2 = camera.Camera(self.bg2, first_in_order=False)
            self.bgs = (self.bg1, self.bg2)
        else:
            self.bg1 = Surface((wwidth, wheight))
            self.bgs = (self.bg1,)
        self.cam1 = camera.Camera(self.bg1)
        
        if self.name == "":
            pygame.display.set_caption("Orbotor")
        else:
            pygame.display.set_caption("Orbotor - %s" % self.name)
            
        self.pl = planet.Planet(self.bgs, self.ERAD, self.MAXRAD, "planet.png" if self.draw_planet else None)
        GCD_Singleton.set_planet(self.pl)
        
        self.soundsys = SoundSystem_Singleton
        
        self.spawn = (self.ERAD+self.ORBHEIGHT, 0)
        self.team1 = Team("Green", "#009900", self.green, self.spawn, self.pl)
        self.team2 = Team("Red", "#880000", self.red, self.spawn, self.pl)
        self.team1.set_opponent_team(self.team2)
        self.team2.set_opponent_team(self.team1)
        self.hell = HellDebrisCollection(self.spawn, self.pl, self.hellmin, self.hellmax)
        
        if self.p1_team == "Green":
            self.player1 = self.team1.guys[0]
            if self.p2:
                if self.p2_team == "Green":
                    self.player2 = self.team1.guys[1]
                elif self.p2_team == "Red":
                    self.player2 = self.team2.guys[0]
                else:
                    raise Exception("unknown team for p2: %s" % self.p2_team)
        elif self.p1_team == "Red":
            self.player1 = team2.guys[0]
            if self.p2:
                if self.p2_team == "Green":
                    self.player2 = self.team1.guys[0]
                elif self.p2_team == "Red":
                    self.player2 = self.team2.guys[1]
                else:
                    raise Exception("unknown team for p2: %s" % self.p2_team)
        else:
            raise Exception("unknown team for p1: %s" % self.p1_team)
        self.player1.is_ai = self.p1_ai
        
        if self.p1_ai:
            self.player1.set_name("[bot] %s" % p1_name)
        else:
            self.player1.set_name("%s" % p1_name)
            
        if self.p2:
            self.player2.is_ai = self.p2_ai
            if self.p2_ai:
                self.player2.set_name("[bot] %s" % p2_name)
            else:
                self.player2.set_name("%s" % p2_name)
                
        self.stats1 = SimpleStats(self.team1, self.team2, self.player1)
         
        if self.p2:
            self.stats2 = SimpleStats(self.team1, self.team2, self.player2)
             
    def game_key_listen(self, event):
        if event.type == KEYDOWN and event.key == K_F1:
            self.PROFILESTEP = True
            self.game_step()
        elif event.type == KEYDOWN and event.key == K_F2:
            print len(GCD_Singleton.orbitables)
        elif event.type == KEYDOWN and event.key == K_F5:
            self.soundsys.switch()
        if not self.p1_ai:
            self.player1.catch_kb_event(event)
        if self.p2 and not self.p2_ai:
            self.player2.catch_kb_event_hotseat(event)
        self.cam1.keys_listen(event)
        if self.p2:
            self.cam2.keys_listen_hotseat(event)
            
    def game_step(self):
        if self.PROFILESTEP:
            profile.runctx("self._step()", globals(), {"self": self})
        else:
            self._step()
            
    def _step(self):
        self.team2.step()  # todo faster better stronger
        self.team1.step()
        self.hell.step()
        
        self.player1.focus(self.cam1)
        self.cam1.step()
        if self.p2:
            self.player2.focus(self.cam2)
            self.cam2.step()
        
        GCD_Singleton.step()
        
    def game_draw(self):
        if self.PROFILESTEP:
            profile.runctx("self._draw()", globals(), {"self": self})
            self.PROFILESTEP = False
        else:
            self._draw()
            
    def _draw(self):
        clock.tick(60)
        
        tup = [self.pl, ] + self.team1.objectslist() + self.team2.objectslist()\
            + self.hell.objectslist() + self.pl.cities
        tup = tuple(tup)
        self.cam1.translate_coords(*tup)
        if self.p2:
            self.cam2.translate_coords(*tup)

        self.stats1.draw(self.bg1)
        self.screen.blit(self.bg1, (0, 0))
        if self.p2:
            self.stats2.draw(self.bg2)
            self.screen.blit(self.bg2, (0, wheight/2))
        
        pygame.display.update()
        
        
def DefaultProfile(draw_planet, hell):
    return Profile(draw_planet=draw_planet, debris_min=hell[0], debris_max=hell[1])


def HotseatProfile(draw_planet, hell):
    return Profile(is_player2_present=True, draw_planet=draw_planet,
                   debris_min=hell[0], debris_max=hell[1])


def RivalProfile(draw_planet, hell):
    return Profile(is_player2_present=True, is_player2_ai=True, draw_planet=draw_planet,
                   debris_min=hell[0], debris_max=hell[1])


def CoopProfile(draw_planet, hell):
    return Profile(is_player2_present=True, player2_team="Green", draw_planet=draw_planet,
                   debris_min=hell[0], debris_max=hell[1])


def SpectateProfile(draw_planet, hell):
    return Profile(is_player1_ai=True, draw_planet=draw_planet,
                   debris_min=hell[0], debris_max=hell[1])


def SurvivalProfile(draw_planet):
    return Profile(draw_planet=draw_planet, debris_min=35, debris_max=70,
                   greenteamsize=1, redteamsize=0)


def CoopSurvivalProfile(draw_planet):
    return Profile(is_player2_present=True, player2_team="Green", draw_planet=draw_planet,
                   debris_min=35, debris_max=70, greenteamsize=2, redteamsize=0)
