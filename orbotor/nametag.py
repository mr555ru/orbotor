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

import pygame
from pygame import Color

from camera import Camerable
from game_constants import SYS_FONT

class Nametag(Camerable):
    def __init__(self, ref):
        Camerable.__init__(self)
        self.ref = ref
        self.r = 3
        self.upd()
        
        self.font = pygame.font.Font(SYS_FONT, 14)
        
    
    def upd(self):
        self.x = self.ref.x
        self.y = self.ref.y
        
    def draw(self, screen, t_x, t_y, t_ang, t_zoom):
        if self.ref.spawned and t_zoom > (0.08 if self.ref.is_ai else 0.03):
            sprite = self.font.render(self.ref.name, True, Color("#FFFF00"))
            screen.blit(sprite, (t_x-len(self.ref.name)*3, t_y-self.r+int(16*t_zoom)))

    def step(self):
        pass