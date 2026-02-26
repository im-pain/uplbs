import bpy
from bpy.types import Operator
from bpy.props import *
from .utils import NODEGROUP_NAME

def is_node_context( context ):
    return (
        getattr( context.space_data, 'type', '' ) == 'NODE_EDITOR' and
        getattr( context.space_data, 'tree_type', '' ) == 'ShaderNodeTree' )

class AnimeStudioOp( Operator ):
    bl_options = {'UNDO'}

    @classmethod
    def poll( cls, context ):
        return is_node_context( context )

class ANIME_STUDIO_OT_setup_material( AnimeStudioOp ):
    bl_idname = "anime_studio.setup_material"
    bl_label = "Set up Anime Studio Material"
    bl_description = "Set up a material with QWN's Anime Super Studio shader"

    @classmethod
    def poll( cls, context ):
        if not super( ).poll( context ):
            return False
        obj = context.space_data.id_from
        return obj and hasattr( obj.data, "materials" )

    def execute( self, context ):
        obj = context.space_data.id_from
        if not context.space_data.id:
            mat = bpy.data.materials.new( "Anime Studio Material" )
            mat.use_nodes = True
            obj.data.materials.append( mat )
        else:
            mat = context.space_data.id

        for n in list( mat.node_tree.nodes ):
            mat.node_tree.nodes.remove( n )

        nt = mat.node_tree
        no = nt.nodes
        li = nt.links

        output = no.new( "ShaderNodeOutputMaterial" )
        output.name = "Output"
        output.location = ( 300, 0 )

        shader = no.new( "QWNAnimeSuperStudioNode" )
        shader.name = "Anime Super Studio Shader"
        shader.location = ( 0, 0 )

        li.new( shader.outputs[0], output.inputs[0] )

        return { "FINISHED" }

def get_classes( ):
    yield ANIME_STUDIO_OT_setup_material
