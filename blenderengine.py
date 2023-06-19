# %%
# pylint: disable=E1101
import math
import os

import bpy
import cv2
import numpy as np
from PIL import Image


# function that creates a new material from the textures
def create_material(
    name, diffuse_map, metalness_map, roughness_map, normal_map, displacement_map
):
    """
    ------------------------------------------------
    A function that creates a new blender material from textures.

    Args:
    ------------------------------------------------
    name: A string representing the name of the material.
    diffuse_map: A PIL image representing the diffuse map.
    metalness_map: A PIL image representing the metalness map.
    roughness_map: A PIL image representing the roughness map.
    normal_map: A PIL image representing the normal map.
    displacement_map: A PIL image representing the displacement map.

    Returns:
    ------------------------------------------------
    A blender material.
    """

    # create a new material and set it to use nodes
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links

    # create the image nodes for the textures
    diffuse_node = nodes.new(type="ShaderNodeTexImage")
    metalness_node = nodes.new(type="ShaderNodeTexImage")
    roughness_node = nodes.new(type="ShaderNodeTexImage")
    normal_node = nodes.new(type="ShaderNodeTexImage")
    displacement_node = nodes.new(type="ShaderNodeTexImage")

    # set the interpolation of the image nodes to closest to prevent blurring
    diffuse_node.interpolation = "Closest"
    metalness_node.interpolation = "Closest"
    roughness_node.interpolation = "Closest"
    normal_node.interpolation = "Closest"
    displacement_node.interpolation = "Closest"

    # get resolution of the textures
    size = diffuse_map.size[0]

    # create empty images for the textures according to the resolution
    diffuse_texture = bpy.data.images.new(
        name="diffuse", width=size, height=size, alpha=False, float_buffer=True
    )
    metalness_texture = bpy.data.images.new(
        name="metalness", width=size, height=size, alpha=False, float_buffer=True
    )
    roughness_texture = bpy.data.images.new(
        name="roughness", width=size, height=size, alpha=False, float_buffer=True
    )
    normal_texture = bpy.data.images.new(
        name="normal", width=size, height=size, alpha=False, float_buffer=True
    )
    displacement_texture = bpy.data.images.new(
        name="displacement", width=size, height=size, alpha=False, float_buffer=True
    )

    # converting PIL images to numpy arrays and then to RGBA range 0-1
    diffuse_map = cv2.cvtColor(np.asarray(diffuse_map), cv2.COLOR_RGB2RGBA) / 255
    metalness_map = cv2.cvtColor(np.asarray(metalness_map), cv2.COLOR_RGB2RGBA) / 255
    roughness_map = cv2.cvtColor(np.asarray(roughness_map), cv2.COLOR_RGB2RGBA) / 255
    normal_map = cv2.cvtColor(np.asarray(normal_map), cv2.COLOR_RGB2RGBA) / 255
    displacement_map = (
        cv2.cvtColor(np.asarray(displacement_map), cv2.COLOR_RGB2RGBA) / 255
    )

    # injecting the numpy arrays into the blender images
    diffuse_texture.pixels[:] = (np.asarray(diffuse_map)).ravel()
    metalness_texture.pixels[:] = (np.asarray(metalness_map)).ravel()
    roughness_texture.pixels[:] = (np.asarray(roughness_map)).ravel()
    normal_texture.pixels[:] = (np.asarray(normal_map)).ravel()
    displacement_texture.pixels[:] = (np.asarray(displacement_map)).ravel()

    # packing the images into the blender file
    diffuse_texture.pack()
    metalness_texture.pack()
    roughness_texture.pack()
    normal_texture.pack()
    displacement_texture.pack()

    # setting the color space of the images to sRGB
    diffuse_texture.colorspace_settings.name = "sRGB"
    metalness_texture.colorspace_settings.name = "sRGB"
    roughness_texture.colorspace_settings.name = "sRGB"
    normal_texture.colorspace_settings.name = "sRGB"
    displacement_texture.colorspace_settings.name = "sRGB"

    # setting the image nodes to use the images
    diffuse_node.image = diffuse_texture
    metalness_node.image = metalness_texture
    roughness_node.image = roughness_texture
    normal_node.image = normal_texture
    displacement_node.image = displacement_texture

    # creating the principled shader node
    principled = nodes.get("Principled BSDF")
    output = nodes.get("Material Output")

    # creating the normal map and displacement map nodes
    normalmap = nodes.new(type="ShaderNodeNormalMap")
    dispmap = nodes.new(type="ShaderNodeDisplacement")

    # set node locations
    diffuse_node.location = (-1200, 0)
    metalness_node.location = (-1200, -200)
    roughness_node.location = (-1200, -400)
    normal_node.location = (-1200, -600)
    displacement_node.location = (-1200, -800)
    principled.location = (-300, 0)
    normalmap.location = (-600, 0)
    dispmap.location = (-900, 0)
    output.location = (300, 0)

    # set principled shader inputs
    principled.inputs["Base Color"].default_value = (1.0, 1.0, 1.0, 1.0)
    principled.inputs["Metallic"].default_value = 1.0
    principled.inputs["Roughness"].default_value = 1.0
    principled.inputs["Specular"].default_value = 0.0
    principled.inputs["Sheen Tint"].default_value = 0.0
    principled.inputs["Clearcoat"].default_value = 0.0
    principled.inputs["Clearcoat Roughness"].default_value = 0.0
    principled.inputs["IOR"].default_value = 1.45
    principled.inputs["Transmission"].default_value = 0.0
    principled.inputs["Transmission Roughness"].default_value = 0.0
    principled.inputs["Emission"].default_value = (0.0, 0.0, 0.0, 1.0)
    principled.inputs["Alpha"].default_value = 1.0

    # link textures
    links.new(diffuse_node.outputs["Color"], principled.inputs["Base Color"])
    links.new(metalness_node.outputs["Color"], principled.inputs["Metallic"])
    links.new(roughness_node.outputs["Color"], principled.inputs["Roughness"])
    links.new(normal_node.outputs["Color"], normalmap.inputs["Color"])
    links.new(displacement_node.outputs["Color"], dispmap.inputs["Height"])

    # link nodes
    links.new(principled.outputs["BSDF"], output.inputs["Surface"])
    links.new(normalmap.outputs["Normal"], principled.inputs["Normal"])
    links.new(dispmap.outputs["Displacement"], output.inputs["Displacement"])

    # mark the material as a render asset to keep it in the file and accessible as a asset
    mat.asset_mark()

    return mat


# render the material
def render_material(
    light_rotation,
    material_name,
    diffuse_map,
    metalness_map,
    roughness_map,
    normal_map,
    displacement_map,
):
    """
    ------------------------------------------------
    Render a material with the given texture maps and light rotation

    Args:
    ------------------------------------------------
    light_rotation: rotation of the light
    material_name: name of the material
    diffuse_map: A PIL image representing the diffuse map.
    metalness_map: A PIL image representing the metalness map.
    roughness_map: A PIL image representing the roughness map.
    normal_map: A PIL image representing the normal map.
    displacement_map: A PIL image representing the displacement map.

    Returns:
    ------------------------------------------------
    A PIL image representing the rendered material preview.
    """

    # clear the scene
    bpy.ops.wm.read_factory_settings(use_empty=True)

    # create an HDRI environment
    bpy.context.scene.world = bpy.data.worlds.new("New World")
    world = bpy.context.scene.world
    world.use_nodes = True
    world_node_tree = world.node_tree
    env_node = world_node_tree.nodes.new("ShaderNodeTexEnvironment")
    env_node.image = bpy.data.images.load(r"E:\_prototypes\ai2mat\assets\hdri.hdr")

    # create a mapping node and link it to the environment node to rotate the environment
    mapping_node = world_node_tree.nodes.new("ShaderNodeMapping")
    mapping_node.inputs[2].default_value = [0, 0, 0]
    world_node_tree.links.new(mapping_node.outputs[0], env_node.inputs[0])
    # link a texture coordinate node to the mapping node
    tex_coord_node = world_node_tree.nodes.new("ShaderNodeTexCoord")
    world_node_tree.links.new(tex_coord_node.outputs[0], mapping_node.inputs[0])

    # link the environment node to the world output node
    output_node = world_node_tree.nodes["World Output"]
    world_node_tree.links.new(env_node.outputs["Color"], output_node.inputs["Surface"])

    # create a new camera and position it
    # convert rotation 360 degrees to radians
    bpy.ops.object.camera_add(location=(0, -3.75, 0), rotation=(1.57, 0, 0))
    bpy.context.scene.camera = bpy.context.object

    # create a directional light and position it
    bpy.ops.object.light_add(type="SUN", location=(0, 0, 0), rotation=(0, 0, 0))
    bpy.context.object.data.energy = 10

    # rotate the light around the z axis from -90 to 90 degrees
    light_rotation = ((light_rotation * 1.8) - 90) * (math.pi / 180)
    bpy.context.object.rotation_euler[2] = light_rotation
    # angle the light at 60 degrees
    bpy.context.object.rotation_euler[0] = 60 * (math.pi / 180)

    # create a new cube at the origin and assign the material
    bpy.ops.mesh.primitive_cube_add(location=(0, 0, 0))
    # uv unwrap the cube with cube projection and apply the material
    bpy.ops.object.editmode_toggle()
    bpy.ops.uv.cube_project(cube_size=1)
    bpy.ops.object.editmode_toggle()
    mat = create_material(
        material_name,
        diffuse_map,
        metalness_map,
        roughness_map,
        normal_map,
        displacement_map,
    )
    bpy.context.object.data.materials.append(mat)

    # set the render settings
    bpy.context.scene.render.resolution_x = 600
    bpy.context.scene.render.resolution_y = 600
    bpy.context.scene.render.engine = "CYCLES"
    bpy.context.scene.cycles.use_denoising = False
    bpy.context.scene.cycles.samples = 16
    bpy.context.scene.render.image_settings.file_format = "PNG"
    image_path = os.path.join(os.path.dirname(__file__), "temp.png")
    # render the image
    bpy.context.scene.render.filepath = image_path
    bpy.ops.render.render(write_still=True)

    # really dirty way to read the rendered image and jank the it out of PIL's scope for removal
    render_image = Image.open(image_path)
    render_np = np.array(render_image)
    Image.Image.close(render_image)
    render_image = Image.fromarray(render_np)
    os.remove(image_path)

    return render_image


# append existing material library if it exists
def save_material_library(
    path,
    material_name,
    diffuse_map,
    metalness_map,
    roughness_map,
    normal_map,
    displacement_map,
):
    """
    ------------------------------------------------
    Save a material to the material library

    Args:
    ------------------------------------------------
    path: path to the material library
    material_name: name of the material
    diffuse_map: A PIL image representing the diffuse map.
    metalness_map: A PIL image representing the metalness map.
    roughness_map: A PIL image representing the roughness map.
    normal_map: A PIL image representing the normal map.
    displacement_map: A PIL image representing the displacement map.

    Returns:
    ------------------------------------------------
    None
    """

    # clear the scene
    bpy.ops.wm.read_factory_settings(use_empty=True)

    # append an existing material library, if it exists
    if os.path.exists(path + "/materiallibrary.blend"):
        with bpy.data.libraries.load(path + "/materiallibrary.blend") as (
            data_from,
            data_to,
        ):
            data_to.materials = data_from.materials
            data_to.textures = data_from.textures
            data_to.node_groups = data_from.node_groups

    # check if material already exists and give it a unique name (e.g. material_001) 
    # also check if any subfixes are already present
    i = 0
    for mat in bpy.data.materials:
        if material_name in mat.name:
            i += 1
    if i > 0:
        material_name = material_name + "_" + str(i).zfill(2)

    mat = create_material(
        material_name,
        diffuse_map,
        metalness_map,
        roughness_map,
        normal_map,
        displacement_map,
    )

    # save the material library
    data_blocks = {*bpy.data.materials, *bpy.data.textures, *bpy.data.node_groups}
    save_file = path + "/materiallibrary.blend"
    bpy.data.libraries.write(save_file, data_blocks, fake_user=True, compress=True)
