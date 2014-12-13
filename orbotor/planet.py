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
from camera import Camerable

class Planet(Camerable):

    def __init__(self, surfaces, radius, maxradius, sprite=None):
        Camerable.__init__(self)
        self.x = 0.0
        self.y = 0.0
        self.r = radius
        self.r2 = maxradius
        self.m = 70000
        self.bg = Color("#000510")
        self.deep_color = Color("#0066EE")
        self.ocean_color = Color("#1177FF")
        self.green_color = Color("#339933")
        self.ice_color = Color("#CCFFFF")
        
        self.repr = "Planet"
        self.polygons = {}

        self.surfaces = surfaces
        
        self.dont_draw = False
        
        if sprite is None:
            self.sprite = None
            self.polygons = continent_polygons(self.r)
        else:
            self.sprite = pil_process(os.path.join("images", sprite), hwsurface=True)
            sprite_ratio = float(self.sprite.get_height())/self.sprite.get_width()

        self.cities = [City(self, "London", -0.35, 0.79),
                       City(self, "Paris", 1, 0.9),
                       City(self, "New-York", -5.2, 0.93),
                       City(self, "Moscow", 3, 0.7),
                       City(self, "Tokyo", 9.3, 0.95),
                       City(self, "Beijing", 7.7, 0.85),
                       City(self, "Los Angeles", -7.8, 0.95),]
        
    def calc_polygons(self, t_x, t_y, t_ang, t_zoom):
        new_polygons = {}
        for name, polygon in self.polygons.items():
            new_polygon = []
            for x, y in polygon:
                newx = (x-self.r)*t_zoom*0.98
                newy = (y-self.r)*t_zoom*0.98
                r = math.sqrt(newx**2+newy**2)
                ange = math.atan2(-newy, newx)+math.radians(t_ang)
                newx = r*math.cos(ange)+t_x
                newy = r*math.sin(ange)+t_y
                new_polygon.append((newx, newy))
            new_polygons[name] = new_polygon
        return new_polygons
        

    def draw(self, camera_bg, t_x, t_y, t_ang, t_zoom):
        camera_bg.fill(self.bg)
        pygame.draw.circle(camera_bg, Color("#002520"), (t_x, t_y), int(self.r2*t_zoom))
        if not self.dont_draw:
            if self.sprite is None:
                pygame.draw.circle(camera_bg, self.deep_color, (t_x, t_y), int(self.r*t_zoom))
                pygame.draw.circle(camera_bg, self.ocean_color, (t_x, t_y), int((self.r-6)*t_zoom))
                polygons = self.calc_polygons(t_x, t_y, t_ang, t_zoom)
                for name, polygon in polygons.items():
                    if name == "Greenland":
                        c = self.ice_color
                    else:
                        c = self.green_color
                    
                    pygame.draw.polygon(camera_bg, c, polygon)
                
            else:
                self.derivative, offsets = better_rotozoom(self.sprite, t_ang, t_zoom*float(self.r*2)/self.sprite.get_width(), (self.sprite_off_x, self.sprite_off_y))
                camera_bg.blit(self.derivative, (t_x-t_zoom*self.r, t_y-t_zoom*self.r))
        self.dont_draw = False

class City(Camerable):

    def __init__(self, planet, name, hour_belt, dist=1):
        Camerable.__init__(self)
        angle = hour_belt / 24.0 * 2 * math.pi
        self.x = planet.r * math.cos(angle) * dist
        self.y = planet.r * math.sin(angle) * dist
        self.name = name

        self.font = pygame.font.Font(SYS_FONT, 25)
        self.dot = create_color_circle(Color("#FFFFFF"), 3)

    def draw(self, screen, t_x, t_y, t_ang, t_zoom):
        if t_zoom > 0.03:
            screen.blit(self.dot, (t_x-3, t_y-3))
        if t_zoom > 0.1:
            sprite = self.font.render(self.name, True, Color("#FFFFFF"))
            screen.blit(sprite, (t_x, t_y+6))