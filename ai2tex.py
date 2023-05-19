# %%
import torch
import diffusers
from diffusers import StableDiffusionPipeline, StableDiffusionInpaintPipeline
diffusers.logging.set_verbosity_info()
import numpy as np
from PIL import Image, ImageDraw
import cv2

pipe_create = StableDiffusionPipeline.from_pretrained(
    "stabilityai/stable-diffusion-2-1-base", revision="fp16", torch_dtype=torch.float16)
pipe_create.to("cuda")
pipe_create.enable_xformers_memory_efficient_attention()
pipe_create.enable_model_cpu_offload()

pipe_inpaint = StableDiffusionInpaintPipeline.from_pretrained(
    "stabilityai/stable-diffusion-2-inpainting", torch_dtype=torch.float16)
pipe_inpaint.to("cuda")
pipe_inpaint.enable_xformers_memory_efficient_attention()
pipe_inpaint.enable_model_cpu_offload()

# %%

'''
Texture creation functions
'''


def prompt_create(material_type):
    '''
    ------------------------------------------------
    A function that creates a prompt for the texture creation.

    Args:
    ------------------------------------------------
    material_type: A string representing the type of the wanted material.

    Returns:
    ------------------------------------------------
    A string representing the prompt.
    '''

    prompt = "a realistic high detail texture of a " + material_type
    return prompt


def tex_create(prompt, size, num_inference_steps):
    '''
    ------------------------------------------------
    A function that creates a diffuse texture according to the given prompt by using StableDiffusion.

    Args:
    ------------------------------------------------
    promt: A string representing the prompt.
    height: An integer representing the height of the texture.
    width: An integer representing the width of the texture.
    num_inference_steps: An integer representing the number of inference steps.

    Returns:
    ------------------------------------------------
    A PIL image representing the created texture.
    '''
    with torch.inference_mode():
        tex = pipe_create(prompt, size, size, num_inference_steps).images[0]
        return tex


def tex_shift(tex):
    # Get image dimensions
    width, height = tex.size

    # Check if image is square
    if width != height:
        raise ValueError("Image must be square")

    # Split image into four quadrants
    top_left = tex.crop((0, 0, width//2, height//2))
    top_right = tex.crop((width//2, 0, width, height//2))
    bottom_left = tex.crop((0, height//2, width//2, height))
    bottom_right = tex.crop((width//2, height//2, width, height))

    # Shift quadrants
    top_left, top_right, bottom_left, bottom_right = bottom_right, bottom_left, top_right, top_left

    # Create a new image from the shifted quadrants
    new_tex = Image.new('RGB', (width, height))
    new_tex.paste(top_left, (0, 0))
    new_tex.paste(top_right, (width//2, 0))
    new_tex.paste(bottom_left, (0, height//2))
    new_tex.paste(bottom_right, (width//2, height//2))

    return new_tex


def tex_mask_seam(tex, seam_width):
    '''
    ------------------------------------------------
    A function that creates a mask for the seamremoval of the texture.

    Args:
    ------------------------------------------------
    tex: A PIL image representing the texture.
    seam_width: An integer representing the width of the seam.

    Returns:
    ------------------------------------------------
    A PIL image representing the mask.
    '''
    size = tex.size[0]
    mask = Image.new('RGB', (size, size), 'black')
    draw = ImageDraw.Draw(mask)
    draw.line((0, size/2, size, size/2), fill='white', width=seam_width)
    draw.line((size/2, 0, size/2, size), fill='white', width=seam_width)

    return mask


def tex_mask_center(tex, seam_width):
    '''
    ------------------------------------------------
    A function that creates a mask for the center of the texture.

    Args:
    ------------------------------------------------
    tex: A PIL image representing the texture.
    mask_size: An integer representing the size of the mask.

    Returns:
    ------------------------------------------------
    A PIL image representing the mask.
    '''
    size = tex.size[0]

    left = (size - seam_width) // 2
    top = (size - seam_width) // 2
    right = (size + seam_width) // 2
    bottom = (size + seam_width) // 2

    mask = Image.new('RGB', (size, size), 'black')

    draw = ImageDraw.Draw(mask)
    draw.rectangle((left, top, right, bottom), fill='white')

    return mask


def tex_seam(prompt, tex, mask, num_inference_steps):
    '''
    ------------------------------------------------
    A function that inpaints the texture according to the introduced seams by the shifting function.

    Args:
    ------------------------------------------------
    promt: A string representing the prompt.
    tex: A PIL image representing the texture.
    mask: A PIL image representing the mask.
    seam_width: An integer representing the width of the seam.
    num_inference_steps: An integer representing the number of inference steps.

    Returns:
    ------------------------------------------------
    A PIL image representing the inpainted texture.
    '''
    seamless = pipe_inpaint(prompt=prompt, image=tex, mask_image=mask,
                            num_inference_steps=num_inference_steps).images[0]
    return seamless