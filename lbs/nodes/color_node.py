import bpy
from .lbsnode import LBSLayeredNode

class LBSColorNode( LBSLayeredNode ):

    bl_idname = "LBSColorNode"
    bl_label = "Color"

    def on_update_node_group( self, context ):
        self.copy_node_tree( self )

    def draw_general( self, context, layout ):
        self.draw_layers_interface( layout )
    
    def is_layer_input(self, input):
        return input.bl_idname == 'NodeSocketColor'
    
    def is_pinned_input( self, input ):
        return input.name in [ '└──', 'Alpha Mask' ] or input.name.startswith( "Color" )
    
    def on_cleanup( self, cleanup ):
        pass

    def add_layer( self, layers ):

        nt = self.node_tree
        no = nt.nodes
        li = nt.links
        inputs = nt.inputs
        input = no["input"]
        add = no["add"]
        connect_socket = add.inputs[1].links[0].from_socket

        inputs.new( "NodeSocketColor", f'Color {layers + 1}' )
        mask_inp = inputs.new( "NodeSocketFloat", "└──" )
        mask_inp.hide_value = True
        inputs.move( len( inputs ) -1, 0 )
        inputs.move( len( inputs ) -1, 0 )
        new_mix = no.new( "ShaderNodeMixRGB" )
        li.new( input.outputs[0], new_mix.inputs[2])
        li.new( input.outputs[1], new_mix.inputs[0])
        li.new( connect_socket, new_mix.inputs[1])
        li.new( new_mix.outputs[0], add.inputs[1])
    
    def remove_layer( self ):

        nt = self.node_tree
        no = nt.nodes
        li = nt.links
        inputs = nt.inputs  
        add = no["add"]
        old_mix = add.inputs[1].links[0].from_node
        connect_socket = old_mix.inputs[1].links[0].from_socket
        inputs.remove( inputs[0] )
        inputs.remove( inputs[0] )
        no.remove( old_mix )
        li.new( connect_socket, add.inputs[ 1 ])
        
def get_classes( ):
    yield LBSColorNode