import bpy
from nodeitems_utils import NodeCategory, NodeItem, register_node_categories, unregister_node_categories
from .nodes.shader_node import QWNAnimeSuperStudioNode
from .utils import NODEGROUP_NAME

class AnimeStudioNodeCategory( NodeCategory ):

    @classmethod
    def poll( cls, context ):
        return (context.space_data.type == 'NODE_EDITOR' and
                context.space_data.tree_type == 'ShaderNodeTree')

def anime_studio_node_items( context ):
    yield NodeItem(
        QWNAnimeSuperStudioNode.bl_idname,
        label = NODEGROUP_NAME,
    )

def register_category( register ):
    if register:
        register_node_categories(
            "AnimeStudioNodes",
            [ AnimeStudioNodeCategory( "AnimeStudioNodes", "Anime Studio", items = anime_studio_node_items ) ]
        )
    else:
        unregister_node_categories( "AnimeStudioNodes" )
