# -*- coding: utf-8 -*-

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

from orbotor.gameprofile import *


def main(profile):
    profile.game_init()

    while 1:
        for e in pygame.event.get():
            if e.type == QUIT:
                pygame.quit()
                # exit()
            elif e.type == profile.UPDAE_GAME:
                profile.game_step()
            elif e.type == KEYDOWN or e.type == KEYUP:
                profile.game_key_listen(e)
        
        profile.game_draw()


if __name__ == "__main__":
    # sys.argv = ["--lesshell","--hotseat"]
    if "--experimental" in sys.argv:
        draw_planet = True
    else:
        draw_planet = False
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
                              
                 F1, F2 - developer outputs to the console
                 F5 - turn sound on/off\n"""
    else:
        main(DefaultProfile(draw_planet, hell))
