#%%
import numpy as np
from PIL import Image
import trimesh
import pyrender
import cv2

def create_material(diffuse_map, roughness_map, metallic_map, normal_map):
    # loads diffuse map
    diffuse = pyrender.Texture(source=diffuse_map, source_channels='RGB', width = 512, height = 512)
    
    # combine roughness and metallic into one texture, where roughness is stored in the green channel and metallic is stored in the blue channel
    metallic_roughness = np.zeros((512, 512, 3), dtype=np.uint8)
    roughness = np.array(roughness_map)
    metallic = np.array(metallic_map)
    # seems like glossiness is used instead of roughness, so the roughness is inverted
    metallic_roughness[:,:,1] = 255-roughness
    metallic_roughness[:,:,0] = metallic
    metallic_roughness = Image.fromarray(metallic_roughness)
    metallic_roughness = pyrender.Texture(source=metallic_roughness, source_channels='RGB', width = 512, height = 512)

    # loads normal map
    normal = pyrender.Texture(source=normal_map, source_channels='RGB', width = 512, height = 512)

    # Create material
    material = pyrender.MetallicRoughnessMaterial(baseColorTexture=diffuse, metallicRoughnessTexture=metallic_roughness, normalTexture=normal)

    return material

def render(diffuse_map, roughness_map, metallic_map, normal_map):
    # create scene
    scene = pyrender.Scene(bg_color=[0.0, 0.0, 0.0, 0.0])

    # load mesh from file
    cube_mesh = trimesh.load('./3D_model/cube.obj')
    mesh = pyrender.Mesh.from_trimesh(cube_mesh)
    # create texture coordinates for the mesh
    mesh.uvs = np.array([[0, 0], [0, 1], [1, 1], [1, 0]])
    mesh.uv_indices = np.array([[0, 1, 2], [0, 2, 3]])
    # add mesh to scene
    scene.add(mesh)

    # create camera
    camera = pyrender.PerspectiveCamera(yfov=np.pi / 3.0, aspectRatio=1.5)
    # set camera pose and add to scene
    camera_pose = np.eye(4)
    camera_pose[2, 3] = 1.075
    scene.add(camera, pose=camera_pose)

    # create light
    light = pyrender.SpotLight(color=np.ones(3), intensity=64.0,
                                innerConeAngle=np.pi/3.0,
                                outerConeAngle=np.pi/2.0)
    # set light pose and add to scene
    light_pose = np.eye(4)
    light_pose[:3, 3] = [1.0, 0.0, 2]
    scene.add(light, pose=light_pose)

    # load material and apply to mesh
    material = create_material(diffuse_map, roughness_map, metallic_map, normal_map)
    mesh.primitives[0].material = material

    # Render scene
    renderer = pyrender.OffscreenRenderer(600, 400)
    color, depth = renderer.render(scene)

    # Convert rendered image to PIL Image
    image = Image.fromarray(color)

    return image
# %%