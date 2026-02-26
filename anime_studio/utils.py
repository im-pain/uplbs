import bpy, os
from bpy.app.handlers import persistent

NODEGROUP_NAME = "QWN's Anime Super Studio"

python_path = os.path.dirname( os.path.realpath( __file__ ))
kk_lib = os.path.join( python_path, "lib", "KK_Template_Shader.blend" )

def node_is_anime_studio( node ):
    return getattr( node, 'is_anime_studio_node', False )

def get_all_anime_studio_nodes( ):
    data = bpy.data
    for nt in [ x.node_tree for x in data.materials if x.node_tree ] + list( data.node_groups ):
        for n in getattr( nt, 'nodes', [] ):
            if node_is_anime_studio( n ):
                yield n

@persistent
def all_anime_nodes( *args ):
    bpy.app.driver_namespace["anime_studio_nodes"] = [ NODEGROUP_NAME ]

def register_get_all_nodes( register ):
    if register:
        bpy.app.handlers.load_post.append( all_anime_nodes )
        all_anime_nodes( )
    else:
        bpy.app.handlers.load_post.remove( all_anime_nodes )
