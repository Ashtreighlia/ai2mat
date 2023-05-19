# %%
import os
import sys
import PySimpleGUI as sg

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from PIL import Image, ImageTk

# necessary scripts
import helper

import ai2tex
import tex2mat
import renderengine

sg.theme("Dark Purple 4")

# %%
# Define the window's contents

# Define the interface
settings = [
    # Title
    [sg.HorizontalSeparator()],
    [sg.Text("AI2MAT", font='"Courier New" 32 bold', justification="center")],
    [sg.HorizontalSeparator()],
    # Texture generation
    [sg.Text("")],
    [sg.Text("Texture generation", font='"Courier New" 12 bold')],
    [sg.HorizontalSeparator()],
    [
        sg.Text("Material typ   ", font='"Courier New" 12'),
        sg.Input(key="-material_type-"),
    ],
    [
        sg.Text("Texture quality", font='"Courier New" 12'),
        sg.Radio("25", "texture_quality", key="qual_25"),
        sg.Radio("50", "texture_quality", key="qual_50", default=True),
        sg.Radio("75", "texture_quality", key="qual_75"),
        sg.Radio("100", "texture_quality", key="qual_100"),
    ],
    [
        sg.Text("Seam width     ", font='"Courier New" 12'),
        sg.Radio("16", "seam_width", key="seam_width_16"),
        sg.Radio("32", "seam_width", key="seam_width_32", default=True),
        sg.Radio("64", "seam_width", key="seam_width_64"),
        sg.Radio("128", "seam_width", key="seam_width_128"),
    ],
    [
        sg.Text("Seam quality   ", font='"Courier New" 12'),
        sg.Radio("10", "seam_quality", key="seam_qual_10"),
        sg.Radio("25", "seam_quality", key="seam_qual_25", default=True),
        sg.Radio("50", "seam_quality", key="seam_qual_50"),
        sg.Radio("75", "seam_quality", key="seam_qual_75"),
    ],
    [
        sg.Text("Load from file ", font='"Courier New" 12'),
        sg.In(size=(25, 1), enable_events=True, key="-RAW_FILE-"),
        sg.FileBrowse(),
        sg.Button("Load"),
    ],
    # Material synthesis
    [sg.Text("")],
    [sg.Text("Material synthesis", font='"Courier New" 12 bold')],
    [sg.HorizontalSeparator()],
    [
        sg.Text("Diffuse              ", font='"Courier New" 12'),
        sg.Slider(
            range=(0, 100),
            default_value=100,
            orientation="h",
            size=(25, 10),
            key="diffuse_strength",
        ),
    ],
    [
        sg.Text("Metallness           ", font='"Courier New" 12'),
        sg.Slider(
            range=(0, 100),
            default_value=100,
            orientation="h",
            size=(25, 10),
            key="metallness_strength",
        ),
    ],
    [
        sg.Text("Roughness            ", font='"Courier New" 12'),
        sg.Slider(
            range=(0, 100),
            default_value=100,
            orientation="h",
            size=(25, 10),
            key="roughness_strength",
        ),
    ],
    [
        sg.Text("Invert depth         ", font='"Courier New" 12'),
        sg.Slider(
            range=(0, 1),
            default_value=1,
            orientation="h",
            size=(25, 10),
            key="invert_depth",
        ),
    ],
    [
        sg.Text("Normal strength      ", font='"Courier New" 12'),
        sg.Slider(
            range=(0, 100),
            default_value=33,
            orientation="h",
            size=(25, 10),
            key="normal_strength",
        ),
    ],
    [
        sg.Text("Displacement strength", font='"Courier New" 12'),
        sg.Slider(
            range=(0, 100),
            default_value=100,
            orientation="h",
            size=(25, 10),
            key="displacement_strength",
        ),
    ],
    # Execution
    [sg.Text("")],
    [sg.Text("Execution", font='"Courier New" 12 bold')],
    [sg.HorizontalSeparator()],
    [
        sg.Text("Texture resolution", font='"Courier New" 12'),
        sg.Radio("32", "texture_resolution", key="tex_res_32"),
        sg.Radio("64", "texture_resolution", key="tex_res_64"),
        sg.Radio("128", "texture_resolution", key="tex_res_128", default=True),
        sg.Radio("256", "texture_resolution", key="tex_res_256"),
        sg.Radio("512", "texture_resolution", key="tex_res_512"),
    ],
    [
        sg.Text("Texture bit depth ", font='"Courier New" 12'),
        sg.Radio("2", "texture_bitdepth", key="tex_bit_2"),
        sg.Radio("3", "texture_bitdepth", key="tex_bit_3"),
        sg.Radio("4", "texture_bitdepth", key="tex_bit_4"),
        sg.Radio("8", "texture_bitdepth", key="tex_bit_8", default=True),
    ],
    [sg.HorizontalSeparator()],
    [
        sg.Push(),
        sg.Column(
            [
                [
                    sg.Text("Save"),
                    sg.In(size=(50, 1), enable_events=True, key="-SAVE_FOLDER-"),
                    sg.FolderBrowse(),
                ],
                [
                    sg.Button("Generate"),
                    sg.Button("Tile"),
                    sg.Button("Synthesize"),
                    sg.Button("Save"),
                ],
            ],
            element_justification="c",
        ),
        sg.Push(),
    ],
]

# Define preview images
previews = [
    [
        sg.Column(
            [
                [sg.Text("preview")],
                [sg.Image(size=(600, 400), key="-PREVIEW-")],
            ],
            size=(600, 400),
        )
    ],
    [
        sg.Column(
            [
                [sg.Text("diffuse")],
                [sg.Image(size=(200, 200), key="-PREVIEW_DIFF-")],
            ]
        ),
        sg.Column(
            [
                [sg.Text("roughness")],
                [sg.Image(size=(200, 200), key="-PREVIEW_ROUGH-")],
            ]
        ),
        sg.Column(
            [
                [sg.Text("metalness")],
                [sg.Image(size=(200, 200), key="-PREVIEW_METAL-")],
            ]
        ),
    ],
    [
        sg.Column(
            [
                [sg.Text("depth")],
                [sg.Image(size=(200, 200), key="-PREVIEW_DEPTH-")],
            ]
        ),
        sg.Column(
            [
                [sg.Text("normal")],
                [sg.Image(size=(200, 200), key="-PREVIEW_NORMAL-")],
            ]
        ),
        sg.Column(
            [
                [sg.Text("displacement")],
                [sg.Image(size=(200, 200), key="-PREVIEW_DISP-")],
            ]
        ),
    ],
]

# Create the layout by combining the interface and the preview images
layout = [
    [
        sg.Column(settings, vertical_alignment="top"),
        sg.Column(previews, vertical_alignment="top"),
    ]
]

# Create the window
window = sg.Window("AI2MAT", layout, finalize=True)

# Display and interact with the Window using an Event Loop
startup = True
while True:
    if startup:
        # create a checkerboard texture for the preview
        checkerboard = np.zeros((400, 600, 3), dtype=np.uint8)
        for i in range(400):
            for j in range(600):
                if (i // 50 + j // 50) % 2 == 0:
                    checkerboard[i, j] = (255, 255, 255)
        checkerboard = Image.fromarray(checkerboard)

        # update the preview images
        checkerboard_small = np.zeros((200, 200, 3), dtype=np.uint8)
        for i in range(200):
            for j in range(200):
                if (i // 50 + j // 50) % 2 == 0:
                    checkerboard_small[i, j] = (255, 255, 255)
        checkerboard_small = Image.fromarray(checkerboard_small)

        window["-PREVIEW_DIFF-"].update(data=ImageTk.PhotoImage(checkerboard_small))
        window["-PREVIEW_ROUGH-"].update(data=ImageTk.PhotoImage(checkerboard_small))
        window["-PREVIEW_METAL-"].update(data=ImageTk.PhotoImage(checkerboard_small))
        window["-PREVIEW_DEPTH-"].update(data=ImageTk.PhotoImage(checkerboard_small))
        window["-PREVIEW_NORMAL-"].update(data=ImageTk.PhotoImage(checkerboard_small))
        window["-PREVIEW_DISP-"].update(data=ImageTk.PhotoImage(checkerboard_small))

        # update the main preview
        window["-PREVIEW-"].update(data=ImageTk.PhotoImage(checkerboard))

        # set the startup flag to false
        startup = False

    event, values = window.read()

    if event == sg.WINDOW_CLOSED:
        break

    # get the values from the interface
    # material type
    material_type = values["-material_type-"]

    # quality of the texture
    if values["qual_25"]:
        quality = 25
    elif values["qual_50"]:
        quality = 50
    elif values["qual_75"]:
        quality = 75
    elif values["qual_100"]:
        quality = 100

    # seam width
    if values["seam_width_16"]:
        seam_width = 16
    elif values["seam_width_32"]:
        seam_width = 32
    elif values["seam_width_64"]:
        seam_width = 64
    elif values["seam_width_128"]:
        seam_width = 128

    # seam removal quality
    if values["seam_qual_10"]:
        seam_removal_quality = 10
    elif values["seam_qual_25"]:
        seam_removal_quality = 25
    elif values["seam_qual_50"]:
        seam_removal_quality = 50
    elif values["seam_qual_75"]:
        seam_removal_quality = 75

    # invert depth
    if values["invert_depth"] == 1:
        invert_depth = True
    else:
        invert_depth = False

    # diffuse
    diffuse_strength = values["diffuse_strength"]

    # metallness
    metallness_strength = values["metallness_strength"]

    # roughness
    roughness_strength = values["roughness_strength"]

    # normal strength
    normal_strength = values["normal_strength"]

    # displacement strength
    displacement_strength = values["displacement_strength"]

    # texture resolution
    if values["tex_res_32"]:
        tex_res = 32
    elif values["tex_res_64"]:
        tex_res = 64
    elif values["tex_res_128"]:
        tex_res = 128
    elif values["tex_res_256"]:
        tex_res = 256
    elif values["tex_res_512"]:
        tex_res = 512

    # texture bit depth
    if values["tex_bit_2"]:
        tex_bit = 2
    elif values["tex_bit_3"]:
        tex_bit = 3
    elif values["tex_bit_4"]:
        tex_bit = 4
    elif values["tex_bit_8"]:
        tex_bit = 8

    # generate the texture
    if event == "Generate":
        # create the texture
        if material_type == "":
            sg.popup_error("No material type entered!")

        else:
            prompt = ai2tex.prompt_create(material_type)
            tex = ai2tex.tex_create(prompt, 512, quality)

            # remove the seams
            tex = ai2tex.tex_shift(tex)
            mask = ai2tex.tex_mask_seam(tex, seam_width)
            tex = ai2tex.tex_seam(prompt, tex, mask, seam_removal_quality)
            tex = ai2tex.tex_shift(tex)

            mask = ai2tex.tex_mask_center(tex, seam_width)
            tex = ai2tex.tex_seam(prompt, tex, mask, seam_removal_quality)

            # texture to material
            raw, depth, diff, metal, rough, norm, disp = tex2mat.tex_to_mat(
                tex,
                invert_depth,
                diffuse_strength,
                metallness_strength,
                roughness_strength,
                normal_strength,
                displacement_strength,
                tex_bit,
            )

            preview = renderengine.render(diff, rough, metal, norm)
            window["-PREVIEW-"].update(data=ImageTk.PhotoImage(image=preview))

            diff_preview = diff.resize((200, 200))
            rough_preview = rough.resize((200, 200))
            metal_preview = metal.resize((200, 200))
            depth_preview = depth.resize((200, 200))
            norm_preview = norm.resize((200, 200))
            disp_preview = disp.resize((200, 200))

            window["-PREVIEW_DIFF-"].update(data=ImageTk.PhotoImage(image=diff_preview))
            window["-PREVIEW_ROUGH-"].update(
                data=ImageTk.PhotoImage(image=rough_preview)
            )
            window["-PREVIEW_METAL-"].update(
                data=ImageTk.PhotoImage(image=metal_preview)
            )
            window["-PREVIEW_DEPTH-"].update(
                data=ImageTk.PhotoImage(image=depth_preview)
            )
            window["-PREVIEW_NORMAL-"].update(
                data=ImageTk.PhotoImage(image=norm_preview)
            )
            window["-PREVIEW_DISP-"].update(data=ImageTk.PhotoImage(image=disp_preview))

    # check tiling of the texture
    if event == "Tile":
        tex_tile = helper.tex_tile(tex, (2, 2))
        tex_tile_preview = tex_tile.resize((600, 600))
        tex_tile_preview = tex_tile_preview.crop((0, 0, 400, 600))
        window["-PREVIEW-"].update(data=ImageTk.PhotoImage(image=tex_tile_preview))

    # synthesize the material from the texture
    if event == "Synthesize":
        raw, depth, diff, metal, rough, norm, disp = tex2mat.tex_to_mat(
            tex,
            invert_depth,
            diffuse_strength,
            metallness_strength,
            roughness_strength,
            normal_strength,
            displacement_strength,
            tex_bit,
        )

        preview = renderengine.render(diff, rough, metal, norm)
        window["-PREVIEW-"].update(data=ImageTk.PhotoImage(image=preview))

        diff_preview = diff.resize((200, 200))
        rough_preview = rough.resize((200, 200))
        metal_preview = metal.resize((200, 200))
        depth_preview = depth.resize((200, 200))
        norm_preview = norm.resize((200, 200))
        disp_preview = disp.resize((200, 200))

        window["-PREVIEW_DIFF-"].update(data=ImageTk.PhotoImage(image=diff_preview))
        window["-PREVIEW_ROUGH-"].update(data=ImageTk.PhotoImage(image=rough_preview))
        window["-PREVIEW_METAL-"].update(data=ImageTk.PhotoImage(image=metal_preview))
        window["-PREVIEW_DEPTH-"].update(data=ImageTk.PhotoImage(image=depth_preview))
        window["-PREVIEW_NORMAL-"].update(data=ImageTk.PhotoImage(image=norm_preview))
        window["-PREVIEW_DISP-"].update(data=ImageTk.PhotoImage(image=disp_preview))
        print("synthesized")

    if event == "Load":
        if values["-RAW_FILE-"] == "":
            sg.popup_error("Please select a directory to save the textures")
            continue

        else:
            # save the texture
            path = values["-RAW_FILE-"]
            tex = Image.open(path)

            # for possible future use for automated material synthesis from real world images
            """
            if loadtype_photo:
                if material_type == "":
                    sg.popup_error("No material type entered!")
                else:
                    helper.crop_center(tex)
                    tex = tex.resize((512, 512))

                    # remove the seams
                    prompt = ai2tex.prompt_create(material_type)
                    tex = ai2tex.tex_shift(tex)
                    mask = ai2tex.tex_mask_seam(tex, seam_width)
                    tex = ai2tex.tex_seam(prompt, tex, mask, seam_removal_quality)
                    tex = ai2tex.tex_shift(tex)

                    mask = ai2tex.tex_mask_center(tex, seam_width)
                    tex = ai2tex.tex_seam(prompt, tex, mask, seam_removal_quality)
            """

            tex_preview = tex.resize((400, 600))
            window["-PREVIEW-"].update(data=ImageTk.PhotoImage(image=tex_preview))

            # texture to material
            raw, diff, rough, metal, depth, norm, disp = tex2mat.tex_to_mat(
                tex,
                invert_depth,
                diffuse_strength,
                metallness_strength,
                roughness_strength,
                normal_strength,
                displacement_strength,
            )

            diff_preview = diff.resize((200, 200))
            rough_preview = rough.resize((200, 200))
            metal_preview = metal.resize((200, 200))
            depth_preview = depth.resize((200, 200))
            norm_preview = norm.resize((200, 200))
            disp_preview = disp.resize((200, 200))

            window["-PREVIEW_DIFF-"].update(data=ImageTk.PhotoImage(image=diff_preview))
            window["-PREVIEW_ROUGH-"].update(
                data=ImageTk.PhotoImage(image=rough_preview)
            )
            window["-PREVIEW_METAL-"].update(
                data=ImageTk.PhotoImage(image=metal_preview)
            )
            window["-PREVIEW_DEPTH-"].update(
                data=ImageTk.PhotoImage(image=depth_preview)
            )
            window["-PREVIEW_NORMAL-"].update(
                data=ImageTk.PhotoImage(image=norm_preview)
            )
            window["-PREVIEW_DISP-"].update(data=ImageTk.PhotoImage(image=disp_preview))

    # save the material to a folder and check if the folder exists already otherwise create a new one
    if event == "Save":
        if values["-SAVE_FOLDER-"] == "":
            sg.popup_error("Please select a directory to save the textures")
            continue

        else:
            # save the texture
            material_type = material_type.replace(" ", "-")
            path = values["-SAVE_FOLDER-"] + "/" + material_type
            if os.path.exists(path):
                # add a number to the end of the path
                i = 1
                while os.path.exists(path + str(i)):
                    i += 1
                path = path + str(i)

            os.mkdir(path)

            diff = helper.tex_resize(diff, (tex_res, tex_res))
            rough = helper.tex_resize(rough, (tex_res, tex_res))
            metal = helper.tex_resize(metal, (tex_res, tex_res))
            norm = helper.tex_resize(norm, (tex_res, tex_res))
            disp = helper.tex_resize(disp, (tex_res, tex_res))

            raw.save(path + "/" + material_type + "_raw.png")
            diff.save(path + "/" + material_type + "_diff.png")
            rough.save(path + "/" + material_type + "_rough.png")
            metal.save(path + "/" + material_type + "_metal.png")
            norm.save(path + "/" + material_type + "_norm.png")
            disp.save(path + "/" + material_type + "_disp.png")

        sg.popup("Textures successfully saved")


# Finish up by removing from the screen
window.close()
# %%
