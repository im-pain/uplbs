import bpy
from bpy.types import ShaderNodeCustomGroup
from bpy.props import *
from .node_utils import import_node_group, import_image, group_is_older_version
from mathutils import Color

class LBSNode( ShaderNodeCustomGroup ):

    @property
    def is_lbs_node( self ):
        return True

    def prop_update_initialize_group( self, context ):
        self.update_node_group( context )
    initialize_group : StringProperty( default = "none", update = prop_update_initialize_group )

    # SHOW ADVANCED PROP
    def prop_update_show_advanced( self, context ):
        self.update_advanced( context )
    show_advanced : BoolProperty( default = False, name = "advanced", update = prop_update_show_advanced )  

    # INHERITED METHODS

    def init( self, context ):
        self.set_color( )
        self.set_width( )
        self.toggle_close( True )
        self.on_init( context )

    def free(self):
        self.clear_node_tree( )

    def copy( self, node ):
        self.copy_node_tree( node )
    
    def draw_label( self ):
        name = f'{self.node_tree["lbs_original_name"]}'
        return name[1:]
    
    def draw_buttons( self, context, layout ):
        self.draw_general( context, layout )
        if self.show_advanced:
            self.draw_advanced( context, layout )
    
    def draw_general( self, context, layout ):
        pass

    def draw_advanced( self, context, layout ):
        pass

    # HELPER FUNCTIONS

    def on_init( self, context ):
        pass
    
    def set_color( self ):
        self.use_custom_color = True
        self.color = ( 0.08, 0.58, 0.7 )
    
    def set_width( self ):
        d = { 'LBSBaseNode' : 160, 'LBSShaderNode' : 200, 'LBSColorNode' : 160, 'LBSTextureNode' : 240 }
        self.width = d[ self.bl_idname ]

    def is_pinned_input( self, input ):
        return True

    def toggle_close( self, toggle ):
        for i in ( x for x in self.inputs if not self.is_pinned_input( x )):
            i.hide = toggle
        self.hide = toggle

    # FINAL
    def clear_node_tree( self ):
        bpy.data.node_groups.remove( self.node_tree )

    # FINAL
    def copy_node_tree( self, node ):
        self.node_tree = node.node_tree.copy( )
        self.node_tree.use_fake_user = True
        self.node_tree['lbs_protected'] = False
    
    def import_image( self, name ):
        return import_image( name )
    
    def update_node_group( self, context ):
        group_name = self.initialize_group
        groups = bpy.data.node_groups
        if group_name in groups.keys( ):
            group = groups[ group_name ]
            if group_is_older_version( group ):
                group.name += '_old'
        if not group_name in groups.keys( ):
            group = import_node_group( group_name )
        self.node_tree = group
        self.on_update_node_group( context )
        self.toggle_close( self.hide )
        self.update_advanced( context )
    
    def get_draw_nodes( self ):

        red = Color(( 1, 0, 0 ))
        nodes = self.node_tree.nodes
        all_frames = ( x for x in nodes if x.bl_idname == 'NodeFrame' and x.color == red )
        for frame in all_frames:
            for child in ( x for x in nodes if x.parent == frame ):
                yield child
    
    def draw_global_properties( self, layout ):

        draw_nodes = self.get_draw_nodes( )
        for node in draw_nodes:
            frame = node.parent
            prop_row = layout.row( align = True )
            labels = frame.name.split( )
            for i, label in enumerate( labels ):
                char = frame.label[ i ]
                prop_row.prop( node.inputs[ int( char )], 'default_value', text = label.replace( '_', ' ' ))
    
    def on_update_node_group( self, context ):
        pass
        
    def update_advanced( self, context ):
        pass
    
    def on_cleanup( self, cleanup ):
        print( f'Override in class "{self.bl_idname}"' )

class LBSInstancedNode( LBSNode ):

    # INSTANCE SUFFIX PROP
    def prop_update_instance_suffix( self, context ):
        self.update_instance( context )
    instance_suffix : StringProperty( default = "", update = prop_update_instance_suffix, name = "Instance Name" )

    def draw_instance_interface( self, layout ):
        inst_split = layout.split( factor = 0.2, align = True )
        inst_split.context_pointer_set( 'active_node', self )
        menu = inst_split.operator( 'wm.call_menu', text = '', icon = "DOWNARROW_HLT" )
        menu.name = 'NODE_MT_lbs_group_children'
        inst_split.prop( self, "instance_suffix", text = "" )
    
    def get_instance_node( self ):
        return self

    def update_instance( self, context ):

        print( 'updating suffix')
        groups = bpy.data.node_groups
        node = self.get_instance_node( )
        node_tree = node.node_tree
        old_name = node_tree.name
        suffix = "" if self.instance_suffix.isspace( ) else self.instance_suffix
        original_name = node_tree["lbs_original_name"]
        if suffix == "":
            new_name = original_name
        else:
            new_name = f'{original_name} ({suffix})'
        if not new_name in groups.keys( ):
            node.node_tree = node_tree.copy( )
            node.node_tree.name = new_name
            node.node_tree["lbs_protected"] = False
        else:
            node.node_tree = groups[new_name]
        
        old_tree = groups[ old_name ]
        if old_tree.users < 1 and old_tree["lbs_protected"] == False:
            groups.remove( old_tree )
    
    def draw_label( self ):
        appendix = f' ({self.instance_suffix})' if not self.instance_suffix == "" else ""
        name = f'{self.node_tree["lbs_original_name"]}{appendix}'
        return self.label if self.label else name[1:]

class LBSLayeredNode( LBSNode ):

    def prop_update_layers( self, context ):
        self.update_layers( context )
    layers : IntProperty( default = 1, min = 1, max = 20, update = prop_update_layers, name = "Layers" )

    def update_layers( self, context ):
        new = self.layers
        old = len([ x for x in self.inputs if self.is_layer_input( x )])
        diff = new - old
        self.layers_mem = self.layers
        if diff > 0:
            for i in range( diff ):
                self.add_layer( old )
                old += 1
        else:
            for i in range( abs( diff )):
                self.remove_layer( )

    def add_layer( self, layers ):
        print( 'define "add_layer" in subclass')
    
    def remove_layer( self ):
        print( 'define "remove_layer" in subclass')

    def is_layer_input( self, input ):
        return True
    
    def draw_layers_interface( self, layout ):
        layout.prop( self, 'layers', text = '' )