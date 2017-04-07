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


def draw(position):
    """ Draw the ball """

    radius = 50
    segments = 360*10
    fill_color = (1, 0, 0)
    line_color = tuple([value - 0.5 for value in fill_color])

    draw_circle(fill_color, radius, position, segments)
    draw_circle(line_color, radius, position, segments, 4, False)

    # restore opengl defaults
    bgl.glLineWidth(1)
    bgl.glDisable(bgl.GL_BLEND)
    bgl.glColor4f(0.0, 0.0, 0.0, 1.0)


def draw_circle(color, radius, position, segments, line=4, fill=True):

    theta = 2 * math.pi / segments
    tangential_factor = math.tan(theta)
    radial_factor = math.cos(theta)
    gl_type = bgl.GL_POLYGON if fill else bgl.GL_LINE_LOOP

    x = radius
    y = 0

    bgl.glColor3f(*color)
    bgl.glLineWidth(line)
    bgl.glBegin(gl_type)

    for i in range(segments):
        bgl.glVertex2f(x + position[0], y + position[1])

        x = (x + (-y * tangential_factor)) * radial_factor
        y = (y + (x * tangential_factor)) * radial_factor

    bgl.glEnd()

