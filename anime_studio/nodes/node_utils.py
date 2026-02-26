import bpy
from .. utils import kk_lib

def group_is_older_version( group ):
    from .. import bl_info
    return tuple( group.get( 'kk_version', ( 0, 0, 0 ))) < bl_info['version']

def import_node_group( name ):
    with bpy.data.libraries.load( kk_lib, link = False ) as ( data_from, data_to ):
        data_to.node_groups.append( name )
    group = bpy.data.node_groups[ name ]
    adjust_node_group( group )
    return group

def adjust_node_group( group, protected_override = True ):
    from .. import bl_info
    group["kk_node"] = True
    group["kk_version"] = bl_info["version"]
    group["kk_protected"] = protected_override
    group["kk_original_name"] = group.name
    group.use_fake_user = True
    return group
