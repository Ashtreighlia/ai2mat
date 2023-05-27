# %%
import numpy as np
import PySimpleGUI as sg
from PIL import Image, ImageTk

import ai2tex
import blenderengine
import helper
import tex2mat

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
        sg.Radio("25", "seam_quality", key="seam_qual_25", default=True),
        sg.Radio("50", "seam_quality", key="seam_qual_50"),
        sg.Radio("75", "seam_quality", key="seam_qual_75"),
        sg.Radio("100", "seam_quality", key="seam_qual_100"),
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
        sg.Text("Invert metalness     ", font='"Courier New" 12'),
        sg.Radio("True", "metalness_invert", key="metalness_invert_true"),
        sg.Radio(
            "False", "metalness_invert", key="metalness_invert_false", default=True
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
        sg.Text("Invert roughness     ", font='"Courier New" 12'),
        sg.Radio("True", "roughness_invert", key="roughness_invert_true"),
        sg.Radio(
            "False", "roughness_invert", key="roughness_invert_false", default=True
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
        sg.Radio("True", "depth_invert", key="depth_invert_true"),
        sg.Radio("False", "depth_invert", key="depth_invert_false", default=True),
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
        sg.Text("Light rotation  ", font='"Courier New" 12'),
        sg.Slider(
            range=(0, 100),
            default_value=100,
            orientation="h",
            size=(25, 10),
            key="light_rotation",
        ),
    ],
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
        sg.Radio("2", "texture_bitdepth", key="bit_depth_2"),
        sg.Radio("3", "texture_bitdepth", key="bit_depth_3"),
        sg.Radio("4", "texture_bitdepth", key="bit_depth_4"),
        sg.Radio("8", "texture_bitdepth", key="bit_depth_8", default=True),
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
                    sg.Button("Retile"),
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
                [sg.Text("render")],
                [sg.Image(size=(600, 600), key="-PREVIEW_RENDER-")],
            ],
        ),
        sg.Column(
            [
                [sg.Text("tiling")],
                [sg.Image(size=(600, 600), key="-PREVIEW_TILE-")],
            ],
        ),
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

# global variable for the PIL image object, representing the texture
tex = None

# Display and interact with the Window using an Event Loop
startup = True
while True:
    if startup:
        # create a checkerboard texture for the tile preview
        checkerboard_tile = np.zeros((600, 600, 3), dtype=np.uint8)
        for i in range(600):
            for j in range(600):
                if (i // 50 + j // 50) % 2 == 0:
                    checkerboard_tile[i, j] = (255, 255, 255)
        checkerboard_tile = Image.fromarray(checkerboard_tile)
        checkerboard_render = checkerboard_tile

        # update the preview images
        checkerboard_small = np.zeros((200, 200, 3), dtype=np.uint8)
        for i in range(200):
            for j in range(200):
                if (i // 50 + j // 50) % 2 == 0:
                    checkerboard_small[i, j] = (255, 255, 255)
        checkerboard_small = Image.fromarray(checkerboard_small)

        # update the tile preview
        window["-PREVIEW_TILE-"].update(data=ImageTk.PhotoImage(checkerboard_tile))

        # update the render preview
        window["-PREVIEW_RENDER-"].update(data=ImageTk.PhotoImage(checkerboard_render))

        # update the material previews
        window["-PREVIEW_DIFF-"].update(data=ImageTk.PhotoImage(checkerboard_small))
        window["-PREVIEW_ROUGH-"].update(data=ImageTk.PhotoImage(checkerboard_small))
        window["-PREVIEW_METAL-"].update(data=ImageTk.PhotoImage(checkerboard_small))
        window["-PREVIEW_DEPTH-"].update(data=ImageTk.PhotoImage(checkerboard_small))
        window["-PREVIEW_NORMAL-"].update(data=ImageTk.PhotoImage(checkerboard_small))
        window["-PREVIEW_DISP-"].update(data=ImageTk.PhotoImage(checkerboard_small))

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
    if values["seam_qual_25"]:
        seam_removal_quality = 25
    elif values["seam_qual_50"]:
        seam_removal_quality = 50
    elif values["seam_qual_75"]:
        seam_removal_quality = 75
    elif values["seam_qual_100"]:
        seam_removal_quality = 100

    # invert metalness
    if values["metalness_invert_true"]:
        invert_metalness = True
    else:
        invert_metalness = False

    # invert roughness
    if values["roughness_invert_true"]:
        invert_roughness = True
    else:
        invert_roughness = False

    # invert depth
    if values["depth_invert_true"]:
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

    # light rotation
    light_rotation = values["light_rotation"]

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
    if values["bit_depth_2"]:
        bit_depth = 2
    elif values["bit_depth_3"]:
        bit_depth = 3
    elif values["bit_depth_4"]:
        bit_depth = 4
    elif values["bit_depth_8"]:
        bit_depth = 8

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
                diffuse_strength,
                invert_metalness,
                metallness_strength,
                invert_roughness,
                roughness_strength,
                invert_depth,
                normal_strength,
                displacement_strength,
                bit_depth,
            )

            tex_tile = helper.tex_downsize(tex, (tex_res, tex_res))
            tex_tile = helper.tex_tile(tex_tile, (3, 3))
            tex_tile = helper.tex_upsize(tex_tile, (600, 600))
            window["-PREVIEW_TILE-"].update(data=ImageTk.PhotoImage(image=tex_tile))

            diff = helper.tex_downsize(diff, (tex_res, tex_res))
            rough = helper.tex_downsize(rough, (tex_res, tex_res))
            metal = helper.tex_downsize(metal, (tex_res, tex_res))
            norm = helper.tex_downsize(norm, (tex_res, tex_res))
            disp = helper.tex_downsize(disp, (tex_res, tex_res))

            preview = blenderengine.render_material(
                light_rotation, "preview_material", diff, rough, metal, norm, disp
            )
            window["-PREVIEW_RENDER-"].update(data=ImageTk.PhotoImage(image=preview))

            diff_preview = helper.tex_upsize(diff, (200, 200))
            rough_preview = helper.tex_upsize(rough, (200, 200))
            metal_preview = helper.tex_upsize(metal, (200, 200))
            depth_preview = helper.tex_upsize(depth, (200, 200))
            norm_preview = helper.tex_upsize(norm, (200, 200))
            disp_preview = helper.tex_upsize(disp, (200, 200))

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

    if event == "Retile":
        if tex == None:
            print(tex)
            sg.popup_error("No material present!")

        else:
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
                diffuse_strength,
                invert_metalness,
                metallness_strength,
                invert_roughness,
                roughness_strength,
                invert_depth,
                normal_strength,
                displacement_strength,
                bit_depth,
            )

            tex_tile = helper.tex_downsize(tex, (tex_res, tex_res))
            tex_tile = helper.tex_tile(tex_tile, (3, 3))
            tex_tile = helper.tex_upsize(tex_tile, (600, 600))
            window["-PREVIEW_TILE-"].update(data=ImageTk.PhotoImage(image=tex_tile))

            diff = helper.tex_downsize(diff, (tex_res, tex_res))
            rough = helper.tex_downsize(rough, (tex_res, tex_res))
            metal = helper.tex_downsize(metal, (tex_res, tex_res))
            norm = helper.tex_downsize(norm, (tex_res, tex_res))
            disp = helper.tex_downsize(disp, (tex_res, tex_res))

            preview = blenderengine.render_material(
                light_rotation, "preview_material", diff, rough, metal, norm, disp
            )
            window["-PREVIEW_RENDER-"].update(data=ImageTk.PhotoImage(image=preview))

            diff_preview = helper.tex_upsize(diff, (200, 200))
            rough_preview = helper.tex_upsize(rough, (200, 200))
            metal_preview = helper.tex_upsize(metal, (200, 200))
            depth_preview = helper.tex_upsize(depth, (200, 200))
            norm_preview = helper.tex_upsize(norm, (200, 200))
            disp_preview = helper.tex_upsize(disp, (200, 200))

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

    # synthesize the material from the texture
    if event == "Synthesize":
        if tex == None:
            sg.popup_error("No material present!")

        else:
            raw, depth, diff, metal, rough, norm, disp = tex2mat.tex_to_mat(
                tex,
                diffuse_strength,
                invert_metalness,
                metallness_strength,
                invert_roughness,
                roughness_strength,
                invert_depth,
                normal_strength,
                displacement_strength,
                bit_depth,
            )

            tex_tile = helper.tex_downsize(tex, (tex_res, tex_res))
            tex_tile = helper.tex_tile(tex_tile, (3, 3))
            tex_tile = helper.tex_upsize(tex_tile, (600, 600))
            window["-PREVIEW_TILE-"].update(data=ImageTk.PhotoImage(image=tex_tile))

            diff = helper.tex_downsize(diff, (tex_res, tex_res))
            rough = helper.tex_downsize(rough, (tex_res, tex_res))
            metal = helper.tex_downsize(metal, (tex_res, tex_res))
            norm = helper.tex_downsize(norm, (tex_res, tex_res))
            disp = helper.tex_downsize(disp, (tex_res, tex_res))

            preview = blenderengine.render_material(
                light_rotation, "preview_material", diff, rough, metal, norm, disp
            )
            window["-PREVIEW_RENDER-"].update(data=ImageTk.PhotoImage(image=preview))

            diff_preview = helper.tex_upsize(diff, (200, 200))
            rough_preview = helper.tex_upsize(rough, (200, 200))
            metal_preview = helper.tex_upsize(metal, (200, 200))
            depth_preview = helper.tex_upsize(depth, (200, 200))
            norm_preview = helper.tex_upsize(norm, (200, 200))
            disp_preview = helper.tex_upsize(disp, (200, 200))

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
            print("synthesized")

    if event == "Load":
        if values["-RAW_FILE-"] == "":
            sg.popup_error("Please select a directory to save the textures")
            continue

        else:
            # save the texture
            path = values["-RAW_FILE-"]
            tex = Image.open(path)

            # texture to material
            raw, diff, rough, metal, depth, norm, disp = tex2mat.tex_to_mat(
                tex,
                diffuse_strength,
                invert_metalness,
                metallness_strength,
                invert_roughness,
                roughness_strength,
                invert_depth,
                normal_strength,
                displacement_strength,
                bit_depth,
            )

            diff = helper.tex_downsize(diff, (tex_res, tex_res))
            rough = helper.tex_downsize(rough, (tex_res, tex_res))
            metal = helper.tex_downsize(metal, (tex_res, tex_res))
            norm = helper.tex_downsize(norm, (tex_res, tex_res))
            disp = helper.tex_downsize(disp, (tex_res, tex_res))

            preview = blenderengine.render_material(
                light_rotation, "preview_material", diff, rough, metal, norm, disp
            )
            window["-PREVIEW_RENDER-"].update(data=ImageTk.PhotoImage(image=preview))

            diff_preview = helper.tex_upsize(diff, (200, 200))
            rough_preview = helper.tex_upsize(rough, (200, 200))
            metal_preview = helper.tex_upsize(metal, (200, 200))
            depth_preview = helper.tex_upsize(depth, (200, 200))
            norm_preview = helper.tex_upsize(norm, (200, 200))
            disp_preview = helper.tex_upsize(disp, (200, 200))

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

    # save the material to a blender library
    if event == "Save":
        if values["-SAVE_FOLDER-"] == "":
            sg.popup_error("Please select a directory to save the textures")
            continue

        else:
            # save the texture
            material_type = material_type.replace(" ", "-")

            diff = helper.tex_downsize(diff, (tex_res, tex_res))
            rough = helper.tex_downsize(rough, (tex_res, tex_res))
            metal = helper.tex_downsize(metal, (tex_res, tex_res))
            norm = helper.tex_downsize(norm, (tex_res, tex_res))
            disp = helper.tex_downsize(disp, (tex_res, tex_res))

            # add to blender library
            blenderengine.save_material_library(
                values["-SAVE_FOLDER-"],
                material_type,
                diff,
                metal,
                rough,
                norm,
                disp,
            )
        sg.popup("Textures successfully saved")

# Finish up by removing from the screen
window.close()
