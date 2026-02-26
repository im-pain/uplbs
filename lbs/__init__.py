# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTIBILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

bl_info = {
    "name" : "Lightning Boy Shader",
    "author" : "Lightning Boy Studio, Kolupsy",
    "description" : "by vfxmed.com A layer-based shader system to create various NPR styles.",
    "blender" : (2, 93, 0),
    "version" : (2, 1, 3),
    "location" : "Shader Editor (N to access panel, Shift-A to create nodes)",
    "warning" : "",
    "category" : "Material",
    "doc_url" : "https://drive.google.com/file/d/131k--yCLnV511q81ZMFMNwKq8yxh9W5A/view?usp=sharing"
}

import bpy
from bpy.props import *

from . import (
    cleanup,
    shader_panel,
    operators,
    node_category,
    utils,
    updater,
)
from .nodes import (
    base_node,
    color_node,
    node_utils,
    shader_node,
    texture_node
)
all_modules = [
    base_node,
    color_node,
    node_utils,
    shader_node,
    texture_node,
    cleanup,
    shader_panel,
    operators,
    node_category,
    utils,
    updater,
]

addon_keymaps = [ ]

def register_classes( register, debug = False ):

    func = getattr( bpy.utils, 'register_class' if register else 'unregister_class' )
    for m in all_modules:
        if hasattr( m, 'get_classes' ):
            for c in m.get_classes( ):
                if debug:
                    try:
                        print( f'importing from "{m.__name__}": {c.__name__}.')
                    except:
                        print( f'Class in "{m.__name__}" has no name.')
                func( c )

def register_keymap( name, space_type, cls, event, value ):
    global addon_keymaps
    kc = bpy.context.window_manager.keyconfigs.addon
    km = kc.keymaps.new(name = name, space_type = space_type )
    kmi = km.keymap_items.new( idname = cls.bl_idname, type = event, value = value )
    addon_keymaps.append( (km, kmi ))

def unregister_keymap( ):
    global addon_keymaps
    for km, kmi in addon_keymaps:
        km.keymap_items.remove( kmi )
    addon_keymaps.clear( )

def register( ):

    register_classes( True )
    register_keymap( "Node Editor", "NODE_EDITOR", operators.NODE_OT_lbs_toggle_advanced, "TAB", "PRESS" )
    register_keymap( "Node Editor", "NODE_EDITOR", operators.NODE_OT_lbs_toggle_closed, "H", "PRESS" )
    node_category.register_category( True )
    utils.register_node_tree_object( True )
    utils.register_get_all_nodes( True )
    cleanup.register( True )

def unregister( ):

    register_classes( False )
    unregister_keymap( )
    node_category.register_category( False )
    utils.register_node_tree_object( False )
    utils.register_get_all_nodes( False )
    cleanup.register( False )