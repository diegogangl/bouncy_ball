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

import os
import pkgutil
import importlib

from time import time

bl_info = {
    "name": "Bouncy Ball",
    "description": "Yup, just a ball that bounces around",
    "author": "Diego Gangl <diego@sinestesia.co>",
    "version": (1, 0, 0),
    "BLENDER": (2, 70, 0),
    "location": "3D View",
    "warning": "",
    "link": "",
    "tracker_url": "",
    "category": "3D View"
}


# ------------------------------------------------------------------------------
# PACKAGE SETUP
# ------------------------------------------------------------------------------
def setup_addon_modules(path, package_name, reload):
    """
    Imports and reloads all modules in this addon.

    path -- __path__ from __init__.py
    package_name -- __name__ from __init__.py
    """
    def get_submodule_names(path=path[0], root=""):
        module_names = []
        for importer, module_name, is_package in pkgutil.iter_modules([path]):
            if is_package:
                sub_path = os.path.join(path, module_name)
                sub_root = root + module_name + "."
                module_names.extend(get_submodule_names(sub_path, sub_root))
            else:
                module_names.append(root + module_name)
        return module_names

    def import_submodules(names):
        modules = []
        for name in names:
            if name == 'batch_render.dispatcher':
                continue

            modules.append(importlib.import_module("." + name, package_name))
        return modules

    def reload_modules(modules):
        for module in modules:
            importlib.reload(module)

    names = get_submodule_names()
    modules = import_submodules(names)
    if reload:
        reload_modules(modules)
    return modules


modules = setup_addon_modules(__path__, __name__, "bpy" in locals())
import bpy
from . import ball


# ------------------------------------------------------------------------------
# OPERATOR
# ------------------------------------------------------------------------------

add_handler = bpy.types.SpaceView3D.draw_handler_add
remove_handler = bpy.types.SpaceView3D.draw_handler_remove
add_timer = bpy.context.window_manager.event_timer_add

class BouncyBall(bpy.types.Operator):
    """Create a ball that bounces around the 3D View"""

    bl_idname = "view3d.bouncy_ball"
    bl_label = "Bouncy Ball"

    def modal(self, context, event):
        context.area.tag_redraw()

        if event.type == 'TIMER':
            time_delta = self._time - time()
            self._position = ball.move(self._position, time_delta)
            self._time = time()

        elif event.type == 'LEFTMOUSE':
            pass

        elif event.type == 'ESC':
            remove_handler(self._handle, 'WINDOW')
            return {'CANCELLED'}

        return {'RUNNING_MODAL'}

    def invoke(self, context, event):
        if context.area.type == 'VIEW_3D':

            self._position = (context.area.width / 2, context.area.height / 2)
            self._time = time()
            settings = (50, (1, 0, 0), 360*5,  self)

            self._timer = add_timer(1/60, context.window)

            self._handle = add_handler(ball.handler, settings,
                                       'WINDOW', 'POST_PIXEL')

            context.window_manager.modal_handler_add(self)
            return {'RUNNING_MODAL'}
        else:
            self.report({'WARNING'}, "View3D not found, cannot bounce")
            return {'CANCELLED'}


def register():
    bpy.utils.register_class(BouncyBall)


def unregister():
    bpy.utils.unregister_class(BouncyBall)


if __name__ == "__main__":
    register()
