import bpy, mathutils
from bpy.props import *
from .. import bl_info
from .. utils import lbs_lib
from .. operators import *
from .. operators import draw_operator as op

#UTIL FUNCTIONS

def group_is_older_version( group ):

    return tuple( group.get( 'lbs_version', ( 0, 0, 0 ))) < bl_info['version']

def import_node_group( init_name ):
    with bpy.data.libraries.load( lbs_lib, link = False ) as ( data_from, data_to ):
            data_to.node_groups.append( init_name )
    group = bpy.data.node_groups[ init_name ]
    adjust_node_group( group )
    return group

def import_image( name ):
    with bpy.data.libraries.load( lbs_lib, link = False ) as ( data_from, data_to ):
        data_to.images.append( name )
    return bpy.data.images[ name ]

def adjust_node_group( group, protected_override = True ):
    #DETERMINE TYPE
    lbs_type = "Normal"
    if group.name == ".Lightning Boy Shader":
        lbs_type = "Base Shader"
        adjust_node_group( group.nodes["global_settings"].node_tree, protected_override = False )
    if group.name == ".Solidify Outline":
        lbs_type = "Outline Shader"
    elif group.name == ".Color":
        lbs_type = "Color Node"
    #SET CUSTOM PROPERTIES
    group["lbs_node"] = lbs_type
    group["lbs_version"] = bl_info["version"]
    group["lbs_protected"] = protected_override
    group["lbs_original_name"] = group.name
    group["lbs_has_global_settings"] = 0
    global_frames = [ x for x in group.nodes if (x.bl_idname == "NodeFrame" and x.use_custom_color) or "driven" in x.name ]
    special_frames = [ x for x in global_frames if x.color == mathutils.Color((0,1,0))]
    if len(special_frames):
        group["lbs_has_global_settings"] = special_frames[0].name
    elif len( global_frames ):
        group["lbs_has_global_settings"] = 1
    defaultD = {
        ".Spherical Gradient*":"lbs_default_spherical", 
        ".Linear Gradient*": "lbs_default_linear", 
        ".Virtual Sun Light*":"lbs_default_virtual_sun",
        ".Virtual Point Light*":"lbs_default_virtual_point",
        ".Virtual Spot Light*":"lbs_default_virtual_spot"}
    if group.name in defaultD:
        try:
            group.lbs_ref_object = [x for x in bpy.data.objects if defaultD[group.name] in x ][0]
        except:
            pass
    group.use_fake_user = True
    return group

def get_material_from_node( node ):

    mats = [x for x in bpy.data.materials if x.node_tree != None and x.node_tree.as_pointer( ) == node.id_data.as_pointer( )]
    if not len( mats ):
        return None
    else:
        return mats[0]

#UTIL CLASSES

class NODE_MT_lbs_group_children( bpy.types.Menu ):
    bl_idname = "NODE_MT_lbs_group_children"
    bl_label = "Node Instances"

    @classmethod
    def poll( cls, context ):
        return (context.space_data.type == 'NODE_EDITOR' and
                context.space_data.tree_type == 'ShaderNodeTree')

    def draw( self, context ):
        layout = self.layout
        node = context.active_node
        layout.context_pointer_set( 'active_node' , node )
        if node.bl_idname == "LBSShaderNode":
            original_name = node.node_tree.nodes[ "global_settings" ].node_tree[ "lbs_original_name" ]
        else:
            original_name = node.node_tree[ "lbs_original_name" ]
        for ng in (x for x in bpy.data.node_groups if "lbs_original_name" in x and x["lbs_original_name"] == original_name ):
            suffix = ng.name[ len( original_name )+2 : -1 ]
            o = layout.operator( "node.lbs_new_group_child", text = ng.name[1:] )
            o.suffix = suffix

def get_classes( ):

    yield NODE_MT_lbs_group_children