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
        self.looped = []
        
        self.initsound("bg","lazarus-rising.ogg",1.0)
        self.loopsound("bg")
        
        
    def initsound(self, id, filename, volume=0.7):
        if id not in self.sounds.keys():
            if os.path.isfile(os.path.join(self.sounds_folder, filename)):
                self.sounds[id] = pygame.mixer.Sound(os.path.join(self.sounds_folder, filename))
                self.sounds[id].set_volume(volume)
            else:
                print "WARNING: no file %s found" % os.path.join(self.sounds_folder, filename)
        
    def playsound(self, id):
        if self.sound_on and id in self.sounds.keys():
            self.sounds[id].play()
            
    def loopsound(self, id):
        if self.sound_on and id not in self.looped and (id in self.sounds.keys()):
            self.sounds[id].play(-1)
            self.looped.append(id)
            print ""
            
    def removelooped(self, id):
        if id in self.looped and id in self.sounds.keys():
            self.sounds[id].stop()
            self.looped.remove(id)
            
    def switch(self):
        self.sound_on = not self.sound_on
        if self.sound_on:
            for id in self.looped:
                self.sounds[id].play(-1)
        else:
            for id in self.looped:
                self.sounds[id].stop()