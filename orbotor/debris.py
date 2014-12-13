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

from orbitable import Orbitable 
from static_functions import *

debris_collection = [imitate_debris(DEBRIS_COLORS[0], DEBRIS_COLORS[1], int(DEBRIS_R*DEBRIS_SCALING)) for i in xrange(30)]
SPARKSPRITE = create_color_circle(Color("#FFFFAA"), 2*DEBRIS_SCALING)

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
        
        self.soundsys.initsound('debris',"debris_crack.wav")
        #print self.dang

        #print "debris initiated %f %f" % (self.dx, self.dy)
        
    def draw(self, screen, t_x, t_y, t_ang, t_zoom):
        t_zoom = t_zoom/self.scaling
        self.derivative, offsets = better_rotozoom(self.sprite, t_ang, t_zoom, (self.sprite_off_x, self.sprite_off_y))
        screen.blit(self.derivative, (t_x-self.drawdx*t_zoom-offsets[0], t_y-self.drawdy*t_zoom-offsets[1]))
            

    def get_collision(self, other, vel, ang):
        if other.repr != "Spark":
            if random.randint(0,4) == 0:
                m = 0
                for i in xrange(random.randint(2, 7)):
                    m += 5
                    self.children.append(Debris(self.x, self.y, self.dx, self.dy))
                for i in xrange(random.randint(0,3)):
                    self.children.append(Spark(self.x, self.y, self.dx, self.dy, vel*other.m, ang))
                self.m = m
                Orbitable.get_collision(self, other, vel, ang)
                if self.hearable:
                    self.soundsys.playsound('debris')
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