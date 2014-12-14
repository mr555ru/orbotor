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

from orbitable import Orbitable, GCD_Singleton
from static_functions import *

class Bullet(Orbitable):
    def __init__(self, c, x, y, dx, dy, ang, ownername):
        Orbitable.__init__(self, x, y, r=2, m=BULLET_MASS, dx=0, dy=0, ang=0, dang=0, nocollidesteps=1, colliding=False)
        #self.set_bounds()
        GCD_Singleton.make_priority(self)
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