#%%
import numpy as np
from PIL import Image
#%%
# Helper functions
# Convert a PIL image to a numpy array
def tex_to_arr(tex):
    arr = np.array(tex)
    return arr

# Convert a numpy array to a PIL image
def arr_to_tex(arr):
    tex = Image.fromarray(arr)
    return tex

# Tiles a PIL image by a given number of times (tiles has to be a tuple)
def tex_tile(tex, tiles):
    arr = tex_to_arr(tex)
    arr = np.tile(arr, (tiles[0], tiles[1], 1))
    tex = arr_to_tex(arr)
    return tex

def tex_resize(tex, size):
    tex = tex.resize(size, Image.LANCZOS)
    return tex

def soft_light(arr1, arr2):
    # normalize to 0-1
    arr1 = arr1.astype(np.float32)/255
    arr2 = arr2.astype(np.float32)/255

    # compute soft light
    arr = (1 - 2*arr2) * arr1**2 + 2*arr2*arr1

    # convert back to 0-255
    arr = arr*255
    return arr

def crop_center(tex):
    w, h = tex.size
    if w == h:
        return tex
    else:
        min_dim = min(w, h)
        w_crop = (w - min_dim) // 2
        h_crop = (h - min_dim) // 2
        return tex.crop((w_crop, h_crop, w - w_crop, h - h_crop))