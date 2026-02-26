import bpy, platform
import urllib.parse
from bpy.props import *
from bpy.types import Panel
from . import bl_info
from .operators import *
from .operators import draw_operator as op, is_node_context

class LBS_PT_shader_settings( Panel ):
    bl_idname = "LBS_PT_options"
    bl_label = "LBS"
    bl_space_type = "NODE_EDITOR"
    bl_region_type = "UI"
    bl_category = "LBS"

    @classmethod
    def poll( cls, context ):
        if not is_node_context( context ):
            return False
        return context.space_data.tree_type == 'ShaderNodeTree'
    
    def draw( self, context ):
        layout = self.layout
        obj = context.object
        #scene settings
        layout.label( text = "Scene:" )
        scene_box = layout.box( )
        op( scene_box, LBS_OT_setup_base_scene )
        mat_row = scene_box.row( align = True )
        op( mat_row, LBS_OT_setup_base_material, text = 'Base Material' ).is_ground = False
        op( mat_row, LBS_OT_setup_base_material, text = 'Ground Material' ).is_ground = True
        op( scene_box, LBS_OT_cleanup_duplicates )
        #shader settings
        layout.label( text = "Shader:" )
        shader_box = layout.box( )

        op( shader_box, LBS_OT_match_global_settings )

        #outline_settings
        obj = context.object
        if obj:
            draw_outline_settings( layout, obj )
        layout.separator( factor = 2 )
        draw_user_guide_button( layout )
        draw_feedback_button( layout )

from .utils import doc_url
def draw_user_guide_button( layout ):
    layout.operator( "wm.url_open", text = "Weblink to User Guide", icon = "HELP" ).url = doc_url

def draw_feedback_button( layout ):

    name = bl_info["name"]
    version = bl_info["version"]
    version_compact = f'{version[0]}.{version[1]}.{version[2]}'
    bl_version = bpy.app.version_string
    system_info = platform.platform( )
    info = f'Version: ({version_compact}), Blender: ({bl_version}), System: ({system_info})'
    body = f'{urllib.parse.quote( info )}%0A%0ABug%20Report%20Checklist%20%28Check%20the%20System%20Console%20for%20errors%29%3A%0A-%20What%20happened%3A%0A%0A-%20What%20I%20expected%3A%0A%0A-%20How%20to%20reproduce%20this%20error%3A%0A%0A'
    subject = urllib.parse.quote( f'{name} Addon Feedback ({version_compact})' )
    url = f"mailto:team@lightningboystudio.com?subject={subject}&body={body}"
    layout.operator( "wm.url_open", text = "Feedback / Report Issue", icon = "URL" ).url = url

def draw_outline_settings( layout, obj ):

    layout.label( text = f'Outline Settings ({obj.name}):')
    outline_box = layout.box( )
    valid_mods = [ x for x in obj.modifiers if "outline" in x.name.lower( ) and x.type == "SOLIDIFY" ]
    if len( valid_mods ):
        solidify = valid_mods[ 0 ]
        outline_box.prop( solidify, "thickness" )
        outline_box.prop( solidify, "offset" )
        outline_box.prop( solidify, "thickness_clamp" )

        #outline material
        act_mat = obj.active_material
        if act_mat:
            target_index = max( 0, obj.active_material_index + solidify.material_offset )
            outline_mat = obj.material_slots[ target_index ].material
            if not outline_mat == None and not outline_mat.node_tree == None:
                try:
                    output = [ x for x in outline_mat.node_tree.nodes if x.bl_idname == "ShaderNodeOutputMaterial" and x.is_active_output == True ][0]
                    outline_box.prop( output.inputs[0].links[0].from_node.inputs["Color"], "default_value", text = f'{outline_mat.name} Color' )
                except:
                    outline_box.label( text = "--No Color Input found--", icon = "ERROR" )
            else:
                outline_box.label( text = "--No Node Tree available--", icon = "ERROR" )
    else:
        op( outline_box, LBS_OT_solidify_add, overrides = {'object' : obj })

def get_classes( ):
    yield LBS_PT_shader_settings