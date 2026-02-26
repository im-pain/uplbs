import bpy
from bpy.types import Image
from bpy.props import *
from .lbsnode import LBSNode

def get_texture_presets( self, context ):

    o_name = self.node_tree.get( "lbs_original_name" )
    presets = [ ]
    if o_name == ".Painterly Style":
        _type = "Painterly Style"
        items = ["1 Hard", "2 Rake", "3 Speckle", "4 Cloud"]      
    if o_name == ".Matcap":
        _type = "Matcap"
        items = ["1 Metallic"]
    if o_name == ".Ambient Occlusion (Baked)":
        _type = "AO Baked"
        items = [ ]
    if o_name == ".Halftone Style":
        _type = "Halftone Style"
        items = [ "1 Hard", "2 Soft" ]
    for i in items:
        i_name = f'{_type} {i}'
        presets.append(( i_name, i, f'Texture Item for {i}'))
    presets.append(( "custom", "Custom Texture", "Use a custom image texture"))
    return presets

#UPDATE FUNCTIONS

class LBSTextureNode( LBSNode ):

    bl_label = "LBS Texture Node"
    bl_idname = "LBSTextureNode"
    
    #PROPERTIES
    presets : EnumProperty( name = "Presets", items = get_texture_presets, default = 0, update = lambda s, c: s.update_presets( c ))
    texture : PointerProperty( type = Image, name = "Texture", update = lambda s,c: s.update_image( c ))
    
    def on_update_node_group( self, context ):
        self.copy_node_tree( self )
        self.presets = get_texture_presets( self, context )[0][0]

    def update_image( self, context ):
        nt = self.node_tree
        nodes = nt.nodes
        for n in (x for x in nodes if x.label == "tex" ):
            n.image = self.texture

    def update_presets( self, context ):
        preset = self.presets
        if not preset == "custom":
            if not preset in bpy.data.images:
                self.texture = self.import_image( preset )
            else: 
                self.texture = bpy.data.images[ self.presets ]
    
    def draw_general( self, context, layout ):
        
        if len ( get_texture_presets( self, context )) > 1:
            layout.prop( self, "presets" )
        if self.presets == "custom":
            layout.template_ID( self, "texture", new = "image.new", open = "image.open" )
    
    def is_pinned_input( self, input ):
        return input.name in ["Color", "Opacity", '└──', "Layer" ]
    
    def on_cleanup( self, cleanup ):
        pass

def get_classes( ):
    yield LBSTextureNode