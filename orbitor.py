# -*- coding: utf-8 -*-
import math
import random
import os.path
import sys
import profile

import pygame
from pygame import *
from PIL import Image as PIL_Image

wwidth = 1024
wheight = 768

display = (wwidth, wheight)

bgcolor = "#000A0F"

ck = "#00FFFF"

G = 1

clock = pygame.time.Clock()

MAXRESPAWNTIME = 3000

MAXOBJECTS = 55

BULLET_LIFE = 7000

BULLET_MASS = 0.3

BULLET_VEL = 6

FUEL_MASS = 0.2

MAX_FUEL = 16
MAX_AMMO = 16

GAME_SPEED = 40

SYS_FONT = "font.ttf"
STATS_FONT = "font_stats.ttf"

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

DEBRIS_R = 6
DEBRIS_SCALING = 3.0
DEBRIS_COLORS = (Color("#555555"),Color("#888888"))
HELLDEBRIS_COLORS = (Color("#303030"),Color("#777777"))

debris_collection = [imitate_debris(DEBRIS_COLORS[0], DEBRIS_COLORS[1], int(DEBRIS_R*DEBRIS_SCALING)) for i in xrange(30)]
helldebris_collection = [imitate_debris(HELLDEBRIS_COLORS[0], HELLDEBRIS_COLORS[1], int(DEBRIS_R*DEBRIS_SCALING)) for i in xrange(30)]

SPARKSPRITE = create_color_circle(Color("#FFFFAA"), 2*DEBRIS_SCALING)

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

bot_names = ['Alice','Reimu','Sakuya','Remilia','Flandre','Patchouli','Cirno','Youmu','Chen','Ran','Yukari', 'Shanghai',
             'Zun','Medicine','Yamaxanadu','Marisa','Koakuma','Shameimaru','Meiling','Lily White','Momiji','Hatete']
random.shuffle(bot_names)

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

class GlobalCollisionDetector():
    
    def __init__(self):
        self.orbitables = []
        self.planet = None
        
    def be_added(self, orbitable):
        self.orbitables.append(orbitable)
        
    def step(self):
        for obj1 in self.orbitables:
            if obj1.GCD_REMOVE_ME_FLAG:
                self.orbitables.remove(obj1)
            else:
                if not (self.planet is None):
                    pl_r = (obj1.x-self.planet.x)**2 + (obj1.y-self.planet.y)**2
                    if pl_r < self.planet.r**2:
                        obj1.get_too_close()
                    elif pl_r > (self.planet.r2**2)*2:
                        obj1.way_too_far()
                    elif pl_r > self.planet.r2**2:
                        obj1.get_too_far()
                for obj2 in self.orbitables:
                    if not (obj1 is obj2) and obj1.colliding and obj2.colliding:
                        r = (obj1.x-obj2.x)**2+(obj1.y-obj2.y)**2
                        minr = (obj1.r + obj2.r)**2
                        #print "%f <= %f" % (r, minr)
                        if r <= minr:
                            #Collision!
                            
                            vel = abs(math.sqrt((obj2.dx-obj1.dx)**2 + (obj2.dy-obj1.dy)**2))
                            ang = math.atan2(obj2.dy-obj1.dy, obj2.dx-obj1.dx)
                            obj1.get_collision(obj2, vel, ang)
                            obj2.get_collision(obj1, vel, ang-math.pi)
                        
                        
GCD = GlobalCollisionDetector()



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
        a = []
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
                a.append((obj, newx, newy, math.degrees(newang), self.zoom))
                if obj.repr == "Planet" and not isoncamera:
                    obj.dont_draw = True
        #print len(a)
        return a
    
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
        else:
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
        
        
        
class Orbitable(Camerable):
    def __init__(self, x, y, r, m, ang=0, dang=0, dx=0, dy=0, nocollidesteps=0, colliding=True):
        global GCD
        Camerable.__init__(self)
        self.x = float(x)
        self.y = float(y)
        self.m = float(m)
        self.r = r
        self.ang = ang
        self.dang = dang
        self.dx = dx
        self.dy = dy
        self.colliding = colliding
        self.repr = "blank"
        GCD.be_added(self)
        self.GCD_REMOVE_ME_FLAG = False
        self.sprite = None #Surface
        self.derivative = None
        self.nocollide = nocollidesteps
        self.maxnocollide = nocollidesteps
        
        self.sprite_off_x = 0
        self.sprite_off_y = 0
        
        self.drawdx = 0
        self.drawdy = 0
        self.is_circle = False
        
    def set_drawdelta(self):
        self.drawdx = self.sprite.get_width()/2
        self.drawdy = self.sprite.get_height()/2
        
           
    def affected(self, mass, x, y):
        R = math.sqrt((x-self.x)**2 + (y-self.y)**2)
        a = G*mass/(R**2)

        ax = a * (x-self.x)/R
        ay = a * (y-self.y)/R

        self.dx += ax
        self.dy += ay

    def initialspeed(self, mass, x, y):
        R = math.sqrt((x-self.x)**2 + (y-self.y)**2)
        aang = math.atan2(-(y-self.y), x-self.x)
        vang = aang+math.pi/2
        v = math.sqrt(G*mass/(R))

        self.dx = v * math.cos(vang)
        self.dy = - v * math.sin(vang)
        
    def focus(self, camera):
        camera.x = self.x
        camera.y = self.y
        camera.ang = self.ang-math.pi/2
        
    def step(self):
        self.x += self.dx
        self.y += self.dy
        self.ang += self.dang
        if self.nocollide > 1:
            self.nocollide -= 1
        elif self.nocollide == 1:
            self.nocollide = 0
            self.colliding = True
        
    def draw(self, screen, t_x, t_y, t_ang, t_zoom):
        self.derivative, offsets = better_rotozoom(self.sprite, t_ang, t_zoom, (self.sprite_off_x, self.sprite_off_y), self.is_circle)
        screen.blit(self.derivative, (t_x-self.drawdx*t_zoom-offsets[0], t_y-self.drawdy*t_zoom-offsets[1]))
        
        
        
    
    def get_collision(self, other, vel, ang):
        self.dx += other.m/float(self.m) * vel * math.cos(ang)
        self.dy += other.m/float(self.m) * vel * math.sin(ang)

    def get_too_close(self):
        pass

    def get_too_far(self):
        pass
    
    def way_too_far(self):
        self.exclude()

    def exclude(self):
        self.colliding = False
        self.GCD_REMOVE_ME_FLAG = True

class Bullet(Orbitable):
    def __init__(self, c, x, y, dx, dy, ang, ownername):
        Orbitable.__init__(self, x, y, r=2, m=BULLET_MASS, dx=0, dy=0, ang=0, dang=0, nocollidesteps=1, colliding=False)
        self.repr = "Bullet"
        self.color = c
        self.ownername = ownername

        self.nocollide = 1

        self.iamakiller = False

        self.sprite = create_color_circle(self.color, self.r)
        
        self.set_drawdelta()

        self.dx = dx + BULLET_VEL*math.cos(ang)
        self.dy = dy + BULLET_VEL*math.sin(ang)

        self.birthtime = pygame.time.get_ticks()

        self.children = []
        
        self.is_circle = True

    def draw(self, screen, t_x, t_y, t_ang, t_zoom):
        Orbitable.draw(self, screen, t_x, t_y, t_ang, t_zoom)

    def step(self):
        Orbitable.step(self)
        if pygame.time.get_ticks() - self.birthtime > BULLET_LIFE and random.randint(0, 30) == 0:
            self.destroy()
        

        

    def get_collision(self, other, vel, ang):
        pass

    def get_too_close(self):
        self.destroy()

    def get_too_far(self):
        if random.randint(0, 40) == 0:
            self.destroy()

    def destroy(self):
        self.exclude()
        self.colliding = False
        #print "bullet destroyed"

class Debris(Orbitable):
    def __init__(self, x, y, dx, dy):
        Orbitable.__init__(self, x, y, r=DEBRIS_R, m=2, dx=0, dy=0, ang=0, dang=0, nocollidesteps=45, colliding=False)
        self.repr = "Debris"
        self.scaling = DEBRIS_SCALING
        self.m = random.random()*5+2
        self.children = []

        self.sprite = random.choice(debris_collection)
        
        self.set_drawdelta()

        self.dx = dx + (random.randint(0,40)-20)/30.0
        self.dy = dy + (random.randint(0,40)-20)/30.0
        self.dang = random.random()*0.8-0.4
        #print self.dang

        #print "debris initiated %f %f" % (self.dx, self.dy)
        
    def draw(self, screen, t_x, t_y, t_ang, t_zoom):
        t_zoom = t_zoom/self.scaling
        self.derivative, offsets = better_rotozoom(self.sprite, t_ang, t_zoom, (self.sprite_off_x, self.sprite_off_y))
        screen.blit(self.derivative, (t_x-self.drawdx*t_zoom-offsets[0], t_y-self.drawdy*t_zoom-offsets[1]))
            

    def get_collision(self, other, vel, ang):
        if random.randint(0,4) == 0 and other.repr != "Spark":
            m = 0
            for i in xrange(random.randint(2, 7)):
                m += 5
                self.children.append(Debris(self.x, self.y, self.dx, self.dy))
            for i in xrange(random.randint(0,3)):
                self.children.append(Spark(self.x, self.y, self.dx, self.dy, vel*other.m, ang))
            self.m = m
            Orbitable.get_collision(self, other, vel, ang)
        self.destroy()

    def get_too_close(self):
        self.destroy()

    def get_too_far(self):
        if random.randint(0, 200) == 0:
            self.destroy()

    def destroy(self):
        self.exclude()
        self.colliding = False
        #print "debris destroyed"
        
class FuelSupply(Debris):
    
    def __init__(self, x, y, dx, dy):
         Debris.__init__(self, x, y, dx, dy)
         self.r = 4
         self.sprite = create_color_circle(Color("#B09050"), self.r*self.scaling)
         self.repr = "FuelSupply"
         self.m = 16*FUEL_MASS
         self.is_circle = True
         
    def get_collision(self, other, vel, ang):
        if other.repr == "Sputnik":
            if other.spawned:
                if vel < 2:
                    other.refuel()
                    #print "Bless you with fuel!"
                else:
                    other.destroy(reason=self.repr)
        self.destroy()
        
class AmmoSupply(Debris):
    
    def __init__(self, x, y, dx, dy):
         Debris.__init__(self, x, y, dx, dy)
         self.r = 4
         self.sprite = create_color_circle(Color("#44DDDD"), self.r*self.scaling)
         self.repr = "AmmoSupply"
         self.m = 16*BULLET_MASS
         self.is_circle = True
         
    def get_collision(self, other, vel, ang):
        if other.repr == "Sputnik":
            if other.spawned:
                if vel < 2:
                    other.reload()
                    #print "Bless you with ammo!"
                else:
                    other.destroy(reason=self.repr)
        self.destroy()
    

class HellDebris(Debris):
    
    def __init__(self, x, y, dx, dy):
         Debris.__init__(self, x, y, dx, dy)
         self.sprite = random.choice(helldebris_collection)
    
    def initialspeed(self, mass, x, y):
        R = math.sqrt((x-self.x)**2 + (y-self.y)**2)
        aang = math.atan2(-(y-self.y), x-self.x)
        vang = aang-math.pi/2
        v = math.sqrt(G*mass/(R))

        self.dx = v * math.cos(vang) + (random.randint(0,40)-20)/80.0
        self.dy = - v * math.sin(vang) + (random.randint(0,40)-20)/80.0

    def get_collision(self, other, vel, ang):
        if random.randint(0,2) == 0:
            m = 0
            for i in xrange(random.randint(2, 4)):
                m += 5
                self.children.append(HellDebris(self.x, self.y, self.dx, self.dy))
            for i in xrange(random.randint(0,3)):
                self.children.append(Spark(self.x, self.y, self.dx, self.dy, vel*other.m, ang))
            self.m = m
            Orbitable.get_collision(self, other, vel, ang)
        self.destroy()
        
class Spark(Debris):
    def __init__(self, x, y, dx, dy, impulse, ang):
        Debris.__init__(self, x, y, dx, dy)
        self.sprite = SPARKSPRITE
        self.set_drawdelta()
        self.nocollide = 50
        self.repr = "Spark"
        self.m = 1.5
        self.dx += impulse*random.random()*math.cos(ang)/self.m
        self.dy += impulse*random.random()*math.sin(ang)/self.m
        self.deathtime = pygame.time.get_ticks() + random.randint(int(2000.0/max(1,impulse)),int(16000.0/max(1,impulse)))
        self.is_circle = True
        
    def step(self):
        Debris.step(self)
        if pygame.time.get_ticks() - self.deathtime > 0:
            self.destroy()
            
    def destroy(self):
        self.exclude()
                
                
                
class Attachment(Camerable):
    def __init__(self, ref, r, distx, disty):
        Camerable.__init__(self)
        self.ref = ref
        self.r = r
        
        self.dist = math.sqrt(distx**2 + disty**2)
        
        self.att_ang = math.atan2(-disty, distx)
        
        #self.upd()
        
        self.sprite = None #Surface
        self.derivative = None
        
    
    def upd(self):
        self.ang = self.att_ang+self.ref.ang
        self.x = self.ref.x+self.dist*math.cos(self.ang)
        self.y = self.ref.y+self.dist*math.sin(self.ang)
        
        
    def draw(self, screen, t_x, t_y, t_ang, t_zoom):
        if self.ref.spawned:
            self.derivative = pygame.transform.rotozoom(self.sprite, t_ang, t_zoom)
            #self.derivative.set_colorkey(Color(ck))
            screen.blit(self.derivative, (t_x-self.r*t_zoom, t_y-self.r*t_zoom))

    def step(self):
        pass

        
class Nose(Attachment):
    def __init__(self, ref):
        Attachment.__init__(self, ref, 3, 8, 0)
        self.sprite = create_color_circle(ref.color, 3)

        
class Thruster(Attachment):
    def __init__(self, ref, thruster_keys, r, distx, disty):
        Attachment.__init__(self, ref, r, distx, disty)
        self.sprite = pil_process(os.path.join("images", "thrust.png"))
        self.sprite_r = self.sprite.get_width()/2
        self.sprite_scaling = 1.5
        self.thruster_keys = thruster_keys
        self.repr = "Thruster"
        self.dist = self.dist+self.r*self.sprite_scaling
        
    def draw(self, screen, t_x, t_y, t_ang, t_zoom):
        if self.ref.spawned:
            k = [self.ref.thrusters_on[key] for key in self.thruster_keys]
            t_zoom = t_zoom*self.r/float(self.sprite_r)*self.sprite_scaling
            
            if sum(k) > 0:
                self.derivative = better_rotozoom(self.sprite, t_ang, t_zoom, (0,0))[0]
                #print offsets
                #self.derivative.set_colorkey(Color(ck))
                screen.blit(self.derivative, (t_x-t_zoom*self.sprite_r, t_y-t_zoom*self.sprite_r))
        

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



        
    
        


class Sputnik(Orbitable):

    def __init__(self, c, x, y, planet, is_ai=False):
        Orbitable.__init__(self, x, y, r=8, m=15, dx=0, dy=0, ang=random.random()*2*math.pi, dang=0, nocollidesteps=20, colliding=True)
        self.color = Color(c)
        self.spawn = (x, y)
        self.repr = "Sputnik"
        
        self.hull_mass = 10
        self.refuel()
        self.reload()
        
        self.m = float(self.hull_mass + self.fuel * FUEL_MASS + self.ammo * BULLET_MASS)
        

        #self.sprite = create_color_circle(self.color, self.r)
        if c == "#009900":
            self.sprite = pil_process(os.path.join("images", "green_ship.png"))
            
            self.sprite_off_x = 1
            self.sprite_off_y = 1
            
        elif c == "#880000":
            self.sprite = pil_process(os.path.join("images", "red_ship.png"))
            
            self.sprite_off_x = 1
            self.sprite_off_y = 1
            
        else:
            self.sprite = create_color_circle(self.color, self.r)
            
        self.set_drawdelta()
        
        #self.nose = Nose(self)
        self.nametag = Nametag(self)
        self.children = []

        self.deaths = 0
        self.frags = 0

        self.name = ' '
        
        self.spawntime = pygame.time.get_ticks()
        self.max_alive = 0

        
        
        #thrusters
        self.angularforce = 0.0007
        self.forwardforce = 0.03
        self.turboforce = 0.14
        self.turboconsum = self.turboforce * 1.33
        self.linearforce = self.forwardforce/2
        
        self.max_dang = 0.16
        
        self.visualthrusters = [Thruster(self, ("fw",), 4, -self.r, 0),
                                Thruster(self, ("turbo",), 7 ,-self.r,0),
                                Thruster(self, ("back","ang_cw","left", "killrot", "ai_cw"), 2, self.r*0.7, 4),
                                Thruster(self, ("back","ang_ccw","right", "killrot", "ai_ccw"), 2, self.r*0.7, -4),
                                Thruster(self, ("ang_ccw","left", "killrot", "ai_ccw"), 2, -self.r*0.4, 7),
                                Thruster(self, ("ang_cw","right", "killrot", "ai_cw"), 2, -self.r*0.4, -7),
                                Thruster(self, ("turbo_left",), 6, 0,10),
                                Thruster(self, ("turbo_right",), 6, 0,-10),
                                Thruster(self, ("turbo_back",), 5, self.r, 0)
                               ]
        
        self.planet = planet
        
        self.is_ai = is_ai
        
        if self.is_ai:
            
            self.name = "[bot] %s" % bot_names.pop()

        self.ai_random_thruster_time = 0

        self.opponent_teams = []
        self.nearest_opponent = (None, 0, 0)
        self.smart_time = 0

        self.spawned = True
        self.deathtime = 0

        self.nodebris = 4

        self.team_notice_dead = False
        
        self.thrusters_on = {"ang_cw": False,
                             "ang_ccw": False,
                             "fw": False,
                             "back": False,
                             "left": False,
                             "right": False,
                             "killrot": False,
                             "ai_cw": False,
                             "ai_ccw": False,
                             "turbo": False,
                             "turbo_left": False,
                             "turbo_right": False,
                             "turbo_back": False}
        
        self.peri = 0
        self.apo = 0
        self.height = 0
        #self.ecc = 0
        self.anomaly = 0
        
    def set_name(self, new_name):
        print "%s is now %s" % (self.name, new_name)
        self.name = new_name
        
        
    def get_peri_apo(self):
        r = math.sqrt((self.x-self.planet.x)**2 + (self.y-self.planet.y)**2)
        v = math.sqrt(self.dx**2 + self.dy**2)
        ang_r = math.atan2(self.y-self.planet.y, self.x-self.planet.x)
        ang_v = math.atan2(self.dy, self.dx)
        ang = ang_v-ang_r
        self.peri, self.apo = get_peri_apo(r, v, ang, G, self.planet.m)
        self.height = r
        
        self.anomaly = math.atan2((r*v*v/(G*self.planet.m))*math.sin(ang)*math.cos(ang),((r*v*v/(G*self.planet.m))*math.sin(ang)-1))
        #self.ecc = math.sqrt((((r*v*v)/(G*self.planet.m)-1)**2) * (math.cos(ang-math.pi/2)**2) + (math.sin(ang-math.pi/2)**2))
        
    def draw_orbit(self, camera): #DOES NOT WORK
        ang_peri = math.atan2(self.y-self.planet.y, self.x-self.planet.x) - self.anomaly
        
        a = (self.peri+self.apo)/2
        b = a * math.sqrt(1-self.ecc**2)
        
        e_surface = Surface((a*2, b*2))
        pygame.draw.ellipse(e_surface, Color("#FFFF00"), (0, 0, a*2, b*2), 2)
        
        ang_to_surf = ang_peri + math.atan2(b, self.peri)
        dist_to_surf = math.sqrt(b**2 + self.peri**2)
        
        surf_x = dist_to_surf*math.cos(ang_to_surf) + self.planet.x
        surf_y = dist_to_surf*math.sin(ang_to_surf) + self.planet.y
        
        surf_x = (surf_x - camera.x)*camera.zoom
        surf_y = (surf_y - camera.y)*camera.zoom
        
        surf_ang = camera.ang - ang_peri
        
        e_surface = better_rotozoom(e_surface, surf_ang, camera.zoom, (0,0))
        camera.surface.blit(e_surface[0], (surf_x, surf_y))
        
        

    def draw(self, screen, t_x, t_y, t_ang, t_zoom):
        if not self.spawned:
            if pygame.time.get_ticks() - self.deathtime > MAXRESPAWNTIME:
                self.respawn()
            else:
                #print pygame.time.get_ticks() - self.deathtime
                pass
        else:
            #self.nose.draw(screen, t_x, t_y, t_ang, t_zoom)
            #for thruster in self.visualthrusters:
            #    thruster.draw(screen, t_x, t_y, t_ang, t_zoom)
            Orbitable.draw(self, screen, t_x, t_y, t_ang, t_zoom)

    def fire(self):
        if self.spawned:
            if self.ammo > 0:
                self.ammo -= 1
                self.m = self.hull_mass + self.fuel * FUEL_MASS + self.ammo * BULLET_MASS
                self.children.append(Bullet(self.color, self.x, self.y, self.dx, self.dy, self.ang, self.name))
                
                self.dx -= BULLET_MASS/float(self.m) * BULLET_VEL * math.cos(self.ang)
                self.dy -= BULLET_MASS/float(self.m) * BULLET_VEL * math.sin(self.ang)
        
    def execute_thrusters(self):
        if self.thrusters_on["ang_cw"]:
            if self.fuel > self.angularforce:
                self.dang += self.angularforce * self.hull_mass*1.5/self.m
                self.fuel -= self.angularforce
            else:
                self.thrusters_on["ang_cw"] = False
        if self.thrusters_on["ang_ccw"]:
            if self.fuel > self.angularforce:
                self.dang -= self.angularforce * self.hull_mass*1.5/self.m
                self.fuel -= self.angularforce
            else:
                self.thrusters_on["ang_ccw"] = False
        if self.thrusters_on["killrot"]:
            if self.fuel > self.angularforce:
                self.dang += -1*math.copysign(self.angularforce, self.dang) * self.hull_mass*1.5/self.m
                if abs(self.dang) < 2*self.angularforce:
                    self.dang = 0
                self.fuel -= self.angularforce
            else:
                self.thrusters_on["killrot"] = False
        if self.thrusters_on["fw"]:
            if self.fuel > self.forwardforce:
                self.dx += self.forwardforce*math.cos(self.ang) * self.hull_mass*1.5/self.m
                self.dy += self.forwardforce*math.sin(self.ang) * self.hull_mass*1.5/self.m
                self.fuel -= self.forwardforce
            else:
                self.thrusters_on["fw"] = False
        if self.thrusters_on["turbo"]:
            if self.fuel > self.turboconsum:
                self.dx += self.turboforce*math.cos(self.ang) * self.hull_mass*1.5/self.m
                self.dy += self.turboforce*math.sin(self.ang) * self.hull_mass*1.5/self.m
                self.fuel -= self.turboconsum
            else:
                self.thrusters_on["turbo"] = False 
        if self.thrusters_on["turbo_left"]:
            if self.fuel > self.turboconsum:
                self.dx += self.turboforce*math.cos(self.ang+math.pi/2) * self.hull_mass*1.5/self.m
                self.dy += self.turboforce*math.sin(self.ang+math.pi/2) * self.hull_mass*1.5/self.m
                self.fuel -= self.turboconsum
            else:
                self.thrusters_on["turbo_left"] = False 
        if self.thrusters_on["turbo_right"]:
            if self.fuel > self.turboconsum:
                self.dx += self.turboforce*math.cos(self.ang-math.pi/2) * self.hull_mass*1.5/self.m
                self.dy += self.turboforce*math.sin(self.ang-math.pi/2) * self.hull_mass*1.5/self.m
                self.fuel -= self.turboconsum
            else:
                self.thrusters_on["turbo_right"] = False 
        if self.thrusters_on["turbo_back"]:
            if self.fuel > self.turboconsum:
                self.dx -= self.turboforce*math.cos(self.ang) * self.hull_mass*1.5/self.m
                self.dy -= self.turboforce*math.sin(self.ang) * self.hull_mass*1.5/self.m
                self.fuel -= self.turboconsum
            else:
                self.thrusters_on["turbo_back"] = False 
        if self.thrusters_on["back"]:
            if self.fuel > self.linearforce:
                self.dx -= self.linearforce*math.cos(self.ang) * self.hull_mass*1.5/self.m
                self.dy -= self.linearforce*math.sin(self.ang) * self.hull_mass*1.5/self.m
                self.fuel -= self.linearforce
            else:
                self.thrusters_on["back"] = False
        if self.thrusters_on["left"]:
            if self.fuel > self.linearforce:
                self.dx += self.linearforce*math.cos(self.ang+math.pi/2) * self.hull_mass*1.5/self.m
                self.dy += self.linearforce*math.sin(self.ang+math.pi/2) * self.hull_mass*1.5/self.m
                self.fuel -= self.linearforce
            else:
                self.thrusters_on["left"] = False
        if self.thrusters_on["right"]:
            if self.fuel > self.linearforce:
                self.dx += self.linearforce*math.cos(self.ang-math.pi/2) * self.hull_mass*1.5/self.m
                self.dy += self.linearforce*math.sin(self.ang-math.pi/2) * self.hull_mass*1.5/self.m
                self.fuel -= self.linearforce
            else:
                self.thrusters_on["right"] = False

    def set_opponent_team(self, team):
        self.opponent_teams.append(team)

    def get_nearest_opponent(self):
        self.nearest_opponent = (None, self.planet.r2*4, 0)
        for t in self.opponent_teams:
            for g in t.guys:
                if g.spawned:
                    r = (g.x - self.x)**2 + (g.y - self.y)**2
                    if r < self.nearest_opponent[1]**2:
                        self.nearest_opponent = (g, math.sqrt(r), math.atan2(g.y-self.y, g.x-self.x))

    def init_smart_behavior(self):
        self.get_nearest_opponent()
        self.smart_time = pygame.time.get_ticks() + random.randint(1600, 12000)

    def behave_smart(self):
        if self.smart_time > 0:
            if pygame.time.get_ticks() > self.smart_time:
                self.smart_time = 0
                self.nearest_opponent = (None, 0, 0)
                self.thrusters_on["ai_cw"] = False
                self.thrusters_on["ai_ccw"] = False
            else:
                if self.nearest_opponent[0] is not None:
                    if self.nearest_opponent[0].spawned:
                        self.killall_thrusters()
                        dang = min_max_value(-self.max_dang*0.9, self.max_dang*0.9, (self.nearest_opponent[2]-self.ang)/5.0)
                        if self.fuel > self.angularforce:
                            if dang > 0.01:
                                self.thrusters_on["ai_ccw"] = True
                                self.fuel -= self.angularforce
                            elif dang < -0.01:
                                self.thrusters_on["ai_cw"] = True
                                self.fuel -= self.angularforce
                            self.dang = dang * self.hull_mass*1.5/self.m
                    else:
                        self.smart_time = pygame.time.get_ticks()
                else:
                    self.smart_time = pygame.time.get_ticks()
                
                    
    def killall_thrusters(self):
        for key, value in self.thrusters_on.items():
            self.thrusters_on[key] = False

    def set_random_thruster(self):
        key = random.choice(("fw", "back", "left", "right", "ang_cw", "ang_ccw", "turbo", "killrot", "turbo_back", "turbo_left", "turbo_right"))
        self.thrusters_on[key] = True
        if key in ("turbo", "killrot", "turbo_left", "turbo_right", "turbo_back","fw"):
            self.ai_random_thruster_time = pygame.time.get_ticks() + random.randint(100, 300)
        else:
            self.ai_random_thruster_time = pygame.time.get_ticks() + random.randint(300, 1250)

            
    def catch_kb_event(self, e):
        if e.type == KEYDOWN:
            applyval = True
        elif e.type == KEYUP:
            applyval = False
        else:
            return 0
        
        if e.key == K_w:
            self.thrusters_on["fw"] = applyval
        elif e.key == K_LSHIFT:
            self.thrusters_on["turbo"] = applyval
        elif e.key == K_z:
            self.thrusters_on["turbo_left"] = applyval
        elif e.key == K_x:
            self.thrusters_on["turbo_back"] = applyval
        elif e.key == K_c:
            self.thrusters_on["turbo_right"] = applyval
        elif e.key == K_s:
            self.thrusters_on["back"] = applyval
        elif e.key == K_q:
            self.thrusters_on["left"] = applyval
        elif e.key == K_e:
            self.thrusters_on["right"] = applyval
        elif e.key == K_a:
            self.thrusters_on["ang_cw"] = applyval
        elif e.key == K_d:
            self.thrusters_on["ang_ccw"] = applyval
        elif e.key == K_r:
            self.thrusters_on["killrot"] = applyval
        elif e.key == K_t:
            self.destroy(reason="selfdestroy")
        elif e.key == K_SPACE and e.type == KEYDOWN:
            self.fire()
            #print ((MAXOBJECTS-len(GCD.orbitables))/float(MAXOBJECTS))**8
        else:
            return 0

    def catch_kb_event_hotseat(self, e):
        if e.type == KEYDOWN:
            applyval = True
        elif e.type == KEYUP:
            applyval = False
        else:
            return 0
        
        if e.key == K_i or e.key == K_UP:
            self.thrusters_on["fw"] = applyval
        elif e.key == K_RSHIFT:
            self.thrusters_on["turbo"] = applyval
        elif e.key == K_n:
            self.thrusters_on["turbo_left"] = applyval
        elif e.key == K_m or e.key == K_COMMA:
            self.thrusters_on["turbo_back"] = applyval
        elif e.key == K_PERIOD:
            self.thrusters_on["turbo_right"] = applyval
        elif e.key == K_k or e.key == K_DOWN:
            self.thrusters_on["back"] = applyval
        elif e.key == K_u:
            self.thrusters_on["left"] = applyval
        elif e.key == K_o:
            self.thrusters_on["right"] = applyval
        elif e.key == K_j or e.key == K_LEFT:
            self.thrusters_on["ang_cw"] = applyval
        elif e.key == K_l or e.key == K_RIGHT:
            self.thrusters_on["ang_ccw"] = applyval
        elif e.key == K_p:
            self.thrusters_on["killrot"] = applyval
        elif e.key == K_h:
            self.destroy()
        elif e.key == K_RETURN and e.type == KEYDOWN:
            self.fire()
            #print ((MAXOBJECTS-len(GCD.orbitables))/float(MAXOBJECTS))**8
        else:
            return 0

    def affected(self, mass, x, y):
        super(self.__class__, self).affected(mass, x, y)
        for child in self.children:
            child.affected(mass, x, y)

    def step(self):
        self.m = self.hull_mass + self.fuel * FUEL_MASS + self.ammo * BULLET_MASS
        self.execute_thrusters()
        self.get_peri_apo()
        Orbitable.step(self)
        
        if abs(self.dang) > self.max_dang:
            self.destroy(reason="too much rotation")
        
        if self.spawned:
            if pygame.time.get_ticks() - self.spawntime > self.max_alive:
                self.max_alive = pygame.time.get_ticks() - self.spawntime
        
        #self.nose.upd()
        self.nametag.upd()
        for thruster in self.visualthrusters:
            thruster.upd()

        for child in self.children:
            if child.GCD_REMOVE_ME_FLAG:
                if child.repr == "Bullet":
                    if child.iamakiller:
                        self.frags += 1
                        child.iamakiller = False
                self.children.remove(child)
            child.step()
            while len(child.children) > 0:
                chichild = child.children.pop()
                self.children.append(chichild)
        
        if self.is_ai and self.spawned:
            self.ai_step()
            
    def ai_step(self):
        if self.ai_random_thruster_time > 0:
            if pygame.time.get_ticks() > self.ai_random_thruster_time:
                self.ai_random_thruster_time = 0
                self.killall_thrusters()
        else:
            if random.randint(0, 20) == 0:
                self.set_random_thruster()
        if random.randint(0,  110) == 0:
            self.fire()
        if self.smart_time == 0:
            if random.randint(0, 200) == 0:
                self.init_smart_behavior()
        else:
            self.behave_smart()
            
        if self.apo >= self.planet.r2-self.r-10:
            if self.fuel > self.forwardforce:
                self.fuel -= self.forwardforce
                self.killall_thrusters()
                self.thrusters_on["ai_ccw"] = True
                self.thrusters_on["ai_cw"] = True
                a = math.atan2((self.y-self.planet.y),(self.x-self.planet.x))
                ang = a - math.pi/2 - (math.pi - abs(self.anomaly))/2
                #self.ang = ang
                
                self.dx += self.forwardforce*math.cos(ang)
                self.dy += self.forwardforce*math.sin(ang)
        if self.peri <= self.planet.r+self.r+10:
            if self.fuel > self.forwardforce:
                self.fuel -= self.forwardforce
                self.killall_thrusters()
                self.thrusters_on["ai_ccw"] = True
                self.thrusters_on["ai_cw"] = True
                a = math.atan2((self.y-self.planet.y),(self.x-self.planet.x))
                ang = a + math.pi/2 - abs(self.anomaly)/2
                #self.ang = ang
                
                self.dx += self.forwardforce*math.cos(ang)
                self.dy += self.forwardforce*math.sin(ang)
            
        
    def objectslist(self):
        return [self, self.nametag] + self.children + self.visualthrusters

    def destroy(self, reason="unknown"):
        #if self.nodebris > 0:
        #    self.nodebris -= 1
        if self.spawned:
            if self.name != " ":
                print "%s has been destroyed, reason: %s" % (self.name, reason)
            self.fuel = 0
            self.deaths += 1
            self.deathtime = pygame.time.get_ticks()
            self.colliding = False
            self.nocollide = 0
            self.team_notice_dead = True
            for i in xrange(random.randint(2,4)):
                self.children.append(Debris(self.x, self.y, self.dx, self.dy))
            if random.randint(0, 2) == 0:
                self.children.append(FuelSupply(self.x, self.y, self.dx, self.dy))
            if random.randint(0, 2) == 0:
                self.children.append(AmmoSupply(self.x, self.y, self.dx, self.dy))
        self.spawned = False
    
    def respawn(self):
        self.spawntime = pygame.time.get_ticks()
        self.refuel()
        self.reload()
        self.spawned = True
        self.colliding = False
        self.nocollide = self.maxnocollide
        self.x = self.spawn[0]+random.randint(0,100)-200
        self.y = self.spawn[1]+random.randint(0,100)-200
        self.dang = 0
        self.initialspeed(self.planet.m, self.planet.x, self.planet.y)
        
    def get_collision(self, other, vel, ang):
        if other.repr == "Sputnik" or other.repr == "Debris":
            Orbitable.get_collision(self, other, vel, ang)
            for i in xrange(random.randint(6,20)):
                self.children.append(Spark(self.x, self.y, self.dx, self.dy, vel*other.m, ang))
            if other.repr == "Sputnik":
                self.destroy(reason="collision with %s" % other.name)
            else:
                self.destroy(reason="Debris")
        elif other.repr == "Bullet" and not other.color == self.color:
            Orbitable.get_collision(self, other, vel, ang)
            for i in xrange(random.randint(6,20)):
                self.children.append(Spark(self.x, self.y, self.dx, self.dy, vel*other.m, ang))
            self.destroy(reason=other.ownername + "'s bullet")
            other.iamakiller = True
            other.destroy()

    def get_too_close(self):
        """r = math.sqrt((self.x - self.planet.x)**2 + (self.y - self.planet.y)**2)
        ang = math.atan2((self.y - self.planet.y), (self.x - self.planet.x))+math.pi/2

        dang = math.atan2(self.dy, self.dx)
        
        self.ang = ang+dang
        self.dx *= 1.2
        self.dy *= 1.2"""
        
        self.destroy(reason="fell on planet")

    def get_too_far(self):
        self.destroy(reason="deorbited")
        
    def way_too_far(self):
        self.destroy(reason="how the hell did it get there?!")
        
    def refuel(self):
        self.fuel = MAX_FUEL
        
    def reload(self):
        self.ammo = MAX_AMMO
        
    def initialspeed(self, mass, x, y):
        Orbitable.initialspeed(self, mass, x, y)
        self.get_peri_apo()
    
class Team():
    def __init__(self, name, color, participants, spawn, planet):
        self.guys = []
        self.deaths = 0
        self.name = name
        self.planet = planet
        self.color = color
        self.maxfrags = 0
        for i in xrange(participants):
            guy = Sputnik(color, spawn[0] + random.randint(0,300)-100, spawn[1] + random.randint(0,600)-300, planet, is_ai=True)
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
                #print "%s team %d deaths" % (self.name, self.deaths)
                guy.team_notice_dead = False
            guy.affected(self.planet.m, self.planet.x, self.planet.y)
            guy.step()
            if guy.frags > self.maxfrags:
                self.maxfrags = guy.frags

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
        print "%d pieces of hell generated" % cnt
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
        if len(self.debris) <= self.min:
            if random.randint(0, 220) == 0:
                self.generate()

class SimpleStats():
    def __init__(self, team1, team2, player):
        self.team1 = team1
        self.team2 = team2
        self.player = player

        self.font = pygame.font.Font(STATS_FONT, 18)
        
        self.bg = Surface((350,160), flags=SRCALPHA)


    def draw(self, screen):
        string1 = "%s: %d" % (self.team1.name, self.team2.deaths)
        string2 = "%s: %d" % (self.team2.name, self.team1.deaths)
        string3 = "You: %d frags, %d deaths" % (self.player.frags, self.player.deaths)
        string4 = "Fuel: %.4f, ammo %d, mass %.2f" % (self.player.fuel, self.player.ammo, self.player.m)
        if self.player.spawned:
            string5 = "Alive for %.2fs, record %.2fs" % ((pygame.time.get_ticks() - self.player.spawntime)/1000.0, self.player.max_alive/1000.0)
            if self.player.apo >= self.player.planet.r2:
                string7 = "     WARNING: ORBIT TOO HIGH!"
                sprite7 = self.font.render(string7, True, Color("#DD0000"))
            elif self.player.peri <= self.player.planet.r:
                string7 = "     WARNING: ORBIT TOO LOW!"
                sprite7 = self.font.render(string7, True, Color("#DD0000"))
            else:
                string7 = "             ORBIT OK"
                sprite7 = self.font.render(string7, True, Color("#007700"))
        else:
            string5 = "Orbited %.2fs, record %.2fs" % ((self.player.deathtime - self.player.spawntime)/1000.0, self.player.max_alive/1000.0)
            string7 = " "
            sprite7 = self.font.render(string7, True, Color("#DD0000"))
        string6 = "peri %d, apo %d, now %d, ano %d" % (self.player.peri, self.player.apo, self.player.height, math.degrees(self.player.anomaly))
        string6 += "º"[1]
        
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
        
class Profile():
    def __init__(self, is_player2_present=False, is_player1_ai=False, is_player2_ai=False, player1_team="Green", player2_team="Red", greenteamsize=8, redteamsize=8, debris_min=6, debris_max=20, draw_planet=False, name=""):
        self.p2 = is_player2_present
        self.p1_ai = is_player1_ai
        self.p2_ai = is_player2_ai
        self.p1_team = player1_team
        self.p2_team = player2_team
        
        mingreen = int(self.p1_team == "Green") + int(self.p2_team == "Green" and self.p2)
        minred = int(self.p1_team == "Red") + int(self.p2_team == "Red" and self.p2)
        self.green = max(mingreen,greenteamsize)
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
            self.cam2 = Camera(self.bg2)
            self.bgs = (self.bg1, self.bg2)
        else:
            self.bg1 = Surface((wwidth, wheight))
            self.bgs = (self.bg1,)
        self.cam1 = Camera(self.bg1)
        
        if self.name == "":
            pygame.display.set_caption("Orbotor")
        else:
            pygame.display.set_caption("Orbotor - %s" % self.name)
            
        self.pl = Planet(self.bgs, self.ERAD, self.MAXRAD, "planet.png" if self.draw_planet else None)
        GCD.planet = self.pl
        
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
            self.player1.set_name("[bot] Player1")
        else:
            self.player1.set_name("Player1")
            
        if self.p2:
            self.player2.is_ai = self.p2_ai
            if self.p2_ai:
                self.player2.set_name("[bot] Player2")
            else:
                self.player2.set_name("Player2")
                
        self.stats1 = SimpleStats(self.team1, self.team2, self.player1)
         
        if self.p2:
            self.stats2 = SimpleStats(self.team1, self.team2, self.player2)
             
    def game_key_listen(self, event):
        if event.type == KEYDOWN and event.key == K_F1:
            self.PROFILESTEP = True
            self.game_step()
        if not self.p1_ai:
            self.player1.catch_kb_event(event)
        if self.p2 and not self.p2_ai:
            self.player2.catch_kb_event_hotseat(event)
        self.cam1.keys_listen(event)
        if self.p2:
            self.cam2.keys_listen_hotseat(event)
            
    def game_step(self):
        if self.PROFILESTEP:
            profile.runctx("self._step()", globals(), {"self":self})
        else:
            self._step()
            
    def _step(self):
        
        self.team2.step() #todo faster better stronger
        self.team1.step()
        self.hell.step()
        
        self.player1.focus(self.cam1)
        self.cam1.step()
        if self.p2:
            self.player2.focus(self.cam2)
            self.cam2.step()
        
        GCD.step()
        
            
    def game_draw(self):
        if self.PROFILESTEP:
            profile.runctx("self._draw()", globals(), {"self":self})
            self.PROFILESTEP = False
        else:
            self._draw()
            
    def _draw(self):
        clock.tick(60)
        
        tup =  [self.pl,] + self.team1.objectslist() + self.team2.objectslist() + self.hell.objectslist() + self.pl.cities
        tup = tuple(tup)
        newco = self.cam1.translate_coords(*tup)
        for obj in newco:
            obj[0].draw(self.bg1, int(obj[1]), int(obj[2]), obj[3], obj[4])
        if self.p2:
            newco = self.cam2.translate_coords(*tup)
            for obj in newco:
                obj[0].draw(self.bg2, int(obj[1]), int(obj[2]), obj[3], obj[4])

        self.stats1.draw(self.bg1)
        self.screen.blit(self.bg1, (0, 0))
        if self.p2:
            self.stats2.draw(self.bg2)
            self.screen.blit(self.bg2, (0, wheight/2))
        
        pygame.display.update()
        
def DefaultProfile(draw_planet, hell):
    return Profile(draw_planet=draw_planet, debris_min=hell[0], debris_max=hell[1])

def HotseatProfile(draw_planet, hell):
    return Profile(is_player2_present=True, draw_planet=draw_planet, debris_min=hell[0], debris_max=hell[1])

def RivalProfile(draw_planet, hell):
    return Profile(is_player2_present=True, is_player2_ai=True, draw_planet=draw_planet, debris_min=hell[0], debris_max=hell[1])

def CoopProfile(draw_planet, hell):
    return Profile(is_player2_present=True, player2_team="Green", draw_planet=draw_planet, debris_min=hell[0], debris_max=hell[1])

def SpectateProfile(draw_planet, hell):
    return Profile(is_player1_ai=True, draw_planet=draw_planet, debris_min=hell[0], debris_max=hell[1])

def SurvivalProfile(draw_planet):
    return Profile(draw_planet=draw_planet, debris_min=35, debris_max=70, greenteamsize=1, redteamsize=0)

def CoopSurvivalProfile(draw_planet):
    return Profile(is_player2_present=True, player2_team="Green", draw_planet=draw_planet, debris_min=35, debris_max=70, greenteamsize=2, redteamsize=0)

def main(profile):
    profile.game_init()

    while 1:
        for e in pygame.event.get():
            if e.type == QUIT:
                 pygame.quit()
                 #exit()
            elif e.type == profile.UPDAE_GAME:
                profile.game_step()
            elif e.type == KEYDOWN or e.type == KEYUP:
                profile.game_key_listen(e)
        
        profile.game_draw()



if __name__ == "__main__":
    sys.argv = ["--lesshell","--coop"]
    if "--experimental" in sys.argv:
        draw_planet=True
    else:
        draw_planet=False
    if "--funbots" in sys.argv:
        bot_names = bot_names[:12] + ['Realer09', 'AndreyWasHere', 'PelMen', 'Monodictor']
        random.shuffle(bot_names)
    if "--nohell" in sys.argv:
        hell = (0, 0)
    elif "--lesshell" in sys.argv:
        hell = (2, 8)
    else:
        hell = (6, 20)
    if "--hotseat" in sys.argv:
        main(HotseatProfile(draw_planet, hell))
    if "--rival" in sys.argv:
        main(RivalProfile(draw_planet, hell))
    elif "--coop" in sys.argv:
        main(CoopProfile(draw_planet, hell))
    elif "--survival" in sys.argv:
        MAX_FUEL = 32
        MAX_AMMO = 0
        main(SurvivalProfile(draw_planet))
    elif "--coop-survival" in sys.argv:
        MAX_FUEL = 32
        MAX_AMMO = 0
        main(CoopSurvivalProfile(draw_planet))
    elif "--spectate" in sys.argv:
        main(SpectateProfile(draw_planet, hell))
    elif "--help" in sys.argv:
        print """
                 game options: --hotseat, --coop, --spectate,
                               --survival or --coop-survival;
                               --rival for debug purposes
                 gameplay options: --nohell or --lesshell (doesnt work in survival)
                 graphics options: --experimental
                 
                 Controls: WSAD, QE-strafe, R-kill rotation, T-selfdestroy,
                           left shift: turbo forward, ZXC - turbo-strafe,
                           1 - zoom in, 2 zoom out, 3 reset zoom
                           Space - shoot
                           
                 2nd player:  IJKL, UO-strafe, P-kill rotation, H-selfdestroy,
                              right shift: turbo forward, N,. - turbo-strafe,
                              8 - zoom in, 9 zoom out, 0 reset zoom
                              Enter - shoot
                              
                 F1 - output performance of 1 step to console\n"""
    else:
        main(DefaultProfile(draw_planet, hell))
