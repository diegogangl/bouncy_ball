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


def handler(radius, fill_color, modal):
    """ Draw the ball """

    position = modal._position

    glossy_position = (position[0] + radius/2, position[1] + radius/2)
    body_position = (position[0] + radius*0.1, position[1] + radius*0.1)

    shadow = circle(radius, position)
    body = circle(radius/1.2, body_position)
    glossy = circle(radius/5, glossy_position)

    draw(shadow, color(fill_color, -0.25))
    draw(body, fill_color)
    draw(glossy, color(fill_color, 0.8))
    draw(shadow, color(fill_color, -0.5), fill=False)

    # restore opengl defaults
    bgl.glLineWidth(1)
    bgl.glDisable(bgl.GL_BLEND)
    bgl.glColor4f(0.0, 0.0, 0.0, 1.0)


# ------------------------------------------------------------------------------
# Drawing
# ------------------------------------------------------------------------------

def color(color, offset): 
    """ Darken or ligthen a color """

    return tuple([value + offset for value in color])


def draw(func, color, fill=True):
    """ Draw an object using a function """

    gl_type = bgl.GL_POLYGON if fill else bgl.GL_LINE_LOOP

    bgl.glColor3f(*color)
    bgl.glLineWidth(4)
    bgl.glBegin(gl_type)

    func()

    bgl.glEnd()


def circle(radius, position):
    """ Return a circle drawing function """

    segments = int(1000 * math.sqrt(radius))
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


# ------------------------------------------------------------------------------
# Physics
# ------------------------------------------------------------------------------

def move(position, velocity):
    """ Move the ball """

    GRAVITY = 0.5
    RESTITUTION = 0.9

    new_x = position[0] + (velocity[0] * -1/60)
    new_y = position[1] + (velocity[1] * -1/60)

    # The area height includes the headers, remove their height
    # to bounce off them
    max_y = bpy.context.area.height - 24
    max_x = bpy.context.area.width

    if new_y - 50 < 0:
        new_y = 50
        new_velocity = (velocity[0], (velocity[1] * -RESTITUTION) + GRAVITY)
    elif new_y + 50 > max_y:
        new_y = max_y - 50
        new_velocity = (velocity[0], (velocity[1] * -RESTITUTION) + GRAVITY)
    else:
        new_velocity = (velocity[0], velocity[1] + GRAVITY)

    return (new_x, new_y), new_velocity
