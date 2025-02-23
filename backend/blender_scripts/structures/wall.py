import bpy
import sys
import os
from mathutils import Vector
import random

def create_wall(location, size, name="Wall", add_trim=True):
    bpy.ops.mesh.primitive_cube_add(size=1, location=location)
    wall = bpy.context.object
    wall.name = name
    wall.scale = Vector(size)

    if add_trim:
        trim_thickness = 0.1
        trim_height = 0.2 

        bpy.ops.mesh.primitive_cube_add(size=1, location=(location[0], location[1], location[2] + size[2] / 2 + trim_height / 2))
        top_trim = bpy.context.object
        top_trim.name = name + "_Top_Trim"
        top_trim.scale = Vector((size[0], size[1], trim_height))

        bpy.ops.mesh.primitive_cube_add(size=1, location=(location[0], location[1], location[2] - size[2] / 2 - trim_height / 2))
        bottom_trim = bpy.context.object
        bottom_trim.name = name + "_Bottom_Trim"
        bottom_trim.scale = Vector((size[0], size[1], trim_height))

        trim_color = (0.3, 0.3, 0.3, 1)  
        top_trim.data.materials.append(get_material(trim_color, "Trim_Material"))
        bottom_trim.data.materials.append(get_material(trim_color, "Trim_Material"))

    return wall
