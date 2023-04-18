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