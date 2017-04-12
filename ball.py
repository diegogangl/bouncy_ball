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
import blf

import numpy as np
from collections import namedtuple


Settings = namedtuple('Settings',
                      ('radius', 'fill_color',
                       'gravity', 'restitution'))


def handler(settings, modal):
    """ Draw the ball """

    position = modal._position
    dragged = modal._first_drag

    glossy_position = position + settings.radius / 2

    body_position = position + settings.radius / 10

    shadow = circle(settings.radius, position)
    body = circle(settings.radius / 1.2, body_position)
    glossy = circle(settings.radius / 5, glossy_position)

    bgl.glEnable(bgl.GL_MULTISAMPLE)
    bgl.glEnable(bgl.GL_LINE_SMOOTH)

    draw(shadow, settings.fill_color - 0.25)
    draw(body, settings.fill_color)
    draw(glossy, settings.fill_color + 0.8)
    draw(shadow, settings.fill_color - 0.5, fill=False)

    if not dragged:
        text_position = position + settings.radius + 5

        speech_rectangle_position = text_position - 10
        speech_triangle_position = text_position + (5, -10)
        speech_rectangle = rectangle(speech_rectangle_position, (155, 30))
        speech_triangle = triangle(speech_triangle_position, 20)

        draw(speech_rectangle, (1, 1, 1))
        draw(speech_triangle, (1, 1, 1))
        text('Drag me to start bouncing!', text_position)

    # restore opengl defaults
    bgl.glLineWidth(1)
    bgl.glDisable(bgl.GL_BLEND)
    bgl.glColor4f(0.0, 0.0, 0.0, 1.0)


# ------------------------------------------------------------------------------
# Drawing
# ------------------------------------------------------------------------------


def draw(vertices, color, fill=True):
    """ Draw an object using a function """

    gl_type = bgl.GL_POLYGON if fill else bgl.GL_LINE_LOOP

    bgl.glColor3f(*color)
    bgl.glLineWidth(4)
    bgl.glBegin(gl_type)

    [bgl.glVertex2f(*vertex) for vertex in vertices]

    bgl.glEnd()


def circle(radius, position):
    """ Return a circle drawing function """

    segments = int(1000 * math.sqrt(radius))
    theta = 2 * math.pi / segments
    tangential_factor = math.tan(theta)
    radial_factor = math.cos(theta)

    x = radius
    y = 0
    vertices = []

    for i in range(segments):
        vertices.append((x + position[0], y + position[1]))

        x = (x + (-y * tangential_factor)) * radial_factor
        y = (y + (x * tangential_factor)) * radial_factor

    return vertices


def rectangle(position, size):
    """ Return a rectangle drawing function """

    return [
            (position[0], position[1]),
            (position[0] + size[0], position[1]),
            (position[0] + size[0], position[1] + size[1]),
            (position[0], position[1] + size[1]),
           ]


def triangle(position, size):
    """ Return a triangle drawing funciton """

    return [
            (position[0], position[1]),
            (position[0] + size, position[1]),
            (position[0], position[1] - size),
           ]



def text(line, position):
    """ Draw text on screen """

    bgl.glColor3f(0.2, 0.2, 0.2)
    blf.position(0, position[0], position[1], 0)
    blf.draw(0, line)


# ------------------------------------------------------------------------------
# Physics
# ------------------------------------------------------------------------------

def move(settings, position, velocity):
    """ Move the ball """

    new_x = position[0] + (velocity[0] * -1/60)
    new_y = position[1] + (velocity[1] * -1/60)

    # The area height includes the headers, remove their height
    # to bounce off them
    max_y = bpy.context.area.height - 24
    max_x = bpy.context.area.width

    if new_y - 50 < 0:
        new_y = 50
        new_velocity_y = (velocity[1] * -settings.restitution) + settings.gravity
    elif new_y + 50 > max_y:
        new_y = max_y - 50
        new_velocity_y = (velocity[1] * -settings.restitution) + settings.gravity
    else:
        new_velocity_y = velocity[1] + settings.gravity

    if new_x - 50 < 0:
        new_x = 50
        new_velocity_x = (velocity[0] * -settings.restitution)
    elif new_x + 50 > max_x:
        new_x = max_x - 50
        new_velocity_x = (velocity[0] * -settings.restitution)
    else:
        new_velocity_x = velocity[0] 

    new_velocity = (new_velocity_x, new_velocity_y)

    return np.array((new_x, new_y)), new_velocity
