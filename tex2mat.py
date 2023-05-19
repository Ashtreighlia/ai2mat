# %%
import numpy as np
from PIL import Image
import cv2
from helper import tex_to_arr, arr_to_tex, soft_light, range_upperlimit, range_lowerlimit, range_midpoint


# %%
def tex_to_depth(tex, depth_invert=True):
    """
    ------------------------------------------------
    A function that converts a texture to a depth map.

    Args:
    ------------------------------------------------
    tex: A PIL image representing the texture.

    Returns:
    ------------------------------------------------
    A PIL image representing the depth map.
    """

    # Compute the Laplacian of the texture
    tex = cv2.cvtColor(tex, cv2.COLOR_RGB2GRAY)
    depth = cv2.Laplacian(tex, cv2.CV_32F, ksize=3)
    # Invert the depth map
    if depth_invert:
        depth = -depth

    depth = cv2.normalize(depth, None, 0, 1, cv2.NORM_MINMAX)
    depth = depth.astype(np.float32)
    return depth


def depth_to_norm(depth, strength):
    """
    ------------------------------------------------
    A function that converts a depth map to a normal map.

    Args:
    ------------------------------------------------
    depth: A PIL image representing the depth map.
    strength: A float representing the strength of the normal map.

    Returns:
    ------------------------------------------------
    A PIL image representing the normal map.
    """
    strength = (np.exp(strength / 10)) / np.exp(5)
    # Compute the gradient of the depth map
    dx = cv2.Scharr(depth, cv2.CV_64F, 1, 0)
    dy = cv2.Scharr(depth, cv2.CV_64F, 0, 1)
    # Compute the surface normal vectors from the gradient
    normal = np.dstack((-dx * strength, -dy * strength, np.ones_like(depth)))
    # Normalize the normal vectors keep rgb
    normal = normal / np.linalg.norm(normal, axis=2, keepdims=True)
    # Scale the normal vectors to the range [0, 1]
    normal = (normal - np.min(normal)) / (np.max(normal) - np.min(normal))
    # Center the mean of the normal vectors to 0.5
    normal = normal - np.mean(normal) + 0.5
    # Clip the values to the range [0, 1]
    normal = np.clip(normal, 0, 1)
    
    return normal


def depth_to_disp(depth, strength):
    """
    ------------------------------------------------
    A function that converts a depth map to a displacement map.

    Args:
    ------------------------------------------------
    depth: A PIL image representing the depth map.

    Returns:
    ------------------------------------------------
    A PIL image representing the displacement map.
    """

    disp = cv2.GaussianBlur(depth, (7, 7), 0)
    disp = range_midpoint(disp, strength)

    # center mean to 0.5
    disp = disp - np.mean(disp) + 0.5

    print(np.min(disp), np.max(disp))
    disp = np.clip(disp, 0, 1)

    return disp

def tex_to_diff(tex, strength):
    """
    ------------------------------------------------
    A function that converts a texture to a diffuse map.

    Args:
    ------------------------------------------------
    tex: A PIL image representing the texture.
    strength: A float representing the strength of lighting information removal.

    Returns:
    ------------------------------------------------
    A PIL image representing the diffuse map.
    """

    # compute the grayscale inverse of the texture
    gray = cv2.cvtColor(tex, cv2.COLOR_RGB2GRAY)
    inv = 1 - gray
    inv = cv2.cvtColor(inv, cv2.COLOR_GRAY2RGB)

    # remove the lighting information from the texture
    diff = soft_light(tex, inv)

    # adjust the strength of the diffuse map
    diff = diff * (strength / 100) + tex * (1 - strength / 100)
    diff = diff.astype(np.float32)
    print(np.min(diff), np.max(diff))
    return diff

def tex_to_rough(diffuse_map, normal_map, strength):
    """
    ------------------------------------------------
    A function that converts a texture to a roughness map.

    Args:
    ------------------------------------------------
    tex: A PIL image representing the texture.

    Returns:
    ------------------------------------------------
    A PIL image representing the roughness map.
    """

    diffuse_map = cv2.cvtColor(diffuse_map, cv2.COLOR_RGB2GRAY)
    diffuse_map = diffuse_map.astype(np.float32)
    # get the normal vectors from the normal map
    nx = normal_map[:, :, 0]
    ny = normal_map[:, :, 1]
    nz = normal_map[:, :, 2]

    rough = cv2.bilateralFilter(diffuse_map, 7, 50, 25) * 0.9 + 0.1 * np.sqrt(nx**2 + ny**2 + nz**2)

    rough = range_lowerlimit(rough, strength)
    return rough


def metallic_map(diffuse_map, roughness_map, normal_map, strength):
    """
    ------------------------------------------------
    A function that computes the metallic map from the base color map, roughness map, and depth map.

    Args:
    ------------------------------------------------
    diffuse_map: A PIL image representing the base color map.
    roughness_map: A PIL image representing the roughness map.
    depth_map: A PIL image representing the depth map.

    Returns:
    ------------------------------------------------
    A PIL image representing the metallic map.
    """
    
    # get the normal vectors from the normal map
    nx = normal_map[:, :, 0]
    ny = normal_map[:, :, 1]
    nz = normal_map[:, :, 2]

    # Compute the roughness value from the roughness map
    roughness = roughness_map.astype(np.float32) / 255.0

    # Compute the metallic map
    # convert base colour to hsv
    hsl = cv2.cvtColor(diffuse_map, cv2.COLOR_RGB2HSV)
    # get the saturation and lightness
    s = hsl[:, :, 1]
    v = hsl[:, :, 2]
    # compute the metallic value
    # the less saturated the reflected light of a surface is, the more metallic it is
    metalness = v * (1-s)
    metal = metalness * 0.8 + 0.1 * roughness + 0.1 * np.sqrt(nx**2 + ny**2 + nz**2)

    # adjust the strength of the metallic map
    metal = range_upperlimit(metal, strength)
    return metal


def tex_to_mat(
    tex,
    depth_invert,
    diff_strength,
    metallness_strength,
    roughness_strength,
    norm_strength,
    disp_strength,
    bit_depth,
):
    disp_strength = disp_strength + 1
    tex = (tex_to_arr(tex)/255).astype(np.float32)

    raw = tex
    depth = tex_to_depth(tex, depth_invert)
    normal = depth_to_norm(depth, norm_strength)
    disp = depth_to_disp(depth, disp_strength)
    diff = tex_to_diff(tex, diff_strength)
    rough = tex_to_rough(diff, normal, roughness_strength)
    metal = metallic_map(diff, rough, normal, metallness_strength)

    # convert the maps to the specified bit depth
    diff = ((255*diff).astype(np.uint8) >> (8 - bit_depth) << (8 - bit_depth))/255

    # ugly type conversion to please PIL in not fucking up the ranges
    raw = Image.fromarray((raw * 255).astype(np.uint8))
    depth = Image.fromarray((depth * 255).astype(np.uint8))
    diff = Image.fromarray((diff * 255).astype(np.uint8))
    metal = Image.fromarray((metal * 255).astype(np.uint8))
    rough = Image.fromarray((rough * 255).astype(np.uint8))
    normal = Image.fromarray((normal * 255).astype(np.uint8))
    disp = Image.fromarray((disp * 255).astype(np.uint8))

    return raw, depth, diff, metal, rough, normal, disp


import matplotlib.pyplot as plt

def main():
    tex = Image.open("./assets/brick-wall-surface/brick-wall-surface_color.png")
    raw, depth, diff, metal, rough, normal, disp = tex_to_mat(
        tex, 0, 100, 100, 1, 33, 100, 8
    )

    roughness = tex_to_arr(rough)
    print(np.min(roughness), np.max(roughness))

    # make a 3x3 grid of the textures
    fig, axs = plt.subplots(2, 3)
    axs[0, 0].imshow(diff)
    axs[0, 0].set_title("Diffuse")
    axs[0, 1].imshow(rough, cmap="gray")
    axs[0, 1].set_title("Roughness")
    axs[0, 2].imshow(metal, cmap="gray")
    axs[0, 2].set_title("Metallic")
    axs[1, 0].imshow(normal)
    axs[1, 0].set_title("Normal")
    axs[1, 1].imshow(disp, cmap="gray")
    axs[1, 1].set_title("Displacement")
    axs[1, 2].imshow(depth, cmap="gray")
    axs[1, 2].set_title("Depth")
    plt.show()

if __name__ == "__main__":
    main()

# %%
