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
        input = no["input"]
        add = no["add"]
        connect_socket = add.inputs[1].links[0].from_socket

        new_color = nt.interface.new_socket( name = f'Color {layers + 1}', in_out = 'INPUT', socket_type = 'NodeSocketColor' )
        mask_inp = nt.interface.new_socket( name = '└──', in_out = 'INPUT', socket_type = 'NodeSocketFloat' )
        mask_inp.hide_value = True
        nt.interface.move( mask_inp, 0 )
        nt.interface.move( new_color, 0 )
        new_mix = no.new( "ShaderNodeMix" )
        new_mix.data_type = 'RGBA'
        li.new( input.outputs[0], new_mix.inputs[7])
        li.new( input.outputs[1], new_mix.inputs[0])
        li.new( connect_socket, new_mix.inputs[6])
        li.new( new_mix.outputs[2], add.inputs[1])
    
    def remove_layer( self ):

        nt = self.node_tree
        no = nt.nodes
        li = nt.links
        add = no["add"]
        old_mix = add.inputs[1].links[0].from_node
        connect_socket = old_mix.inputs[1].links[0].from_socket
        input_items = [ item for item in nt.interface.items_tree if item.item_type == 'SOCKET' and item.in_out == 'INPUT' ]
        nt.interface.remove( input_items[1] )
        nt.interface.remove( input_items[0] )
        no.remove( old_mix )
        li.new( connect_socket, add.inputs[ 1 ])
        
def get_classes( ):
    yield LBSColorNode