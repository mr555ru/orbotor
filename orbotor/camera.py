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
from static_functions import *

class Camera():

    def __init__(self, surface):
        self.x = 0
        self.y = 0
        self.ang = 0
        self.surface = surface
        self.w = self.surface.get_width()
        self.h = self.surface.get_height()
        self.maxwh = max(self.w, self.h)
        self.zoom = 1
        self.zooming = {"in": False, "out": False}
            

    def translate_coords(self,*args):
        #a = []
        for obj in args:
            x = (obj.x - self.x)*self.zoom
            y = (obj.y - self.y)*self.zoom
            
            isoncamera = x+self.maxwh/2 > -obj.r*self.zoom and y+self.maxwh/2 > -obj.r*self.zoom and x+self.maxwh/2 < self.maxwh+obj.r*self.zoom and y+self.maxwh/2 < self.maxwh+obj.r*self.zoom
            
            if isoncamera or obj.repr == "Planet":    
                r = math.sqrt(x**2+y**2)
                ange = math.atan2(-y, x)+self.ang
                newx = r*math.cos(ange)+self.w/2
                newy = r*math.sin(ange)+self.h/2
                
                newang = self.ang - obj.ang
                obj.draw(self.surface, int(newx), int(newy), math.degrees(newang), self.zoom)
                obj.hearable = True
                #a.append((obj, newx, newy, math.degrees(newang), self.zoom))
                if obj.repr == "Planet" and not isoncamera:
                    obj.dont_draw = True
            else:
                obj.hearable = False
        #print len(a)
        #return a
    
    def step(self):
        if self.zooming["in"]:
            self.zoom *= 1.1
        if self.zooming["out"]:
            self.zoom /= 1.1
        self.zoom = min_max_value(0.01, 7, self.zoom)
    
    def keys_listen(self, e):
        if e.type == KEYDOWN:
            applyval = True
        elif e.type == KEYUP:
            applyval = False
        else:
            return 0
        
        if e.key == K_1:
            self.zooming["out"] = applyval
        elif e.key == K_2:
            self.zooming["in"] = applyval
        elif e.key == K_3 and e.type == KEYDOWN:
            self.zoom = 1
            
    def keys_listen_hotseat(self, e):
        if e.type == KEYDOWN:
            applyval = True
        elif e.type == KEYUP:
            applyval = False
        else:
            return 0
        
        if e.key == K_8:
            self.zooming["out"] = applyval
        elif e.key == K_9:
            self.zooming["in"] = applyval
        elif e.key == K_0 and e.type == KEYDOWN:
            self.zoom = 1
        
    
class Camerable(object):
    def __init__(self):
        self.x = 0
        self.y = 0
        self.ang = 0
        self.name = ''
        self.sprite_off_x = 0
        self.sprite_off_y = 0
        self.r = 0
        self.repr = "dunno"
        self.hearable = False
        
    def draw(self, screen, t_x, t_y, t_ang, t_zoom):
        pass