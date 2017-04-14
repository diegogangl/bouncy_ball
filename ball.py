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
from time import time


Settings = namedtuple('Settings',
                      ('radius', 'fill_color',
                       'gravity', 'restitution'))


def handler(settings, state):
    """ Draw the ball """

    position = state['position']
    dragged = state['first_drag']

    bgl.glEnable(bgl.GL_MULTISAMPLE)
    bgl.glEnable(bgl.GL_LINE_SMOOTH)

    # Shadow
    draw(circle(settings.radius, position),
         settings.fill_color - 0.25)

    # Body
    draw(circle(settings.radius / 1.2, position + settings.radius / 10),
         settings.fill_color)

    # Glossy reflection
    draw(circle(settings.radius / 5, position + settings.radius / 2),
         settings.fill_color + 0.8)

    # Outline
    draw(circle(settings.radius, position),
         settings.fill_color - 0.5, fill=False)

    text('Press ESC to stop bouncing', 
         (20, bpy.context.area.height - 85), 
         (0.9, 0.9, 0.9))

    if not dragged:
        text_position = position + settings.radius + 5
        balloon_color = (1, 1, 1)

        # Speech balloon
        draw(rectangle(text_position - 10, (155, 30)), balloon_color)
        draw(triangle(text_position + (5, -10), 20), balloon_color)

        text('Drag me to start bouncing!', text_position)

    # restore opengl defaults
    bgl.glLineWidth(1)
    bgl.glDisable(bgl.GL_BLEND)
    bgl.glColor4f(0.0, 0.0, 0.0, 1.0)


# ------------------------------------------------------------------------------
# Drawing
# ------------------------------------------------------------------------------


def draw(vertices, color, fill=True):
    """ Draw an object """

    gl_type = bgl.GL_POLYGON if fill else bgl.GL_LINE_LOOP

    bgl.glColor3f(*color)
    bgl.glLineWidth(4)
    bgl.glBegin(gl_type)

    [bgl.glVertex2f(*vertex) for vertex in vertices]

    bgl.glEnd()


def circle(radius, position):
    """ Return vertex list for a circle"""

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
    """ Return vertex list for a rectangle"""

    return [
            (position[0], position[1]),
            (position[0] + size[0], position[1]),
            (position[0] + size[0], position[1] + size[1]),
            (position[0], position[1] + size[1]),
           ]


def triangle(position, size):
    """ Return vertex list for a triangle"""

    return [
            (position[0], position[1]),
            (position[0] + size, position[1]),
            (position[0], position[1] - size),
           ]


def text(line, position, color=(0.1, 0.1, 0.1)):
    """ Draw text on screen """

    bgl.glColor3f(*color)
    blf.position(0, position[0], position[1], 0)
    blf.draw(0, line)


# ------------------------------------------------------------------------------
# Physics
# ------------------------------------------------------------------------------

def physics_setup(settings):
    """ Setup physics and return the move function """

    # The area height includes the headers, remove their height
    # to bounce off them
    max_y = bpy.context.area.height - 24
    max_x = bpy.context.area.width

    restitution = settings.restitution
    gravity = settings.gravity
    radius = settings.radius

    velocity = np.zeros(2)

    def move(position, custom_velocity=None):
        """ Move the ball """

        if custom_velocity is None:
            nonlocal velocity
        else:
            velocity = custom_velocity

        target = position + (velocity * -1/60)
        bounce_x = False
        bounce_y = False

        if target[1] - radius < 0:
            target[1] = radius
            bounce_y = True
        elif target[1] + radius > max_y:
            target[1] = max_y - radius
            bounce_y = True

        velocity[1] = velocity[1] * -restitution if bounce_y else velocity[1]
        velocity[1] += gravity

        if target[0] - radius < 0:
            target[0] = radius
            bounce_x = True
        elif target[0] + radius > max_x:
            target[0] = max_x - radius
            bounce_x = True

        velocity[0] = velocity[0] * -restitution if bounce_x else velocity[0]

        return target

    return move


def drag_start(settings, origin):
    """ Draggin setup """

    min_xy = settings.radius
    max_x = bpy.context.area.width - 50
    max_y = bpy.context.area.height - 50 - 24

    start_time = time()

    def drag(event):
        """ Drag the ball while clamping """

        drag_x = min(max(event.mouse_region_x, min_xy), max_x)
        drag_y = min(max(event.mouse_region_y, min_xy), max_y)

        return np.array((drag_x, drag_y))

    def release(position):
        """ Calculate a target and velocity based on dragging """

        time_delta = time() - start_time
        space_delta = origin - position

        return space_delta * 1/time_delta

    return (drag, release)

