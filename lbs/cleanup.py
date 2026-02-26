import bpy
from bpy.types import PropertyGroup, NodeTree
from bpy.props import *
from . import utils

class CleanupElement( PropertyGroup ):
    node_tree : PointerProperty( type = NodeTree )

def get_clean_group_name( name ):
    
    groups = bpy.data.node_groups
    gnames = groups.keys( )
    if not name in gnames:
        print( f'Group "{name}" does not exist in Blend Data. This should not happen.')
        return ''
    short = name[:-4]
    if name[-4] == "." and name[-3:].isnumeric( ):
        if short in gnames:
            return short
        else:
            print( f'Group name "{name}" looks duplicate but "{short}" not found in Blend Data')
    return name

class CleanupEngine( PropertyGroup ):
    
    @property
    def scene( self ):
        return self.id_data
    
    remove_queue : CollectionProperty( type = CleanupElement )

    def flush_queue( self ):
        self.remove_queue.clear( )
    
    def add_to_queue( self, node_group ):
        gname = node_group.name
        if not gname in self.remove_queue.keys( ):
            e = self.remove_queue.add( )
            e.name = node_group.name
            e.node_tree = node_group
    
    def remove_groups_in_queue( self ):
        groups = bpy.data.node_groups
        for e in self.remove_queue:
            group = e.node_tree
            print( f'Removing node group "{group.name}"' )
            groups.remove( group )
        self.flush_queue( )

    def execute( self ):

        print( '-----------------------------------------')
        print( 'Starting Clean up!' )
        nodes = list( utils.get_all_lbs_nodes( ))
        for n in nodes:
            n.on_cleanup( self )

        self.remove_groups_in_queue( )
        print( 'Finished cleanup!' )

    def clean( self, node ):
        gname = node.node_tree.name
        new_name = get_clean_group_name( gname )
        if not gname == new_name:
            print( f'Duplicate found: "{gname}" --> "{new_name}"')
            return new_name
        else:
            return None

def register( register ):

    if register:
        bpy.types.Scene.lbs_cleanup = PointerProperty( type = CleanupEngine )
    else:
        del bpy.types.Scene.lbs_cleanup

def get_classes( ):
    yield CleanupElement
    yield CleanupEngine