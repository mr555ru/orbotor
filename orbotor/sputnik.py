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
import random
import os.path

import pygame
from pygame import *


from orbotor.static_functions import *

from orbotor.orbitable import Orbitable, GCD_Singleton
from orbotor.bullet import Bullet
from orbotor.debris import Debris, Spark
from orbotor.supply import FuelSupply, AmmoSupply
from orbotor.thruster import Thruster
from orbotor.nametag import Nametag


with open("botnames.txt", "r") as f:
    bot_names = f.readlines()
random.shuffle(bot_names)

class Sputnik(Orbitable):

    def __init__(self, c, x, y, planet, is_ai=False):
        Orbitable.__init__(self, x, y, r=8, m=15, dx=0, dy=0, ang=random.random()*2*math.pi, dang=0, nocollidesteps=20, colliding=True)
        
        GCD_Singleton.make_priority(self)
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
            if len(bot_names) == 0:
                self.name = "[bot] Bot_%d" % random.randint(1000,9999)
            else:
                self.name = "[bot] %s" % bot_names.pop()[:-1]

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
        
        self.soundsys.initsound('kill',"kill.wav")
        self.soundsys.initsound('fire',"shoot.wav")
        self.soundsys.initsound('turbo',"turbo.wav")
        self.soundsys.initsound('respawn',"respawn.wav")
        self.soundsys.initsound('noammo',"noammo.wav")
        
        self.focused = False
        
        self.respawntime = MAXRESPAWNTIME
        
    def focus(self, camera):
        Orbitable.focus(self, camera)
        self.focused = True
        
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
        if self.spawned:
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
                if self.hearable:
                    self.soundsys.playsound('fire')
            elif self.focused:
                self.soundsys.playsound('noammo')
        
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
                        dang = min_max_value(-self.max_dang*self.hull_mass*1.2/self.m, self.max_dang*self.hull_mass*1.2/self.m, (self.nearest_opponent[2]-self.ang)/5.0)
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
            if random.randint(0,10) == 0 and self.hearable:
                self.soundsys.playsound('turbo')
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
            if applyval and self.hearable:
                self.soundsys.playsound('turbo')
        elif e.key == K_LSHIFT:
            self.thrusters_on["turbo"] = applyval
            if applyval and self.hearable:
                self.soundsys.playsound('turbo')
        elif e.key == K_z:
            self.thrusters_on["turbo_left"] = applyval
            if applyval and self.hearable:
                self.soundsys.playsound('turbo')
        elif e.key == K_x:
            self.thrusters_on["turbo_back"] = applyval
            if applyval and self.hearable:
                self.soundsys.playsound('turbo')
        elif e.key == K_c:
            self.thrusters_on["turbo_right"] = applyval
            if applyval and self.hearable:
                self.soundsys.playsound('turbo')
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
            if applyval and self.hearable:
                self.soundsys.playsound('turbo')
        elif e.key == K_RSHIFT:
            self.thrusters_on["turbo"] = applyval
            if applyval and self.hearable:
                self.soundsys.playsound('turbo')
        elif e.key == K_n:
            self.thrusters_on["turbo_left"] = applyval
            if applyval and self.hearable:
                self.soundsys.playsound('turbo')
        elif e.key == K_m or e.key == K_COMMA:
            self.thrusters_on["turbo_back"] = applyval
            if applyval and self.hearable:
                self.soundsys.playsound('turbo')
        elif e.key == K_PERIOD:
            self.thrusters_on["turbo_right"] = applyval
            if applyval and self.hearable:
                self.soundsys.playsound('turbo')
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
        if not self.spawned:
            if pygame.time.get_ticks() - self.deathtime > self.respawntime:
                    self.respawn()
        self.m = self.hull_mass + self.fuel * FUEL_MASS + self.ammo * BULLET_MASS
        self.execute_thrusters()
        self.get_peri_apo()
        Orbitable.step(self)
        if self.nocollide == 1 and self.hearable:
            self.soundsys.playsound('respawn')
        
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
            child.step()
            while len(child.children) > 0:
                chichild = child.children.pop()
                self.children.append(chichild)
            if child.GCD_REMOVE_ME_FLAG:
                if child.repr == "Bullet":
                    if child.iamakiller:
                        self.frags += 1
                        child.iamakiller = False
                self.children.remove(child)
        
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
            if self.hearable:
                self.soundsys.playsound('kill')
            if self.name != " ":
                print "%s has been destroyed, reason: %s" % (self.name, reason)
            self.fuel = 0
            self.deaths += 1
            self.deathtime = pygame.time.get_ticks()
            self.respawntime = MAXRESPAWNTIME + random.randint(0, int(MAXRESPAWNTIME*0.15))
            self.colliding = False
            self.nocollide = 0
            self.team_notice_dead = True
            if not GCD_Singleton.loosening:
                for i in xrange(random.randint(2,4)):
                    self.children.append(Debris(self.x, self.y, self.dx, self.dy))
            else:
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
            if not GCD_Singleton.loosening:
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