import bpy
from bpy.types import Operator
from bpy.props import *
from mathutils import Color

from .utils import lbs_sub_groups, lbs_lib, get_all_group_nodes, node_is_lbs, get_lbs_world, import_lbs_collection

temp_layers = [ ]

def draw_operator( layout, cls, text = None, icon = 'NONE', icon_value = 0, overrides = {}):

    row = layout.row( align = True )
    for i in list( overrides ):
        row.context_pointer_set( i, overrides[ i ])
    op = row.operator( cls.bl_idname, text = text if not text == None else cls.bl_label, icon = icon, icon_value = icon_value )
    return op

def is_node_context( context ):
    return ( 
        getattr( context.space_data, 'type', '') == 'NODE_EDITOR' and 
        getattr( context.space_data, 'tree_type', '' ) == 'ShaderNodeTree' )

class NodeEditorOp( Operator ):
    bl_options = {'UNDO'}

    @classmethod
    def poll( cls, context ):
        return is_node_context( context )

class LBSSelectedOp( Operator ):
    bl_options = {'UNDO'}

    @classmethod
    def poll( cls, context ):
        return ( is_node_context (context ) and
                len([ x for x in context.selected_nodes if node_is_lbs( x )]))
    
    def selected_lbs_nodes( self, context ):
        return ( x for x in context.selected_nodes if node_is_lbs( x ))

    def first_lbs_node( self, context ):

        node = context.active_node
        if node_is_lbs( node ):
            return node
        elif len( list( self.selected_lbs_nodes( context ))):
            lbs_nodes = list( self.selected_lbs_nodes( context ))
            return lbs_nodes[0]
        else: return None

class LBSActiveOp( Operator ):

    bl_options = {'UNDO'}
    lbs_filter = {'ALL'}

    @classmethod
    def poll( cls, context ):
        if not is_node_context( context ):
            return False
        node = getattr( context, 'active_node', None )
        if not node:
            return False
        if 'ALL' in cls.lbs_filter:
            return node
        elif node.bl_idname in cls.lbs_filter:
            return node
        else:
            return False

class NODE_OT_lbs_toggle_advanced( LBSSelectedOp ):
    bl_idname = "node.lbs_toggle_advanced"
    bl_label = "Toggle Advanced"

    def execute( self, context ):

        toggle = not self.first_lbs_node( context ).show_advanced
        nodes = self.selected_lbs_nodes( context )
        for n in nodes:
            n.show_advanced = toggle
        context.area.tag_redraw( )
        return{ "FINISHED" }

class NODE_OT_lbs_toggle_closed( LBSSelectedOp ):
    bl_idname = "node.lbs_toggle_closed"
    bl_label = "Toggle Closed"

    def execute( self, context ):

        toggle = not self.first_lbs_node( context ).hide
        for n in context.selected_nodes:
            if node_is_lbs( n ):
                n.toggle_close( toggle )
            n.hide = toggle
        return{ "FINISHED" }

class NODE_OT_lbs_layer_rearrange( LBSActiveOp ):
    bl_idname = "node.lbs_shader_rearrange"
    bl_label = "Sort Layers"
    bl_description = "Dort layers of current Shader Node"

    _node = None

    def draw( self, context ):
        
        layout = self.layout
        layout.separator( )
        global temp_layers
        for e in temp_layers:
            row = layout.row( align = True )
            if len( e.links ) < 1:
                no_buttons = True
                text = "(Empty Layer)"
            else:
                no_buttons = False
                connect_node = e.links[0].from_node
                if connect_node.bl_idname == "LBSColorNode":
                    text = connect_node.label if connect_node.label else "Color"
                else:
                    text = connect_node.label if connect_node.label else connect_node.node_tree.name[1:]

            row.label( text = text + "."*100 )
            if not no_buttons:
                for dir in [ "UP", "DOWN" ]:
                    op = row.operator( "node.lbs_shader_layer_move", text = "", icon = f'TRIA_{dir}' )
                    op.dir = dir
                    op.index = temp_layers.index( e )
        
    def execute( self, context ):
        
        global temp_layers
        node = self._node
        if temp_layers == node.inputs[1:len( temp_layers) + 1]:
            self.report( {"WARNING"}, "No change to layers made!" )
            return{"FINISHED"}
        input_sockets = [ ]
        nt = context.space_data.edit_tree
        for i in temp_layers:
            if len( i.links ) > 0:
                input_sockets.append( i.links[0].from_socket )
                nt.links.remove( i.links[0])
            else:
                input_sockets.append( None )
        for e in range( len( temp_layers )):
            if not input_sockets[e] == None:
                nt.links.new( input_sockets[e], node.inputs[e + 1] )

        return{"FINISHED"}

    def invoke( self, context, event ):
        global temp_layers
        self._node = context.active_node
        temp_layers = [ ]
        node = context.active_node
        for i in ( x for x in node.inputs if x.bl_idname == "NodeSocketShader" ):
            temp_layers.append( i )
        return context.window_manager.invoke_props_dialog( self )

class NODE_OT_lbs_new_group_child( NodeEditorOp ):
    bl_idname = "node.lbs_new_group_child"
    bl_label = "New Group Child"

    suffix : StringProperty( default = "001" )

    def draw(self, context ):

        layout = self.layout
        layout.prop( self, "suffix" )

    def execute( self, context ):

        node = context.active_node
        node.instance_suffix = self.suffix
        return{"FINISHED"}

class NODE_OT_lbs_layer_move( NodeEditorOp ):
    bl_idname = "node.lbs_shader_layer_move"
    bl_label = "Move"

    dir : StringProperty( default = "UP" )
    index : IntProperty( )

    def execute( self, context ):
        global temp_layers
        try:
            element = temp_layers[ self.index ]
            if self.dir == "DOWN":
                if self.index > len( temp_layers ) - 1:
                    return{"FINISHED"}
                temp_layers.remove( element )
                temp_layers.insert( self.index + 1, element )
            elif self.index > 0:
                temp_layers.remove( element )
                temp_layers.insert( self.index - 1, element )
        except:
            pass
        return{"FINISHED"}

class LBS_OT_setup_base_scene( NodeEditorOp ):
    bl_idname = "lbs.setup_base_scene"
    bl_label = "Set up Base Scene"
    bl_description = 'This Button will change your world material, Color Management settings to "Standard" and turn off SSR as well as all incompatible lights'

    def execute( self, context ):
        
        scene = context.scene
        try:
            scene.view_settings.view_transform = "Standard"
        except:
            self.report( {'WARNING'}, '"Standard" view transform setting not found. Could not set up scene properly.' )
        scene.eevee.use_ssr = False
        context.space_data.insert_offset_direction = "LEFT"

        scene.world = get_lbs_world( )
    
        coll_name = "Lightning Boy Shader"
        if not coll_name in bpy.data.collections.keys( ):
            import_lbs_collection( coll_name )
        else:
            self.report( {"INFO"}, "Lightning Boy Shader collection already appended." )
        try:
            scene.collection.children.link( bpy.data.collections[ "Lightning Boy Shader" ])
        except:
            print( 'Could not link LBS Collection to scene. Might already be linked.' )
        
        for o in bpy.data.collections[ coll_name ].all_objects:
            o.use_fake_user = True

        self.manage_lights( context )

        return{"FINISHED"}

    def manage_lights( self, context ):

        red = Color((1,0,0))
        green = Color((0,1,0))
        blue = Color((0,0,1))
        log = []
        for o in context.view_layer.objects:
            if o.type == "LIGHT" and not o.data.color in [ red, green, blue ]:
                log.append( o.name )
                o.hide_render = True
                o.hide_viewport = True
        if len( log ):
            self.report( {"WARNING"}, "Light objects have been disabled. Check system console for details.")
            print( "Some light objects have been disabled from the viewport and render:" )
            for l in log:
                print( l )

class LBS_OT_match_global_settings( NodeEditorOp ):
    bl_idname = "lbs.match_global_settings"
    bl_label = "Match Global Settings"
    bl_description = "Select Objects to match global settings of active LBS Shader Node"
    
    def execute( self, context ):
        bpy.app.driver_namespace["lbs_temp_nodes"] = []
        temp_nodes = bpy.app.driver_namespace["lbs_temp_nodes"]
        objects = [x for x in context.scene.objects if x.select_get( ) == True ]
        an = context.active_node
        for o in objects:
            for m in o.data.materials:
                for lbs_node in ( x for x in m.node_tree.nodes if x.bl_idname == "LBSShaderNode" ):
                    temp_nodes.append( lbs_node )
        bpy.ops.wm.call_menu( name = "NODE_MT_lbs_group_children" )
        return {"FINISHED"}

class LBS_OT_setup_base_material( NodeEditorOp ):
    bl_idname = "lbs.setup_base_material"
    bl_label = "Set up Base Material"
    bl_description = "This action will override the active material"

    is_ground : BoolProperty( default = False )

    @classmethod
    def poll( cls, context ):
        if not super( ).poll( context ):
            return False
        obj = context.space_data.id_from
        return obj and hasattr( obj.data, "materials" )
    
    def base_material( self, mat ):
        
        nt = mat.node_tree
        no = nt.nodes
        li = nt.links

        #new nodes
        output = no.new( "ShaderNodeOutputMaterial" )
        output.name = "Output"
        output.location = ( 0, 0 )
        shader = no.new( "LBSShaderNode" )
        shader.initialize_group = ".Lightning Boy Shader"
        shader.name = "Base Shader"
        shader.location = ( -240, 0 )
        shader.layers = 3
        color = no.new( "LBSColorNode" )
        color.initialize_group = ".Color"
        color.name = "Color"
        color.location = ( -420, -160 )
        color.toggle_close( True )
        light = no.new( "LBSBaseNode" )
        light.initialize_group = ".Key Light*"
        light.name = "Key Light"
        light.location = ( -420, -120 )
        spec = no.new( "LBSBaseNode" )
        spec.initialize_group = ".Specular"
        spec.name = "Specular"
        spec.location = ( -420, -80 )
        #make links
        li.new( shader.outputs[0], output.inputs[0] )
        li.new( color.outputs[0], shader.inputs["――――――  1"] )
        li.new( light.outputs[0], shader.inputs["――――――  2"] )
        li.new( spec.outputs[0], shader.inputs["――――――  3"] )

    def ground_material( self, mat ):

        nt = mat.node_tree
        no = nt.nodes
        li = nt.links

        #new nodes
        output = no.new( "ShaderNodeOutputMaterial" )
        output.name = "Output"
        output.location = ( 0, 0 )
        shader = no.new( "LBSShaderNode" )
        shader.initialize_group = ".Lightning Boy Shader"
        shader.name = "Base Shader"
        shader.location = ( -240, 0 )
        shader.layers = 2
        color = no.new( "LBSColorNode" )
        color.initialize_group = ".Color"
        color.name = "Color"
        color.location = ( -420, -140 )
        color.inputs["Color 1"].default_value = ( 0.041613, 0.324302, 0.771987, 1.0 )
        color.toggle_close( True )
        light = no.new( "LBSBaseNode" )
        light.initialize_group = ".Key Light*"
        light.name = "Key Light"
        light.location = ( -420, -80 )
        light.active_channel = "1"
        light.inputs["Color"].default_value = ( 0.262251, 0.630757, 0.879623, 1.0 )
        #make links
        li.new( shader.outputs[0], output.inputs[0] )
        li.new( color.outputs[0], shader.inputs["――――――  1"] )
        li.new( light.outputs[0], shader.inputs["――――――  2"] )

    def execute( self, context ):

        obj = context.space_data.id_from
        if not context.space_data.id:
            mat = bpy.data.materials.new( "Material" )
            mat.use_nodes = True
            obj.data.materials.append( mat )
        else:
            mat = context.space_data.id
        #clear all nodes
        for n in mat.node_tree.nodes:
            mat.node_tree.nodes.remove( n )
        
        if not self.is_ground:
            self.base_material( mat )
        else:
            self.ground_material( mat )
        

        return {"FINISHED"}

class LBS_OT_solidify_add( NodeEditorOp ):

    bl_idname = "lbs.solidify_add"
    bl_label = "Add Solidify Outline"
    bl_description = "Hold Shift for individual outlines per Material"

    ev = [ ]

    @classmethod
    def poll( cls, context ):
        if not super( ).poll( context ):
            return False
        return hasattr( context.object.data, "materials" ) and len( context.object.data.materials ) > 0

    def invoke(self, context, event ):

        ev = [ ]
        if event.shift:
            ev.append( "SHIFT" )
        
        self.ev = ev
        return self.execute( context )

    def execute( self, context ):
        obj = context.object
        if None in ( x.material for x in obj.material_slots ):
            self.report( {'ERROR'}, 'Empty material slot found. Could not add outlines to active object')
            return{'CANCELLED'}
        init_mat = obj.active_material
        print( init_mat.name )
        ev = self.ev
        vg_name = "LBS Solidify Outline"
        mat_name = "LBS Outline Material"
        mod = new_solidify( obj, vg_name )
        mats = obj.data.materials
        
        if "SHIFT" in ev:

            mod.material_offset = -1
            for mat in ( x for x in mats if not "lbs_outline_mat" in x ):
                mat_index = mats.find( mat.name )
                outline_mat_name = f'{mat.name} (LBS Outline)'
                if not outline_mat_name in bpy.data.materials.keys( ):
                    outline_mat = new_outline_mat( outline_mat_name )
                else:
                    outline_mat = bpy.data.materials[ outline_mat_name ]
                mats.append( outline_mat )
                obj.active_material_index = len( mats ) -1
                for i in range( len(mats) - mat_index - 1 ):
                    bpy.ops.object.material_slot_move( direction = "UP" )
        else:
            if not obj.material_slots[-1].material.name == mat_name:
                if not mat_name in bpy.data.materials:
                    mat = new_outline_mat( mat_name )
                else:
                    mat = bpy.data.materials[mat_name]
                obj.data.materials.append( mat )
            obj.active_material_index = len( mats ) -1
            for i in range( len( mats ) -1 ):
                bpy.ops.object.material_slot_move( direction = "UP" )
        obj.active_material_index = obj.material_slots.find( init_mat.name )
                
        return{"FINISHED"}

def new_solidify( obj, vg_name ):

    if not vg_name in obj.vertex_groups.keys( ):
        vg = obj.vertex_groups.new( name = vg_name)
    else: 
        vg = obj.vertex_groups[vg_name]
    mod = obj.modifiers.new( "LBS Geometry Outline", "SOLIDIFY" )
    mod.offset = 1
    mod.thickness = 0.1
    mod.use_flip_normals = True
    mod.vertex_group = vg.name
    mod.invert_vertex_group = True
    mod.material_offset = -100
    mod.use_rim = False
    return mod

def new_outline_mat( mat_name ):
    mat = bpy.data.materials.new( mat_name )
    mat["lbs_outline_mat"] = True
    mat.use_nodes = True
    mat.use_backface_culling = True
    mat.shadow_method = "NONE"
    nt = mat.node_tree
    nodes = nt.nodes
    for n in nodes:
        nodes.remove( n )
    output = nodes.new( "ShaderNodeOutputMaterial" )
    rgb = nodes.new( "LBSBaseNode" )
    rgb.name = "solidify_shader"
    rgb.initialize_group = ".Solidify Outline"
    rgb.location = ( -160.0, 0.0 )
    rgb.inputs[0].default_value = (0,0,0,1)
    rgb.toggle_close( False )
    nt.links.new( rgb.outputs[0], output.inputs[0])
    return mat

class LBS_OT_cleanup_duplicates( NodeEditorOp ):
    bl_idname = 'lbs.cleanup_duplicates'
    bl_label = 'Clean up Duplicates'
    bl_description = 'Resolve duplicate node group issues when appending materials from other files'

    def execute( self, context ):
        cleanup = context.scene.lbs_cleanup
        cleanup.execute( )
        self.report( {'INFO'}, 'Clean up complete. Check console for details.' )
        return{'FINISHED'}

def get_classes( ):
    yield NODE_OT_lbs_toggle_advanced
    yield NODE_OT_lbs_toggle_closed
    yield NODE_OT_lbs_layer_rearrange
    yield NODE_OT_lbs_new_group_child
    yield NODE_OT_lbs_layer_move
    yield LBS_OT_setup_base_scene
    yield LBS_OT_match_global_settings
    yield LBS_OT_setup_base_material
    yield LBS_OT_solidify_add
    yield LBS_OT_cleanup_duplicates