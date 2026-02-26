import bpy
from bpy.types import ShaderNodeCustomGroup
from bpy.props import *
from .node_utils import import_node_group, group_is_older_version
from ..utils import NODEGROUP_NAME

class QWNAnimeSuperStudioNode( ShaderNodeCustomGroup ):

    bl_idname = "QWNAnimeSuperStudioNode"
    bl_label = "QWN's Anime Super Studio"

    @property
    def is_anime_studio_node( self ):
        return True

    def init( self, context ):
        self.use_custom_color = True
        self.color = ( 0.1, 0.2, 0.6 )
        self.width = 240
        self._setup_node_group( )

    def _setup_node_group( self ):
        groups = bpy.data.node_groups
        name = NODEGROUP_NAME
        if name in groups:
            group = groups[ name ]
            if group_is_older_version( group ):
                group.name += '_old'
        if name not in groups:
            import_node_group( name )
        self.node_tree = groups[ name ]

    def copy( self, node ):
        # Share the protected nodegroup rather than copying it.
        self.node_tree = node.node_tree

    def free( self ):
        # Do not remove the protected shared nodegroup.
        pass

    def draw_label( self ):
        return "QWN's Anime Super Studio"

    def draw_buttons( self, context, layout ):
        pass

def get_classes( ):
    yield QWNAnimeSuperStudioNode
