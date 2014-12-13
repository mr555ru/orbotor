#static_functions
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
import math
from PIL import Image as PIL_Image

import pygame
from pygame import *

from game_constants import *

def min_max_value(min, max, value):
    if value < min:
        return min
    elif value > max:
        return max
    return value

def create_color_circle(color, r):
    r = int(r)
    p = Surface((r*2, r*2), flags=SRCALPHA)
    p.fill(Color("#00000000"))
    pygame.draw.circle(p, Color(color.r/2, color.g/2, color.b/2, color.a), (r, r), r)
    pygame.draw.circle(p, color, (r, r), r-int(r/5))
    return p

def imitate_debris(color1, color2, r):
    p = Surface((r*2, r*2), flags=SRCALPHA)
    p.fill(Color("#00000000"))
    places = []
    for i in xrange(3):
        new = random.randint(max(2, int(r/2)), max(2+int(r/5), int(r/1.5)))
        x = random.randint(new, r*2-new)
        y = random.randint(new, r*2-new)
        places.append((new,x,y))
    for place in places:
        pygame.draw.circle(p, color1, (place[1], place[2]), place[0])
    for place in places:
        pygame.draw.circle(p, color2, (place[1], place[2]), place[0]-int(r/5))
    return p

def mirror_polygons(d, l):
    for name, polygon in l.items():
        new_polygon = []
        for x, y in polygon:
            new_polygon.append((d-x, d-y))
        l[name] = new_polygon
    return l

def continent_polygons(r):
    d = r*2
    Asia = [(d*5/24, d*11/24),
            (d*1/4, d*1/2),
            (d*1/2, d*16/24),
            (d*3/4, d*16/24),
            (d*22/24, d*1/2),
            (d*23/24, d*9/24),
            (d*1, d*1/2),
            (d*22/24, d*3/4),
            (d*3/4, d*22/24),
            (d*1/2, d*1),
            (d*1/3, d*23/24),
            (d*5/24, d*21/24),
            (d*4/24, d*3/4),
            (d*5/24, d*3/4),
            (d*4/24, d*15/24),
            (d*3/24, d*2/3)
            ]
    
    Honshu = [(d*3/24, d*3/4),
              (d*4/24, d*3/4),
              (d*3/24, d*20/24)]
    
    England = [
        (d*13/16, d*7/16),
        (d*20/24, d*11/24),
        (d*22/24, d*11/24),
        (d*22/24, d*1/2),
        (d*13/16, d*11/24)]

    Ireland = [
        (d*21/24, d*7/16),
        (d*22/24, d*10/24),
        (d*22/24, d*7/16)]

    America = [
        (d*4/24, d*10/24),
        (d*4/24, d*1/3),
        (d*1/4, d*1/4),
        (d*1/4, d*3/24),
        (d*7/24, d*1/24),
        (d*11/24, d*0),
        (d*9/16, d*0),
        (d*3/4, d*4/24),
        (d*9/16, d*4/24),
        (d*14/24, d*3/24),
        (d*1/2, d*3/24),
        (d*11/24, d*4/24),
        (d*14/24, d*5/24),
        (d*15/24, d*6/24),
        (d*13/24, d*6/24),
        (d*1/2, d*7/24),
        (d*9/24, d*7/24),
        (d*5/24, d*9/24)]

    Greenland = [
        (d*3/4, d*1/4),
        (d*2/3, d*10/24),
        (d*14/24, d*11/24),
        (d*13/24, d*1/3),
        (d*14/24, d*1/3)]
    
    l = {"Asia":Asia, "Honshu":Honshu, "England":England, "Ireland":Ireland, "America":America, "Greenland":Greenland}
    #mirror_polygons(d, l)
    return l

def create_planet_visualisation(r):
    ocean_color = Color("#1177FF")
    green_color = Color("#339933")
    ice_color = Color("#CCFFFF")
    p = create_color_circle(ocean_color, r)
    return p

def pil_process(path, hwsurface=False):
    i = PIL_Image.open(path)
    mode = i.mode
    size = i.size
    data = i.tostring()
    surface = pygame.image.fromstring(data, size, mode)
    if hwsurface:
        surface2 = Surface(size, flags=SRCALPHA+HWSURFACE)
        surface2.blit(surface, (0,0))
        surface = surface2
    return surface

def rot_center(image, angle):
    """rotate an image while keeping its center and size"""
    orig_rect = image.get_rect()
    rot_image = pygame.transform.rotate(image, angle)
    rot_rect = orig_rect.copy()
    rot_rect.center = rot_image.get_rect().center
    rot_image = rot_image.subsurface(rot_rect).copy()
    return rot_image

def better_rotozoom(surface, angle, zoom, offset, is_circle=False):
    #zoom = zoom*sprite_hd_ratio
    
    #offset = (center[0]-real_center[0],center[1]-real_center[1])
    
    r = math.sqrt(offset[0]**2 + offset[1]**2) * zoom
    ang = math.atan2(-offset[1], offset[0]) - math.radians(angle)
    
    new_offset = (r*math.cos(ang), r*math.sin(ang))
    
    #new_surface = pygame.transform.rotozoom(surface, angle, zoom)
    #new_surface_center = (new_surface.get_width()/2, new_surface.get_height()/2)
    #new_offset = (new_offset[0] - new_surface_center[0]+surface_center[0], new_offset[1] - new_surface_center[1]+surface_center[1])
    
    new_surface = surface
    
    if zoom != 1: #ebig performance tweaks!
        scale_dim = (max(int(surface.get_width()*zoom),2), max(int(surface.get_height()*zoom),2))
        if abs(angle) > 0.08 and not is_circle and max(scale_dim) > 2:
            new_surface = rot_center(new_surface, -angle)
        new_surface = pygame.transform.scale(new_surface, scale_dim)
    elif abs(angle) > 0.08 and not is_circle:
        new_surface = rot_center(new_surface, -angle)
        
    
    if surface.get_flags() % 2 == 1: #hwsurface: 
        new_surface_2 = Surface(new_surface.get_size(), new_surface.get_flags())
        new_surface_2.blit(new_surface, (0,0))
        new_surface = new_surface_2
    
    return new_surface, new_offset

def get_peri_apo(r, v, ang, G, M): #equations! via http://www.braeunig.us/space/orbmech.htm
    C = (2*G*M)/(r*v*v)
    
    R1 = (-C + math.sqrt(C*C - 4 * (1-C) * (-math.sin(ang)**2)))/(2 * (1-C)) * r
    R2 = (-C - math.sqrt(C*C - 4 * (1-C) * (-math.sin(ang)**2)))/(2 * (1-C)) * r
    
    peri = min(R1,R2)
    apo = max(R1,R2)
    
    return peri, apo