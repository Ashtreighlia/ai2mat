#%%
import numpy as np
from PIL import Image
import cv2
from helper import tex_to_arr, arr_to_tex
#%%
def tex_to_depth(tex, depth_invert=True):
    '''
    ------------------------------------------------
    A function that converts a texture to a depth map.

    Args:
    ------------------------------------------------
    tex: A PIL image representing the texture.

    Returns:
    ------------------------------------------------
    A PIL image representing the depth map.
    '''

    tex = tex.convert('L')
    arr = tex_to_arr(tex)

    # Compute the Laplacian of the texture
    arr = cv2.Laplacian(arr, cv2.CV_64F, ksize=3)
    # Invert the depth map
    if depth_invert:
        arr = -arr

    arr = cv2.normalize(arr, None, 0, 255, cv2.NORM_MINMAX)
    arr.astype(np.uint8)
    depth = arr_to_tex(arr)
    depth.convert('L')
    return depth

def depth_to_norm(depth, strength):
    '''
    ------------------------------------------------
    A function that converts a depth map to a normal map.

    Args:
    ------------------------------------------------
    depth: A PIL image representing the depth map.
    strength: A float representing the strength of the normal map.

    Returns:
    ------------------------------------------------
    A PIL image representing the normal map.
    '''
    strength = (np.exp(strength / 10))/np.exp(10)
    arr = tex_to_arr(depth)
    # Compute the gradient of the depth map
    dx = cv2.Scharr(arr, cv2.CV_64F, 1, 0)
    dy = cv2.Scharr(arr, cv2.CV_64F, 0, 1)
    # Compute the surface normal vectors from the gradient
    normal = np.dstack((-dx*strength, -dy*strength, np.ones_like(arr)))
    # Normalize the normal vectors keep rgb
    normal = normal / np.linalg.norm(normal, axis=2, keepdims=True)
    # Scale the normal vectors to the range [0, 255]
    normal = (normal - np.min(normal)) / (np.max(normal) - np.min(normal)) * 255
    # Center the mean of the normal vectors to 127
    normal = normal - np.mean(normal) + 127
    # Clip the values to the range [0, 255]
    normal = np.clip(normal, 0, 255)
    normal = normal.astype(np.uint8)
    normal = arr_to_tex(normal)
    return normal


def depth_to_disp(depth, strength):
    '''
    ------------------------------------------------
    A function that converts a depth map to a displacement map.
    
    Args:
    ------------------------------------------------
    depth: A PIL image representing the depth map.

    Returns:
    ------------------------------------------------
    A PIL image representing the displacement map.
    '''

    arr = tex_to_arr(depth)
    arr = cv2.GaussianBlur(arr, (7, 7), 0)
    arr = cv2.normalize(arr, None, 0, 255, cv2.NORM_MINMAX, cv2.CV_8UC1)
    ## scale the displacement by the strength
    strength = 255/2 * strength/100
    lower_bound = 255/2 - strength
    upper_bound = 255/2 + strength
    arr = cv2.normalize(arr, None, lower_bound, upper_bound, cv2.NORM_MINMAX, cv2.CV_8UC1)

    arr = arr.astype(np.uint8)
    disp = arr_to_tex(arr)
    disp.convert('L')
    return disp


def tex_to_rough(tex, strength):
    '''
    ------------------------------------------------
    A function that converts a texture to a roughness map.
    
    Args:
    ------------------------------------------------
    tex: A PIL image representing the texture.

    Returns:
    ------------------------------------------------
    A PIL image representing the roughness map.
    '''

    tex = tex.convert('L')
    arr = tex_to_arr(tex)

    arr = cv2.bilateralFilter(arr, 7, 50, 25)
    arr = cv2.normalize(arr, None, 0, 255, cv2.NORM_MINMAX, cv2.CV_8UC1)

    strength = 255/2 * strength/100
    lower_bound = 255/2 - strength
    arr = cv2.normalize(arr, None, lower_bound, 255, cv2.NORM_MINMAX, cv2.CV_8UC1)

    arr = arr.astype(np.uint8)
    rough = arr_to_tex(arr)
    rough.convert('L')
    return rough


def metallic_map(base_color_map, roughness_map, depth_map, strength):
    '''
    ------------------------------------------------
    A function that computes the metallic map from the base color map, roughness map, and depth map.
    
    Args:
    ------------------------------------------------
    base_color_map: A PIL image representing the base color map.
    roughness_map: A PIL image representing the roughness map.
    depth_map: A PIL image representing the depth map.

    Returns:
    ------------------------------------------------
    A PIL image representing the metallic map.
    '''

    base_color_map = tex_to_arr(base_color_map)
    roughness_map = tex_to_arr(roughness_map)
    depth_map = tex_to_arr(depth_map)

    # Convert depth map to float and normalize to range 0-1
    depth_map = depth_map.astype(np.float32) / 255.0
    # Compute the gradient of the depth map
    dx, dy = np.gradient(depth_map)
    # Compute the surface normal vectors from the gradient
    nx = -dx
    ny = -dy
    nz = np.ones_like(depth_map)
    norm = np.sqrt(nx**2 + ny**2 + nz**2)
    nx = nx / norm
    ny = ny / norm
    nz = nz / norm

    # Compute the roughness value from the roughness map
    roughness = roughness_map.astype(np.float32) / 255.0
    # Compute the metallic map
    metal = np.zeros_like(base_color_map)
    for i in range(3):
        metal[:, :, i] = (1 - roughness) * (base_color_map[:, :, i] * 0.04 + 0.96 * np.maximum(
            nx*base_color_map[:, :, 0] + ny*base_color_map[:, :, 1] + nz*base_color_map[:, :, 2], 0))
    metal = cv2.normalize(metal, None, 0, 255, cv2.NORM_MINMAX, cv2.CV_8UC1)

    strength = 255/2 * strength/100
    upper_bound = 255/2 + strength
    metal = cv2.normalize(metal, None, 0, upper_bound, cv2.NORM_MINMAX, cv2.CV_8UC1)

    metal = metal.astype(np.uint8)
    metal = arr_to_tex(metal)
    metal.convert('L')
    return metal

def tex_to_mat(tex, depth_invert, metallness, roughness, norm_strength, disp_strength):
    color = tex
    depth = tex_to_depth(tex, depth_invert)
    normal = depth_to_norm(depth, norm_strength)
    disp = depth_to_disp(depth, disp_strength)
    rough = tex_to_rough(tex, roughness)
    metal = metallic_map(tex, rough, depth, metallness)

    return color, rough, metal, depth, normal, disp
# %%
