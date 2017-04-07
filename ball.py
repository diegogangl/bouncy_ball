# ------------------------------------------------------------------------------
# LICENSE
#
# (c) Copyright Diego Gangl (januz) - 2017
# <diego@sinestesia.co>
#
# This addon is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software Foundation,
# Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
# ------------------------------------------------------------------------------
# Circle drawing algorithm from:
# http://slabode.exofire.net/circle_draw.shtml
# ------------------------------------------------------------------------------


import math

import bpy
import bgl


def handler(radius, fill_color, segments, modal):
    """ Draw the ball """

    position = modal._position
    line_color = tuple([value - 0.5 for value in fill_color])
    glossy_color = tuple([value + 0.8 for value in fill_color])
    glossy_position = (position[0] + radius/2, position[1] + radius/2.5)

    body = circle(radius, position, segments)
    glossy = circle(radius/5, glossy_position, segments)

    draw(body, fill_color)
    draw(body, line_color, False)
    draw(glossy, glossy_color)

    # restore opengl defaults
    bgl.glLineWidth(1)
    bgl.glDisable(bgl.GL_BLEND)
    bgl.glColor4f(0.0, 0.0, 0.0, 1.0)


def move(position, time_delta):
    """ Move the ball """

    velocity = 100
    new_position = (position[0], position[1] + velocity * time_delta)

    return new_position


def draw(func, color, fill=True):
    """ Draw an object using a function """

    gl_type = bgl.GL_POLYGON if fill else bgl.GL_LINE_LOOP

    bgl.glColor3f(*color)
    bgl.glLineWidth(4)
    bgl.glBegin(gl_type)

    func()

    bgl.glEnd()


def circle(radius, position, segments):
    """ Return a circle drawing function """

    theta = 2 * math.pi / segments
    tangential_factor = math.tan(theta)
    radial_factor = math.cos(theta)

    def draw():
        x = radius
        y = 0

        for i in range(segments):
            bgl.glVertex2f(x + position[0], y + position[1])

            x = (x + (-y * tangential_factor)) * radial_factor
            y = (y + (x * tangential_factor)) * radial_factor

    return draw
