#%%
import numpy as np
from PIL import Image
import cv2
from io import BytesIO

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
    '''
    ------------------------------------------------
    A function that blends two images using the soft light blend mode.

    Args:
    ------------------------------------------------
    arr1: A numpy array representing the first image.
    arr2: A numpy array representing the second image.

    Returns:
    ------------------------------------------------
    A numpy array representing the blended image.
    
    Source:
    ------------------------------------------------
    http://www.pegtop.net/delphi/articles/blendmodes/softlight.htm
    '''

    # compute soft light
    arr = (1 - 2*arr2) * arr1**2 + 2*arr2*arr1
    
    return arr

def range_upperlimit(arr, percentage):
    arr = arr * (percentage / 100)
    return arr

def range_lowerlimit(arr, percentage):
    arr = arr * percentage / 100 + (1 - percentage / 100)
    return arr

def range_midpoint(arr, percentage):
    midpoint = 0.5 * percentage / 100
    lower_bound = 0.5 - midpoint
    upper_bound = 0.5 + midpoint
    arr = cv2.normalize(arr, None, lower_bound, upper_bound, cv2.NORM_MINMAX, cv2.CV_32F)
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
# %%
