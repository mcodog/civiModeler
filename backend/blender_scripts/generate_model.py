import bpy
import sys
import os
from mathutils import Vector
import random

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')
script_dir = os.path.dirname(os.path.abspath(__file__))


def parse_arguments():
    args = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []

    width = float(args[0]) if len(args) > 0 else 10
    depth = float(args[1]) if len(args) > 1 else 8
    height = float(args[2]) if len(args) > 2 else 2.5
    budget = float(args[4]) if len(args) > 2 else 100
    output_path = args[5] if len(args) > 5 else os.path.join(os.getcwd(), "media", "models", "house_model.glb")

    return width, depth, height, budget, os.path.abspath(output_path)

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

def subtract_from_wall(location, size, rotation=(0, 0, 0)):
    bpy.ops.mesh.primitive_cube_add(size=1, location=location)
    cutter = bpy.context.object
    cutter.name = "Window_Cutter"
    cutter.scale = Vector(size)
    cutter.rotation_euler = rotation 

    for obj in bpy.data.objects:
        if "Wall" in obj.name and (
            abs(obj.location.x - location[0]) < size[0] and
            abs(obj.location.y - location[1]) < size[1] and
            abs(obj.location.z - location[2]) < size[2]
        ):
            boolean_modifier = obj.modifiers.new(name="Boolean_Cut", type='BOOLEAN')
            boolean_modifier.operation = 'DIFFERENCE'
            boolean_modifier.object = cutter
            bpy.context.view_layer.objects.active = obj
            bpy.ops.object.modifier_apply(modifier=boolean_modifier.name)

    bpy.data.objects.remove(cutter, do_unlink=True)

def create_door(location, size=(1, 0.1, 2), name="Door"):
    bpy.ops.mesh.primitive_cube_add(size=1, location=location)
    door = bpy.context.object
    door.name = name
    door.scale = Vector(size)
    door.data.materials.append(get_material((0.4, 0.2, 0.1, 1), "Wood_Material"))  

    frame_thickness = 0.1  
    frame_height = size[2] + 0.2  
    frame_width = size[0] + 0.2  
    
    frame_positions = [
        (location[0] - frame_width/2 + frame_thickness/2, location[1], location[2]), 
        (location[0] + frame_width/2 - frame_thickness/2, location[1], location[2]),  
        (location[0], location[1], location[2] + frame_height/2 - frame_thickness/2), 
    ]
    
    frame_parts = []
    for i, pos in enumerate(frame_positions):
        bpy.ops.mesh.primitive_cube_add(size=1, location=pos)
        frame_part = bpy.context.object
        frame_part.name = name + f"_Frame_{i+1}"
        frame_part.scale = Vector((frame_thickness, size[1] + 0.05, frame_height if i < 2 else frame_thickness))
        frame_part.data.materials.append(get_material((0.3, 0.15, 0.08, 1), "Frame_Material")) 
        frame_parts.append(frame_part)

    handle_location = (location[0] + size[0] / 2 - 0.05, location[1] + size[1] / 2 + 0.01, location[2] - size[2] / 3)
    bpy.ops.mesh.primitive_cylinder_add(radius=0.05, depth=0.2, location=handle_location)
    handle = bpy.context.object
    handle.name = name + "_Handle"
    handle.rotation_euler = (1.57, 0, 0)
    handle.data.materials.append(get_material((0.8, 0.8, 0.1, 1), "Handle_Material"))

    return door, frame_parts, handle

def create_window(location, size=(1.5, 0.1, 1.5), name="Window", rotation=(0, 0, 0)):
    if location[1] > 0: 
        rotation = (0, 0, 0) 
        subtract_location = (location[0], location[1] - size[1], location[2])
    elif location[1] < 0: 
        rotation = (0, 0, 0)  
        subtract_location = (location[0], location[1] + size[1], location[2])
    elif location[0] > 0: 
        rotation = (0, 1.5708, 0)  
        subtract_location = (location[0] - size[1], location[1], location[2])
    elif location[0] < 0: 
        rotation = (0, 1.5708, 0)  
        subtract_location = (location[0] + size[1], location[1], location[2])
    subtract_from_wall(subtract_location, size, rotation)

    bpy.ops.mesh.primitive_cube_add(size=1, location=location)
    glass = bpy.context.object
    glass.name = name + "_Glass"
    glass.scale = Vector(size)
    glass.rotation_euler = rotation  
    glass.data.materials.append(get_material((0.5, 0.7, 1, 0.1), "Glass_Material", transparency=True))  

    frame_thickness = 0.1 
    frame_size = (size[0] + frame_thickness, size[1] + 0.05, size[2] + frame_thickness)

    frame_positions = [
        (location[0] - frame_size[0] / 2 + frame_thickness / 2, location[1], location[2]), 
        (location[0] + frame_size[0] / 2 - frame_thickness / 2, location[1], location[2]), 
        (location[0], location[1], location[2] + frame_size[2] / 2 - frame_thickness / 2),  
        (location[0], location[1], location[2] - frame_size[2] / 2 + frame_thickness / 2),  
    ]

    frames = []
    for i, pos in enumerate(frame_positions):
        bpy.ops.mesh.primitive_cube_add(size=1, location=pos)
        frame = bpy.context.object
        frame.name = name + f"_Frame_{i+1}"
        frame.scale = Vector((frame_thickness, size[1] + 0.05, frame_size[2] if i < 2 else frame_thickness))
        frame.rotation_euler = rotation 
        frame.data.materials.append(get_material((0.2, 0.2, 0.2, 1), "Frame_Material")) 
        frames.append(frame)

    return glass, frames

def create_floor(location, size, name="Floor", use_texture=False, texture_path=""):
    bpy.ops.mesh.primitive_plane_add(size=1, location=location)
    floor = bpy.context.object
    floor.name = name
    floor.scale = Vector((size[0], size[1], 1)) 
    
    floor.data.materials.append(get_material((0.8, 0.8, 0.8, 1), "Floor_Material", use_texture, texture_path))
    mat = get_material((0.8, 0.8, 0.8, 1), "Floor_Material", use_texture, texture_path)
    floor.data.materials.clear() 
    floor.data.materials.append(mat) 

    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.subdivide(number_cuts=2)
    bpy.ops.object.mode_set(mode='OBJECT')

    return floor

def create_furniture():
    create_bed((-3, 3, 0.3), "Bed 1")  
    create_bed((3, 3, 0.3), "Bed 2")   
    # create_table((-3, 2, 0.3), "Nightstand 1")
    # create_table((3, 2, 0.3), "Nightstand 2")

    create_sofa((0, 1, 0.3), "Sofa")
    create_table((0, -0.5, 0.3), "Coffee Table")

    create_toilet((2, -3, 0.3), "Toilet")
    create_sink((3, -3, 0.3), "Sink")

    create_table((0, -3, 0.3), "Dining Table")
    create_chair((-1, -3, 0.3), "Chair 1")
    create_chair((1, -3, 0.3), "Chair 2")

def create_bed(location, name="Bed"):
    bpy.ops.mesh.primitive_cube_add(size=1, location=location)
    bed_base = bpy.context.object
    bed_base.name = name
    bed_base.scale = Vector((1.6, 2, 0.3))
    bed_base.data.materials.append(get_material((0.6, 0.4, 0.3, 1), "Wood_Material")) 

    bpy.ops.mesh.primitive_cube_add(size=1, location=(location[0], location[1], location[2] + 0.35))
    mattress = bpy.context.object
    mattress.name = name + "_Mattress"
    mattress.scale = Vector((1.5, 1.9, 0.2))
    mattress.data.materials.append(get_material((0.9, 0.9, 0.9, 1), "Fabric_Material"))

    bpy.ops.mesh.primitive_cube_add(size=1, location=(location[0], location[1] - 0.95, location[2] + 0.7))
    headboard = bpy.context.object
    headboard.name = name + "_Headboard"
    headboard.scale = Vector((1.6, 0.7, 0.1))  
    headboard.rotation_euler.x = 1.5708 
    headboard.data.materials.append(get_material((0.5, 0.3, 0.2, 1), "Wood_Material")) 

    leg_positions = [
        (location[0] - 0.75, location[1] - 0.95, location[2] - 0.3),
        (location[0] + 0.75, location[1] - 0.95, location[2] - 0.3),
        (location[0] - 0.75, location[1] + 0.95, location[2] - 0.3),
        (location[0] + 0.75, location[1] + 0.95, location[2] - 0.3),
    ]
    
    legs = []
    for i, pos in enumerate(leg_positions):
        bpy.ops.mesh.primitive_cylinder_add(radius=0.08, depth=0.4, location=pos)
        leg = bpy.context.object
        leg.name = name + f"_Leg_{i+1}"
        leg.rotation_euler.x = 1.5708  
        leg.data.materials.append(get_material((0.3, 0.2, 0.1, 1), "Metal_Material")) 
        legs.append(leg)

    pillow_positions = [
        (location[0] - 0.4, location[1] - 0.8, location[2] + 0.5),
        (location[0] + 0.4, location[1] - 0.8, location[2] + 0.5),
    ]
    
    pillows = []
    for i, pos in enumerate(pillow_positions):
        bpy.ops.mesh.primitive_cube_add(size=1, location=pos)
        pillow = bpy.context.object
        pillow.name = name + f"_Pillow_{i+1}"
        pillow.scale = Vector((0.5, 0.2, 0.15)) 
        pillow.data.materials.append(get_material((0.95, 0.95, 0.95, 1), "Pillow_Material")) 
        pillows.append(pillow)

    return bed_base, mattress, headboard, legs, pillows

def create_sofa(location, name="Sofa"):
    bpy.ops.mesh.primitive_cube_add(size=1, location=(location[0], location[1], location[2] + 0.3))
    seat = bpy.context.object
    seat.name = name + "_Seat"
    seat.scale = Vector((2, 1, 0.2)) 
    seat.data.materials.append(get_material((0.3, 0.3, 0.3, 1), "Fabric_Material")) 

    bpy.ops.mesh.primitive_cube_add(size=1, location=(location[0], location[1] - 0.45, location[2] + 0.75))
    backrest = bpy.context.object
    backrest.name = name + "_Backrest"
    backrest.scale = Vector((2, 0.2, 0.6)) 
    backrest.data.materials.append(get_material((0.3, 0.3, 0.3, 1), "Fabric_Material"))

    armrest_positions = [
        (location[0] - 0.9, location[1], location[2] + 0.5),
        (location[0] + 0.9, location[1], location[2] + 0.5), 
    ]
    
    armrests = []
    for i, pos in enumerate(armrest_positions):
        bpy.ops.mesh.primitive_cube_add(size=1, location=pos)
        armrest = bpy.context.object
        armrest.name = name + f"_Armrest_{i+1}"
        armrest.scale = Vector((0.2, 1, 0.5))  
        armrest.data.materials.append(get_material((0.3, 0.3, 0.3, 1), "Fabric_Material"))
        armrests.append(armrest)

    cushion_positions = [
        (location[0] - 0.6, location[1] - 0.35, location[2] + 0.6),
        (location[0], location[1] - 0.35, location[2] + 0.6),
        (location[0] + 0.6, location[1] - 0.35, location[2] + 0.6),
    ]
    
    cushions = []
    for i, pos in enumerate(cushion_positions):
        bpy.ops.mesh.primitive_cube_add(size=1, location=pos)
        cushion = bpy.context.object
        cushion.name = name + f"_Cushion_{i+1}"
        cushion.scale = Vector((0.6, 0.2, 0.3))
        cushion.data.materials.append(get_material((0.35, 0.35, 0.35, 1), "Cushion_Material")) 
        cushions.append(cushion)

    return seat, backrest, armrests, cushions

def create_table(location, name="Table"):
    bpy.ops.mesh.primitive_cube_add(size=1, location=(location[0], location[1], location[2] + 0.75))
    tabletop = bpy.context.object
    tabletop.name = name + "_Top"
    tabletop.scale = Vector((1.2, 0.8, 0.1)) 
    tabletop.data.materials.append(get_material((0.7, 0.5, 0.3, 1), "Wood_Material")) 

    leg_positions = [
        (location[0] - 0.5, location[1] - 0.3, location[2] + 0.35),
        (location[0] + 0.5, location[1] - 0.3, location[2] + 0.35),
        (location[0] - 0.5, location[1] + 0.3, location[2] + 0.35),
        (location[0] + 0.5, location[1] + 0.3, location[2] + 0.35),
    ]
    
    legs = []
    for i, pos in enumerate(leg_positions):
        bpy.ops.mesh.primitive_cylinder_add(radius=0.05, depth=0.7, location=pos)
        leg = bpy.context.object
        leg.name = name + f"_Leg_{i+1}"
        leg.rotation_euler.x = 1.5708  
        leg.data.materials.append(get_material((0.5, 0.3, 0.2, 1), "Leg_Material"))  
        legs.append(leg)

    return tabletop, legs

def create_chair(location, name="Chair"):
    bpy.ops.mesh.primitive_cube_add(size=1, location=(location[0], location[1], location[2] + 0.4))
    seat = bpy.context.object
    seat.name = name + "_Seat"
    seat.scale = Vector((0.5, 0.5, 0.1))  
    seat.data.materials.append(get_material((0.7, 0.5, 0.3, 1), "Wood_Material")) 

    bpy.ops.mesh.primitive_cube_add(size=1, location=(location[0], location[1] - 0.22, location[2] + 0.8))
    backrest = bpy.context.object
    backrest.name = name + "_Backrest"
    backrest.scale = Vector((0.5, 0.1, 0.4)) 
    backrest.data.materials.append(get_material((0.7, 0.5, 0.3, 1), "Wood_Material"))

    leg_positions = [
        (location[0] - 0.2, location[1] - 0.2, location[2] + 0.2),
        (location[0] + 0.2, location[1] - 0.2, location[2] + 0.2),
        (location[0] - 0.2, location[1] + 0.2, location[2] + 0.2),
        (location[0] + 0.2, location[1] + 0.2, location[2] + 0.2),
    ]
    
    legs = []
    for i, pos in enumerate(leg_positions):
        bpy.ops.mesh.primitive_cylinder_add(radius=0.05, depth=0.4, location=pos)
        leg = bpy.context.object
        leg.name = name + f"_Leg_{i+1}"
        leg.rotation_euler.x = 1.5708 
        leg.data.materials.append(get_material((0.5, 0.3, 0.2, 1), "Leg_Material"))
        legs.append(leg)

    return seat, backrest, legs

def create_toilet(location, name="Toilet"):
    bpy.ops.mesh.primitive_cylinder_add(radius=0.3, depth=0.5, location=location)
    bowl = bpy.context.object
    bowl.name = name + "_Bowl"
    bowl.data.materials.append(get_material((1, 1, 1, 1), "Ceramic_Material"))

    bpy.ops.mesh.primitive_torus_add(align='WORLD', location=(location[0], location[1], location[2] + 0.2))
    seat = bpy.context.object
    seat.name = name + "_Seat"
    seat.scale = Vector((0.4, 0.4, 0.05)) 
    seat.data.materials.append(get_material((0.9, 0.9, 0.9, 1), "Seat_Material"))

    bpy.ops.mesh.primitive_cube_add(size=1, location=(location[0], location[1] - 0.2, location[2] + 0.5))
    tank = bpy.context.object
    tank.name = name + "_Tank"
    tank.scale = Vector((0.4, 0.2, 0.4)) 
    tank.data.materials.append(get_material((1, 1, 1, 1), "Ceramic_Material"))

    return bowl, seat, tank

def create_sink(location, name="Sink"):
    bpy.ops.mesh.primitive_cube_add(size=1, location=(location[0], location[1], location[2] - 0.1))
    countertop = bpy.context.object
    countertop.name = name + "_Countertop"
    countertop.scale = Vector((1, 0.5, 0.1))  
    countertop.data.materials.append(get_material((0.6, 0.6, 0.6, 1), "Countertop_Material")) 

    bpy.ops.mesh.primitive_cylinder_add(radius=0.3, depth=0.15, location=(location[0], location[1], location[2] + 0.05))
    sink_bowl = bpy.context.object
    sink_bowl.name = name + "_Bowl"
    sink_bowl.scale.z = 0.8  
    sink_bowl.data.materials.append(get_material((1, 1, 1, 1), "Ceramic_Material"))  

    bpy.ops.mesh.primitive_cylinder_add(radius=0.05, depth=0.2, location=(location[0] + 0.3, location[1] - 0.15, location[2] + 0.2))
    faucet_base = bpy.context.object
    faucet_base.name = name + "_Faucet_Base"
    faucet_base.rotation_euler.x = 1.5708  
    faucet_base.data.materials.append(get_material((0.8, 0.8, 0.8, 1), "Metal_Material")) 

    bpy.ops.mesh.primitive_cylinder_add(radius=0.04, depth=0.3, location=(location[0] + 0.3, location[1] - 0.15, location[2] + 0.4))
    faucet_spout = bpy.context.object
    faucet_spout.name = name + "_Faucet_Spout"
    faucet_spout.rotation_euler.y = 1.5708 
    faucet_spout.data.materials.append(get_material((0.8, 0.8, 0.8, 1), "Metal_Material"))

    bpy.ops.mesh.primitive_cylinder_add(radius=0.05, depth=0.02, location=(location[0], location[1], location[2] - 0.05))
    drain = bpy.context.object
    drain.name = name + "_Drain"
    drain.data.materials.append(get_material((0.2, 0.2, 0.2, 1), "Drain_Material"))

    return countertop, sink_bowl, faucet_base, faucet_spout, drain

def subtract_area(x, y, width, depth, height):
    bpy.ops.mesh.primitive_cube_add(size=1, location=(x, y, height / 2))
    cutter = bpy.context.object
    cutter.name = "Cutter_Temp"
    cutter.scale = (width, depth, height) 

    objects_to_modify = [
        obj for obj in bpy.data.objects
        if (
            obj.type == 'MESH' and obj.name != "Cutter_Temp" and 
            x - width / 2 <= obj.location.x <= x + width / 2 and
            y - depth / 2 <= obj.location.y <= y + depth / 2
        )
    ]

    for obj in objects_to_modify:
        bpy.context.view_layer.objects.active = obj
        boolean_modifier = obj.modifiers.new(name="Boolean_Cut", type='BOOLEAN')
        boolean_modifier.operation = 'DIFFERENCE'
        boolean_modifier.object = cutter
        bpy.ops.object.modifier_apply(modifier=boolean_modifier.name)

    bpy.data.objects.remove(cutter, do_unlink=True)

import random

def generate_house(width, depth, height, output_path, budget):
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()

    wall_thickness = 0.2
    create_floor((0, 0, -0.05), (width, depth, 0.1), "Floor")

    walls = {
        "Front Wall": create_wall((0, depth / 2, height / 2), (width, wall_thickness, height), "Front Wall"),
        "Back Wall": create_wall((0, -depth / 2, height / 2), (width, wall_thickness, height), "Back Wall"),
        "Right Wall": create_wall((width / 2, 0, height / 2), (wall_thickness, depth, height), "Right Wall"),
        "Left Wall": create_wall((-width / 2, 0, height / 2), (wall_thickness, depth, height), "Left Wall"),
    }

    create_door((0, depth / 2 + 0.05, 1), (0.9, wall_thickness, 2), "Front Door")

    for wall_name, wall_obj in walls.items():
        num_windows = random.randint(0, 2)
        used_positions = []  

        for _ in range(num_windows):
            win_size = (1.5, 0.5, 1.5) 
            min_gap = 2.0  

            max_attempts = 10  
            for attempt in range(max_attempts):
                if "Front Wall" in wall_name or "Back Wall" in wall_name:
                    win_x = random.uniform(-width / 3, width / 3) 
                    win_y = random.uniform(1, height - 1) 
                    win_pos = (win_x, depth / 2 if "Front" in wall_name else -depth / 2, win_y)
                    win_rotation = (0, 0, 0)  
                else:  
                    win_x = width / 2 if "Right" in wall_name else -width / 2
                    win_y = random.uniform(1, height - 1) 
                    win_z = random.uniform(-depth / 3, depth / 3) 
                    win_pos = (win_x, win_z, win_y)
                    win_rotation = (0, 1.5708, 0)  

                if all(abs(win_pos[0] - pos[0]) >= min_gap and abs(win_pos[2] - pos[2]) >= min_gap for pos in used_positions):
                    used_positions.append(win_pos)
                    break  

            # create_window(win_pos, size=win_size, rotation=win_rotation)

    if budget <= 500:
        num_rooms = 2 
        room_types = ["Bedroom", "Bathroom"]
    elif budget <= 1000:
        num_rooms = 3
        room_types = ["Bedroom", "Bathroom", "Kitchen"]
    elif budget <= 3000:
        num_rooms = 4
        room_types = ["Bedroom", "Bathroom", "Kitchen", "Living Room"]
    elif budget <= 8000:
        num_rooms = 5
        room_types = ["Master Bedroom", "Guest Bedroom", "Bathroom", "Kitchen", "Living Room"]
    else:
        num_rooms = 6 
        room_types = ["Master Bedroom", "Guest Bedroom", "Bathroom", "Kitchen", "Living Room", "Office"]

    room_sizes = {
        "Bathroom": (width / 3, depth / 3),  
        "Bedroom": (width / 2, depth / 2),
        "Living Room": (width / 1.5, depth / 1), 
        "Kitchen": (width / 2, depth / 2),
        "Office": (width / 2, depth / 2),
        "Guest Bedroom": (width / 2, depth / 2),
        "Master Bedroom": (width / 2, depth / 2)
    }

    possible_positions = [
        (-width / 2 + 2, depth / 2 - 2),  
        (width / 2 - 2, depth / 2 - 2),    
        (-width / 2 + 2, -depth / 2 + 2),  
        (width / 2 - 2, -depth / 2 + 2),  
        (-width / 2 + 2, 0), 
        (width / 2 - 2, 0), 
        (0, -depth / 2 + 2), 
        (0, depth / 2 - 2)  
    ]
    random.shuffle(possible_positions)

    room_positions = {}
    for i in range(num_rooms):
        room_name = room_types[i]
        room_positions[room_name] = possible_positions[i]

    for room, (x, y) in room_positions.items():
        room_width, room_depth = room_sizes.get(room, (width / 4, depth / 4)) 

        subtract_area(x, y, room_width, room_depth, height)

        texture_filename = "vinyl.jpg" 
        texture_path = os.path.join(script_dir, texture_filename).encode("utf-8").decode("utf-8")

        if os.path.exists(texture_path):
            print(f"Texture found at: {texture_path}")
        else:
            print(f"Error: Texture file not found at {texture_path}")

        create_floor((x, y, -0.05), (room_width, room_depth, 0.1), f"{room} Floor", use_texture=True, texture_path=texture_path)

        create_wall((x, y + room_depth / 2, height / 2), (room_width, wall_thickness, height), f"{room} Top Wall")
        create_wall((x, y - room_depth / 2, height / 2), (room_width, wall_thickness, height), f"{room} Bottom Wall")
        create_wall((x - room_width / 2, y, height / 2), (wall_thickness, room_depth, height), f"{room} Left Wall")
        create_wall((x + room_width / 2, y, height / 2), (wall_thickness, room_depth, height), f"{room} Right Wall")

        create_door((x, y + room_depth / 2, 1), (0.9, wall_thickness, 2), f"{room} Door")

    for room, (x, y) in room_positions.items():
        if "Bedroom" in room:
            create_bed((x, y, 0.3), f"{room} Bed")
        elif room == "Living Room":
            create_sofa((x, y, 0.3), "Sofa")
        elif room == "Kitchen":
            create_table((x, y, 0.3), "Dining Table")
            create_chair((x - 1, y, 0.3), "Dining Chair 1")
            create_chair((x + 1, y, 0.3), "Dining Chair 2")
        elif room == "Bathroom":
            create_sink((x, y, 0.3), "Bathroom Sink")
            create_toilet((x, y - 1, 0.3), "Bathroom Toilet")
        elif room == "Dining Room":
            create_table((x, y, 0.3), "Dining Table")
            create_chair((x - 1, y, 0.3), "Dining Chair 1")
            create_chair((x + 1, y, 0.3), "Dining Chair 2")
        elif room == "Office":
            create_table((x, y, 0.3), "Office Desk")
            create_chair((x, y - 0.5, 0.3), "Office Chair")

    bpy.ops.file.make_paths_absolute()
    bpy.ops.file.pack_all()

    bpy.ops.export_scene.gltf(
        filepath=output_path,
        export_format='GLB',
        export_apply=True,
        use_selection=False,  
        export_image_format='AUTO'  
    )

    print(f"Generated a Closed Concept Layout with {num_rooms} rooms based on budget and randomized windows.")
    return output_path

if __name__ == "__main__":
    width, depth, height, budget, output_path = parse_arguments()
    print(budget)
    generate_house(width, depth, height, output_path, budget)
