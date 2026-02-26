import bpy
from .operators import NodeEditorOp, is_node_context, draw_operator as op
from .utils import get_all_lbs_nodes

class LBS_OT_update_node_colors( NodeEditorOp ):
    bl_idname = 'lbs.update_node_colors'
    bl_label = 'Update Node Colors'
    bl_description = 'Changes the color of all LBS nodes to a darker shade for better visibility in Blender 3.0'

    def execute( self, context ):
        nodes = get_all_lbs_nodes( )
        for n in nodes:
            n.set_color( )
        self.report( {'INFO'}, 'Updated colors of all LBS nodes.' )
        return{'FINISHED'}

class LBS_OT_update_outdated_nodes( NodeEditorOp ):
    bl_idname = 'lbs.update_outdated_nodes'
    bl_label = 'Update Outdated Nodes'
    bl_description = 'Updates the Lightning Boy Shader Node to reflect the changes in Version 2.1.2'

    def execute( self, context ):
        updates = set( )
        for nt in ( x for x in bpy.data.node_groups if x.name.startswith( '.Global Settings' ) and not 'hsv' in x.nodes.keys( )):
            updates.add( 'Updated Global settings to include exposed HSV parameters.' )
            curve = nt.nodes['curve']
            from_socket = curve.outputs[0]
            to_socket = from_socket.links[0].to_socket
            hsv = nt.nodes.new( 'ShaderNodeHueSaturation' )
            hsv.name = 'hsv'
            nt.links.new( from_socket, hsv.inputs[4] )
            nt.links.new( hsv.outputs[0], to_socket )
        
        for nt in ( x for x in bpy.data.node_groups if x.name.startswith( '.Global Settings' ) and not 'alpha_correct' in x.nodes.keys( )):
            updates.add( 'Updated Global settings to include a fix for a random color shift.' )
            
            n = nt.nodes.new( 'ShaderNodeMath' )
            n.name == 'alpha_correct'
            n.label = 'alpha_correct'
            n.location = ( 100, 0 )
            n.operation = 'ADD'
            n.inputs[ 0 ].default_value = 0.0
            n.inputs[ 1 ].default_value = 0.0

            rgb_socket = nt.nodes[ 'Shader to RGB' ].outputs[ 1 ]
            mix_socket = nt.nodes[ 'Mix Shader' ].inputs[ 0 ]
            nt.links.new( rgb_socket, n.inputs[ 0 ])
            nt.links.new( n.outputs[ 0 ], mix_socket )
        
        for nt in ( x for x in bpy.data.node_groups if x.name.startswith( '.Halftone Style' ) and not 'Rotation' in [ item.name for item in x.interface.items_tree if item.item_type == 'SOCKET' and item.in_out == 'INPUT' ]):
            updates.add( 'Updated Halftone Style nodes to include a "Rotation" input.' )
            new_inp = nt.interface.new_socket( name = 'Rotation', in_out = 'INPUT', socket_type = 'NodeSocketFloat' )
            nt.interface.move( new_inp, 3 )
            mapping = next( x for x in nt.nodes if x.bl_idname == 'ShaderNodeMapping' )
            rot_socket = mapping.inputs[2]
            combine = nt.nodes.new( 'ShaderNodeCombineXYZ' )
            combine.location = ( -1430, -1507 )
            add = nt.nodes.new( 'ShaderNodeMath' )
            add.location = (-1777, -1462 )
            add.operation = 'ADD'
            add.inputs[1].default_value = 4.0
            input_node = next( x for x in nt.nodes if x.bl_idname == 'NodeGroupInput' )
            nt.links.new( input_node.outputs[3], add.inputs[0])
            nt.links.new( add.outputs[0], combine.inputs[2])
            nt.links.new( combine.outputs[0], rot_socket )
        
        if not updates:
            self.report( {'INFO'}, 'All features up to date. No changes were made.' )
        else:
            print( '\n====================' )
            for u in updates:
                print( 'LBS Updater:', u )
            self.report( {'INFO'}, 'Outdated features updated. See console for details.' )
        
        return{'FINISHED'}

class LBS_PT_updater( bpy.types.Panel ):
    bl_idname = "LBS_PT_updater"
    bl_label = "LBS Updater"
    bl_space_type = "NODE_EDITOR"
    bl_region_type = "UI"
    bl_category = "LBS"
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll( cls, context ):
        if not is_node_context( context ):
            return False
        return context.space_data.tree_type == 'ShaderNodeTree'
    
    def draw( self, context ):
        layout = self.layout
        layout = layout.box( )
        op( layout, LBS_OT_update_node_colors )
        op( layout, LBS_OT_update_outdated_nodes )

def get_classes( ):
    yield LBS_OT_update_node_colors
    yield LBS_OT_update_outdated_nodes
    yield LBS_PT_updater