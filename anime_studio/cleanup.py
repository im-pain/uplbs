import bpy
from bpy.types import PropertyGroup
from bpy.props import *
from .utils import get_all_anime_studio_nodes

def get_clean_group_name( name ):
    groups = bpy.data.node_groups
    gnames = groups.keys( )
    if name not in gnames:
        print( f'Group "{name}" does not exist in Blend Data.' )
        return ''
    if len( name ) > 4 and name[-4] == "." and name[-3:].isnumeric( ):
        short = name[:-4]
        if short in gnames:
            return short
        else:
            print( f'Group name "{name}" looks duplicate but "{short}" not found in Blend Data' )
    return name

class AnimeStudioCleanupEngine( PropertyGroup ):

    @property
    def scene( self ):
        return self.id_data

    def execute( self ):
        print( '-----------------------------------------' )
        print( 'Starting Anime Studio Clean up!' )
        nodes = list( get_all_anime_studio_nodes( ) )
        for n in nodes:
            self._clean_node( n )
        print( 'Finished cleanup!' )

    def _clean_node( self, node ):
        if not hasattr( node, 'node_tree' ) or not node.node_tree:
            return
        gname = node.node_tree.name
        new_name = get_clean_group_name( gname )
        if new_name and new_name != gname:
            groups = bpy.data.node_groups
            if new_name in groups:
                print( f'Duplicate found: "{gname}" --> "{new_name}"' )
                node.node_tree = groups[ new_name ]

def register( register ):
    if register:
        bpy.types.Scene.anime_studio_cleanup = PointerProperty( type = AnimeStudioCleanupEngine )
    else:
        del bpy.types.Scene.anime_studio_cleanup

def get_classes( ):
    yield AnimeStudioCleanupEngine
