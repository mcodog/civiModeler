import bpy
import sys
import os
from mathutils import Vector
import random

def get_material(color, name="Material", use_texture=False, texture_path=""):
    
    mat = bpy.data.materials.get(name) or bpy.data.materials.new(name=name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    bsdf = nodes.get("Principled BSDF")

    if use_texture and texture_path and os.path.exists(texture_path):
        try:
            tex_image = nodes.new(type="ShaderNodeTexImage")
            tex_image.image = bpy.data.images.load(texture_path)

            tex_coord = nodes.new("ShaderNodeTexCoord")
            mapping = nodes.new("ShaderNodeMapping")
            mat.node_tree.links.new(tex_coord.outputs["UV"], mapping.inputs["Vector"])
            mat.node_tree.links.new(mapping.outputs["Vector"], tex_image.inputs["Vector"])
            mat.node_tree.links.new(tex_image.outputs["Color"], bsdf.inputs["Base Color"])

            print(f"Texture applied: {texture_path}")
        except Exception as e:
            print(f"Failed to load texture: {texture_path} - {e}")
    
    else:
        bsdf.inputs["Base Color"].default_value = color
        print(f"⚠️ Using solid color instead of texture: {color}")

    return mat