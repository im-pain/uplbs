import bpy
from bpy.props import *
from .lbsnode import LBSInstancedNode

class LBSStandardNode( LBSInstancedNode ):

    bl_label = "LBS Base Node"
    bl_idname = "LBSBaseNode"

    #PROPERTIES
    active_channel : EnumProperty( 
        items = [
            ( "0", "Character", "Character Lighting" ),
            ( "1", "Background", "Background Lighting" ),
            ( "2", "Extra", "Extra Lighting" )
        ],
        name = "Color Channel",
        default = 0,
        update = lambda s, c: s.update_color_channel( c )
        )
    
    @property
    def instance_tree( self ):
        if self.node_tree["lbs_has_global_settings"] == 1:
            return self.node_tree
        else:
            return None

    def update_color_channel( self, context ):
        self.inputs[".channel"].default_value = int( self.active_channel )
        self.update( )

    def draw_general( self, context, layout ):
        if ".channel" in self.inputs.keys( ):
            layout.prop( self, "active_channel", text = "" )
    
    def draw_advanced( self, context, layout ):
        
        if self.instance_tree:
            box = layout.box( )
            self.draw_instance_interface( box )
            self.draw_global_properties( box )
            nodes = self.node_tree.nodes
            if "driven_object" in nodes.keys( ) or "driven_transforms" in nodes.keys( ):
                box.prop( self.node_tree, "lbs_ref_object", text = "" )

    def copy( self, node ):
        pass

    def free( self ):
        if( not self.node_tree.get("lbs_protected") and self.node_tree.users <= 1 ): 
            self.clear_node_tree( )

    def is_pinned_input( self, input ):
        return input.name in ["Color", "Opacity", '└──', "Layer" ]
    
    def on_update_node_group( self, context ):

        if not self.node_tree["lbs_has_global_settings"] in [ 0, 1 ]:
            self.copy_node_tree( self )
        if ".channel" in self.node_tree.inputs.keys( ):
            self.inputs[".channel"].enabled = False
    
    def on_cleanup(self, cleanup ):
        new_name = cleanup.clean( self )
        if new_name:
            if self.instance_tree:
                self.instance_suffix = self.instance_suffix
            else:
                cleanup.add_to_queue( self.node_tree )
                self.initialize_group = new_name

class LBSBaseNode( LBSStandardNode ):
    bl_idname = 'LBSBaseNode'

# THIS IS A LEFACY CLASS FOR BASE NODES MADE IN VERSION (2.1.0).
class LBSLegacyNode( LBSStandardNode ):
    bl_idname = 'LBSNode'

def get_classes( ):
    yield LBSBaseNode
    yield LBSLegacyNode