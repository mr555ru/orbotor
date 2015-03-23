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

from pygame import *

from static_functions import *
from gcd import GlobalCollisionDetector
from soundsystem import SoundSystem
import camera
import quadtree

                     
GCD_Singleton = GlobalCollisionDetector()
SoundSystem_Singleton = SoundSystem()


class Orbitable(camera.Camerable, quadtree.QuadTreeObject):
    """Orbitable: any physical object that orbits the planet.
       Implements Camerable interface, so it can be visible;
       Implements QuadTreeObject interface, so it can collide with things.
       
       Public methods:
       
       affected(mass, x, y): advance it's velocity with planet's G force with mass and x,y coords.
       initialspeed(mass, x, y): change velocity to have circular orbit around planet with mass and x,y coords.
       set_drawdelta(): use this after creating an actual sprite to counter the fact that by default pygame
                        draws sprite's upper left corner at given coords.
       focus(camera): focus camera on self.
       step(): perform one logical step (involves movement and whatnot). Usually to be overriden.
       draw(screen, t_x, t_y, t_ang, t_zoom): draw it's sprite on screen with these coords,
                                              this angle and this zoom. Inherited from Camerable.
       get_collision(other, vel, ang): perform logic after collision with other (expected to be another Orbitable)
                                       with impact velocity vel and angle ang.
                                       Usually to be overriden.
       get_too_close(): perform logic after falling on planet. To be overriden.
       get_too_far(): perform logic after leaving the orbit. To be overriden.
       way_too_far(): perform logic after leaving orbit really much. Bug-bearing function for objects
                      that do not destroy themselves immediately. Usually is not expected to be overriden.
       exclude(): ask GlobalCollisionDetector to exclude itself from collision processing. Usually
                  called at destroying of an object. Not to be overriden.
       
       
       Instance variables:
       
       x, y: coordinates
       dx, dy: linear velocity
       ang: angle
       dang: angular velocity
       m: mass
       r: radius that is used at collision detection
       colliding: boolean - can object collide
       nocollide: counter, counts how many steps left for initial nocollide state
       maxnocollide: maximum of steps for initial nocollide state. can be used if object respawns
       repr: object type identifier for processing on get_collision (what is the impact object), string
       GCD_REMOVE_ME_FLAG: boolean flag that is raised when object asks to be removed. GCD requires these.
       sprite - sprite object that is used as visual representation
       derivative - new sprite that is created on each draw after transforming sprite
       sprite_off_x, sprite_off_y: offsets between sprite geometrical center and implied actual rotation center
       drawdx, drawdy: offsets that are used to set center of a sprite at object coords (because by default)
                       pygame draws left upper corner at coords)
       is_circle: is sprite a circle. If it is then it's not gonna spend time on rotating it.
       bounds: these are used for QuadTreeObject
       soundsys: pointer at SoundSystem_Singleton
       """
    def __init__(self, x, y, r, m, ang=0, dang=0, dx=0, dy=0, nocollidesteps=0, colliding=True):
        """Constructor.
        Keyword arguments:
        x, y: default coordinates.
        r: radius (for collision detection)
        m: mass (for impacts)
        ang: default angle of object
        dang: angular velocity (ang += dang per step)
        dx, dy: linear velocity
        nocollidesteps: how many steps after creation it will not collide
        colliding: does it collide.
        """
        global GCD_Singleton
        quadtree.QuadTreeObject.__init__(self)
        camera.Camerable.__init__(self)
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
        GCD_Singleton.be_added(self)
        self.GCD_REMOVE_ME_FLAG = False
        self.sprite = None  # Surface
        self.derivative = None
        self.nocollide = nocollidesteps
        self.maxnocollide = nocollidesteps
        
        self.sprite_off_x = 0
        self.sprite_off_y = 0
        
        self.drawdx = 0
        self.drawdy = 0
        self.is_circle = False
        
        self.soundsys = SoundSystem_Singleton
        self.bounds = None
        
    def set_drawdelta(self):
        """Set drawdx, drawdy.
        Use this after you created the sprite to counter the fact that by default pygame
        draws sprite's upper left corner at given coords.
        """
        self.drawdx = self.sprite.get_width()/2
        self.drawdy = self.sprite.get_height()/2
        
    def affected(self, mass, x, y):
        """Be affected with gravity of planet with mass and x,y coords."""
        R = math.sqrt((x-self.x)**2 + (y-self.y)**2)
        a = G*mass/(R**2)

        ax = a * (x-self.x)/R
        ay = a * (y-self.y)/R

        self.dx += ax
        self.dy += ay

    def initialspeed(self, mass, x, y):
        """Use this at creation so objects are going to have circular orbit
        around planet with mass and x,y coords.
        """
        R = math.sqrt((x-self.x)**2 + (y-self.y)**2)
        aang = math.atan2(-(y-self.y), x-self.x)
        vang = aang+math.pi/2
        v = math.sqrt(G*mass/(R))

        self.dx = v * math.cos(vang)
        self.dy = - v * math.sin(vang)
        
    def focus(self, camera):
        """Focus camera on self."""
        camera.x = self.x
        camera.y = self.y
        camera.ang = self.ang-math.pi/2
        
    def step(self):
        """Logical step of the program."""
        quadtree.QuadTreeObject.step(self)
        self.x += self.dx
        self.y += self.dy
        self.ang += self.dang
        if self.nocollide > 1:
            self.nocollide -= 1
        elif self.nocollide == 1:
            self.nocollide = 0
            self.colliding = True
        
    def draw(self, screen, t_x, t_y, t_ang, t_zoom):
        """Draw the object on given screen (anything that you can blit the sprite on)
        with given screen's coords, angle and zoom. Inherited from Camerable.
        """
        self.derivative, offsets = better_rotozoom(self.sprite, t_ang, t_zoom,
                                                   (self.sprite_off_x, self.sprite_off_y),
                                                   self.is_circle)
        screen.blit(self.derivative, (t_x-self.drawdx*t_zoom-offsets[0],
                                      t_y-self.drawdy*t_zoom-offsets[1]))

    def get_collision(self, other, vel, ang):
        """Used by GlobalCollisionDetector when it notices a collision.
           other - object with which happened the collision,
           vel - velocity of impact
           ang - angle of impact
        """
        self.dx += other.m/float(self.m) * vel * math.cos(ang)
        self.dy += other.m/float(self.m) * vel * math.sin(ang)

    def get_too_close(self):
        """Called when orbitable falls on planet."""
        pass

    def get_too_far(self):
        """Called when orbitable leaves the orbit."""
        pass
    
    def way_too_far(self):
        """Perform logic after leaving orbit really much. Bug-bearing function for objects
        that do not destroy themselves immediately. """
        self.exclude()

    def exclude(self):
        """Ask GCD to be excluded from collision detection on next step.
        Called on destroy.
        """
        self.colliding = False
        self.GCD_REMOVE_ME_FLAG = True
