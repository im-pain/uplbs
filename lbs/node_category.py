import bpy
from nodeitems_utils import NodeCategory, NodeItem, NodeItemCustom, register_node_categories, unregister_node_categories
from . utils import lbs_sub_groups
from .nodes.base_node import LBSBaseNode
from .nodes.color_node import LBSColorNode
from .nodes.shader_node import LBSShaderNode
from .nodes.texture_node import LBSTextureNode

class LBSNodeCategory( NodeCategory ):
    @classmethod
    def poll(cls, context):
        return (context.space_data.type == 'NODE_EDITOR' and
                context.space_data.tree_type == 'ShaderNodeTree')

def separator_item( self, layout, context ):
    layout.separator( )

def lbs_item( cls, group_name ):
    return NodeItem( cls.bl_idname, label = group_name[1:], settings = { 'initialize_group' : repr( group_name )})

def lbs_node_items( context ):

    node_list = bpy.app.driver_namespace["lbs_nodes"]
    for n in node_list:
        if n == ".Color":
            yield lbs_item( LBSColorNode, n )
        elif n == ".Lightning Boy Shader":
            yield lbs_item( LBSShaderNode, n )
        elif n in [".Matcap", ".Painterly Style", ".Ambient Occlusion (Baked)", ".Halftone Style"]:
            yield lbs_item( LBSTextureNode, n )
        elif not n in lbs_sub_groups + ["*"]:
            yield lbs_item( LBSBaseNode, n )
        elif n == '*':
            yield NodeItemCustom( draw = separator_item )

def register_category( register ):
    if register:
        register_node_categories( "LBSNodes", [ LBSNodeCategory( "LBSNodes", "LBS Nodes", items = lbs_node_items )])
    else:
        unregister_node_categories( "LBSNodes" )