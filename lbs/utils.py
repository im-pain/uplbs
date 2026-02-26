import bpy, os
from bpy.app.handlers import persistent
from bpy.props import *
from bpy.types import Object

lbs_sub_groups = [ ".LBS Layer", ".LBS Transparency Layer" ]
python_path = os.path.dirname( os.path.realpath( __file__ ))
lbs_lib = os.path.join( python_path, "lib", "lbs_library.blend" )

doc_url = "https://drive.google.com/file/d/131k--yCLnV511q81ZMFMNwKq8yxh9W5A/view?usp=sharing"

def get_lbs_world( ):

    if not "LBS World Material" in bpy.data.worlds.keys( ):
        with bpy.data.libraries.load( lbs_lib, link = False ) as ( data_from, data_to ):
            for w in data_from.worlds:
                world = w
                data_to.worlds.append( w )
    else:
        world = "LBS World Material"
    
    return bpy.data.worlds[ world ]

def import_lbs_collection( name ):

    with bpy.data.libraries.load( lbs_lib, link = False ) as ( data_from, data_to ):
        for c in data_from.collections:
            if c == name:
                data_to.collections.append( c )

def node_is_lbs( node ):
    return getattr( node, 'is_lbs_node', False )

def get_all_lbs_nodes( ):

    data = bpy.data
    for nt in [ x.node_tree for x in data.materials ] + list( data.node_groups ):
        for n in getattr( nt, 'nodes', [ ]):
            if node_is_lbs( n ):
                yield n

def node_is_lbs_layer( node ):

    if not hasattr( node, 'node_tree' ):
        return False
    else:
        group_name = node.node_tree.name
        for sg in lbs_sub_groups:
            if sg in group_name:
                return True
        return False

def get_all_group_nodes( nt ):
        for n in nt.nodes:
            if hasattr( n, "node_tree" ):
                yield n
                for n in get_all_group_nodes( n.node_tree ):
                    yield n

def update_lbs_shader_transparency( ):
    
    for m in ( x for x in bpy.data.materials if x.get( "is_lbs_material" ) == True ):
        transparency = not m.blend_method == "OPAQUE"
        for n in ( x for x in m.node_tree.nodes if x.bl_idname == "LBSShaderNode" ):
            n.update_transparency( transparency )
        if m.blend_method == "BLEND" and not "lbs_first_time_blend" in m:
            m.show_transparent_back = False
            m.use_backface_culling = True
            m["lbs_first_time_blend"] = True

@persistent
def all_lb_nodes( *args ):

    bpy.app.driver_namespace["lbs_nodes"] = [
        '.Lightning Boy Shader', '.Solidify Outline', '*',
        '.Key Light*', '.Specular', '.Virtual Sun Light*', '.Virtual Point Light*', '.Virtual Spot Light*', '*',
        '.Color', '.Layer Adjustment', '.Global Color*', '*',
        '.Linear Gradient*', '.Spherical Gradient*', '.Local Gradient', '.Z Depth*', '*',
        '.2D Outline*', '.2D Rim Light*', '.2D Specular', '.Matcap', '*',
        '.Ambient Occlusion (Baked)', '.Ambient Occlusion (SS)', '*',
        '.Halftone Style', '.Hatch Style', '.Painterly Style', '.Anisotropic Style' ]

    detect_blend_mode_change( )

def detect_blend_mode_change( ):

    if bpy.app.driver_namespace.get( "lbs_msgbus_ready" ):
        return
    else:
        bpy.msgbus.subscribe_rna(
            key = ( bpy.types.Material, "blend_method" ),
            owner = object( ),
            notify = update_lbs_shader_transparency,
            args=(  )
            )
        bpy.app.driver_namespace["lbs_msgbus_ready"] = True

def update_node_tree_object( self, context ):
    obj = self.lbs_ref_object
    obj.use_fake_user = True
    for n in (x for x in self.nodes if "driven" in x.name ):
        if hasattr( self.animation_data, "drivers" ):
            for d in self.animation_data.drivers:
                if "driven_transforms" in d.data_path:
                    d.driver.variables[0].targets[0].id = self.lbs_ref_object
        if n.name == "driven_object":
            n.object = obj

def register_get_all_nodes( register ):

    if register:
        bpy.app.handlers.load_post.append( all_lb_nodes )
        all_lb_nodes( )
    else:
        bpy.app.handlers.load_post.remove( all_lb_nodes )

def register_node_tree_object( register ):

    if register:
        bpy.types.NodeTree.lbs_ref_object = PointerProperty( type = Object, update = update_node_tree_object )
    else:
        del bpy.types.NodeTree.lbs_ref_object