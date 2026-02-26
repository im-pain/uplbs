import bpy
from .node_utils import get_material_from_node
from .lbsnode import LBSInstancedNode, LBSLayeredNode
from ..utils import node_is_lbs_layer

class LBSShaderNode( LBSInstancedNode, LBSLayeredNode ):

    bl_idname = "LBSShaderNode"
    bl_label = "Lightning Boy Shader"

    def global_settings_node( self ):
        return self.node_tree.nodes['global_settings']

    def layer_nodes( self ):
        for n in self.node_tree.nodes:
            if node_is_lbs_layer( n ):
                yield n

    def on_update_node_group( self, context ):

        self.copy_node_tree( self )
        material = get_material_from_node( self )
        self.update_transparency( not material.blend_method == "OPAQUE" )

    def is_layer_input(self, input):
        return input.bl_idname == 'NodeSocketShader'
    
    def update_transparency( self, transparency ):
        trans = self.inputs[".transparency"]
        trans.enabled = False
        trans.default_value = transparency
        mask = self.inputs["Alpha Mask"]
        opacity = self.inputs["Shader Opacity"]
        if transparency == 0:
            for i in (mask, opacity):
                if len( i.links ):
                    self.id_data.links.remove( i.links[0] )
        mask.enabled = opacity.enabled = bool( transparency )
        self.update( )

    def on_init( self, context ):

        mat = get_material_from_node( self )
        mat["is_lbs_material"] = True
        self.toggle_close( False )

    def draw_general( self, context, layout ):
        
        row = layout.row( align = True )
        row.context_pointer_set( 'active_node', self )
        self.draw_layers_interface( row )
        row.operator( "node.lbs_shader_rearrange", text = "", icon = "COLLAPSEMENU" )
    
    def draw_advanced(self, context, layout):
        layout = layout.box( )
        self.draw_instance_interface( layout )
        gs_node = self.global_settings_node( )
        layout.template_curve_mapping( gs_node.node_tree.nodes["curve"], "mapping", type = "COLOR" )
        c = layout.column( align = True )
        hsv = gs_node.node_tree.nodes['hsv']
        for input in ( hsv.inputs[x] for x in range( 3 )):
            c.prop( input, 'default_value', text = input.name )

    def get_instance_node( self ):
        return self.global_settings_node( )
    
    def copy( self, node ):
        self.copy_node_tree( node )
        mat = get_material_from_node( self )
        if not mat:
            print( 'LBS: Material not found')
        else:
            mat[ "is_lbs_material" ] = True
    
    def free( self ):
        
        gs = self.global_settings_node( )
        if gs.node_tree.users < 2 and gs.node_tree["lbs_protected"] == False:
            bpy.data.node_groups.remove( gs.node_tree )
        self.clear_node_tree( )

    def update_advanced( self, context ):
        self.inputs["Opacity"].enabled = self.show_advanced
    
    def on_cleanup( self, cleanup ):
        for n in list( self.layer_nodes( )) + [self.global_settings_node( )]:
            new_name = cleanup.clean( n )
            if new_name:
                cleanup.add_to_queue( n.node_tree )
                n.node_tree = bpy.data.node_groups[ new_name ]
    
    def add_layer( self, layers ):

        nt = self.node_tree
        no = nt.nodes
        li = nt.links
        inputs = nt.inputs
        input = no["input"]
        mix = no["global_settings"]
        connect_socket = mix.inputs[0].links[0].from_socket

        spaces = " " if layers + 1 >= 10 else "  "
        new_inp = inputs.new( "NodeSocketShader", f'――――――{spaces}{layers + 1}' )
        inputs.move( len( inputs ) -1, 1 )
        new_layer = no.new( "ShaderNodeGroup" )
        new_layer.node_tree = bpy.data.node_groups[".LBS Layer"]
        li.new( input.outputs[1], new_layer.inputs[0])  
        li.new( connect_socket, new_layer.inputs[1])
        li.new( new_layer.outputs[0], mix.inputs[0])
    
    def remove_layer( self ):

        nt = self.node_tree
        no = nt.nodes
        li = nt.links
        inputs = nt.inputs  
        mix = no["global_settings"]
        old_layer = mix.inputs[0].links[0].from_node
        connect_socket = old_layer.inputs[1].links[0].from_socket
        inputs.remove( inputs[1] )
        no.remove( old_layer )
        li.new( connect_socket, mix.inputs[0])

def get_classes( ):
    yield LBSShaderNode