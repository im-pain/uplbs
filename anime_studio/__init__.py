# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

bl_info = {
    "name" : "QWN's Anime Super Studio",
    "author" : "QWN",
    "description" : "A Blender addon for QWN's Anime Super Studio shader, following the Lightning Boy Shader architecture.",
    "blender" : ( 4, 0, 0 ),
    "version" : ( 1, 0, 0 ),
    "location" : "Shader Editor (Shift-A to create nodes)",
    "warning" : "Requires KK_Template_Shader.blend placed in the addon lib folder",
    "category" : "Material",
}

import bpy

from . import (
    cleanup,
    operators,
    node_category,
    utils,
)
from .nodes import (
    shader_node,
    node_utils,
)

all_modules = [
    shader_node,
    cleanup,
    operators,
    node_category,
]

def register_classes( register ):
    func = getattr( bpy.utils, 'register_class' if register else 'unregister_class' )
    for m in all_modules:
        if hasattr( m, 'get_classes' ):
            for c in m.get_classes( ):
                func( c )

def register( ):
    register_classes( True )
    node_category.register_category( True )
    utils.register_get_all_nodes( True )
    cleanup.register( True )

def unregister( ):
    register_classes( False )
    node_category.register_category( False )
    utils.register_get_all_nodes( False )
    cleanup.register( False )
