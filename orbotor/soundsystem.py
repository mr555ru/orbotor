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

import os

import pygame


class SoundSystem():
    
    def __init__(self):
        pygame.mixer.init()
        self.sound_on = True
        self.sounds_folder = "sounds"
        self.sounds = {}
        self.bg = pygame.mixer.Sound(os.path.join(self.sounds_folder, "lazarus-rising.ogg"))
        self.bg.play(-1)
        
    def initsound(self, id, filename):
        if id not in self.sounds.keys():
            self.sounds[id] = pygame.mixer.Sound(os.path.join(self.sounds_folder, filename))
        
    def playsound(self, id):
        if self.sound_on:
            self.sounds[id].play()
            
    def switch(self):
        self.sound_on = not self.sound_on
        if self.sound_on:
            self.bg.play(-1)
        else:
            self.bg.stop()