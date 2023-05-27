# ![](./assets/ai2mat_logo.svg)

## Description
**ai2mat** is a tool for generating seamless textures/materials. It is built on top of [StableDiffusion](https://huggingface.co/spaces/stabilityai/stable-diffusion), a library for generative image generation. The program is written in Python and uses CUDA for GPU acceleration.

## Installation
Clone the repository and install the dependencies listed below.

**Dependencies**
- [Python 3.10.x](https://www.python.org/downloads/)
- [Pytorch](https://pytorch.org/get-started/locally/), with CUDA support.
- [Diffusers](https://huggingface.co/docs/diffusers/installation)
- [Transformers](https://huggingface.co/docs/transformers/installation)
- [Numpy](https://numpy.org/install/)
- [PIL](https://pillow.readthedocs.io/en/stable/installation.html)
- [cv2](https://pypi.org/project/opencv-python/)
- [PySimpleGUI](https://github.com/PySimpleGUI/PySimpleGUI)
- [Matplotlib](https://matplotlib.org/stable/users/installing.html)
- [pyrender](https://pyrender.readthedocs.io/en/latest/)
- [bpy](https://docs.blender.org/api/current/info_quickstart.html)

## Usage
![](./assets/ai2mat_usage.gif)

## Feature List
### Material synthesis
#### Generative
- [x] Texture generation
- [x] Texture seamless tiling
- [x] Material synthesis

#### Photographic
- [ ] Automated image pre-processing
- [ ] Automated image cropping
- [ ] Image seamless tiling
- [x] Material synthesis

### GUI
#### Generative material synthesis
- [x] Interface for texture generation
- [x] Interface for texture seamless tiling
- [x] Interface for material synthesis

#### Photographic material synthesis
- [ ] Interface for image pre-processing
- [ ] Interface for image seamless tiling
- [ ] Interface for image cropping

#### Controls
- [x] Controls for texture generation
- [x] Controls for export

## Improvements
- [ ] Remove lighting information from the colour output

## Examples
### Texture generation
| prompt | texture | tiling |
| --- | --- | --- |
| brick wall surface | ![](./assets/brick-wall-surface/brick-wall-surface_color.png) | ![](./assets/tile_preview/brick-wall-surface_tiled.jpg) |
| sandstone surface | ![](./assets/sandstone-surface/sandstone-surface_color.png) | ![](./assets/tile_preview/sandstone-surface_tiled.jpg) |
| tree bark surface | ![](./assets/tree-bark-surface/tree-bark-surface_color.png) | ![](./assets/tile_preview/tree-bark-surface_tiled.jpg) |
| wood surface | ![](./assets/wood-surface/wood-surface_color.png) | ![](./assets/tile_preview/wood-surface_tiled.jpg) |
| red leather surface | ![](./assets/red-leather-surface/red-leather-surface_color.png) | ![](./assets/tile_preview/red-leather-surface_tiled.jpg) |

### Material synthesis
| colour | metal | rough | norm | disp |
| --- | --- | --- | --- | --- |
| ![](./assets/brick-wall-surface/brick-wall-surface_color.png) | ![](./assets/brick-wall-surface/brick-wall-surface_metal.png) | ![](./assets/brick-wall-surface/brick-wall-surface_rough.png) | ![](./assets/brick-wall-surface/brick-wall-surface_norm.png) | ![](./assets/brick-wall-surface/brick-wall-surface_disp.png) |
| ![](./assets/sandstone-surface/sandstone-surface_color.png) | ![](./assets/sandstone-surface/sandstone-surface_metal.png) | ![](./assets/sandstone-surface/sandstone-surface_rough.png) | ![](./assets/sandstone-surface/sandstone-surface_norm.png) | ![](./assets/sandstone-surface/sandstone-surface_disp.png) |
| ![](./assets/tree-bark-surface/tree-bark-surface_color.png) | ![](./assets/tree-bark-surface/tree-bark-surface_metal.png) | ![](./assets/tree-bark-surface/tree-bark-surface_rough.png) | ![](./assets/tree-bark-surface/tree-bark-surface_norm.png) | ![](./assets/tree-bark-surface/tree-bark-surface_disp.png) |
| ![](./assets/wood-surface/wood-surface_color.png) | ![](./assets/wood-surface/wood-surface_metal.png) | ![](./assets/wood-surface/wood-surface_rough.png) | ![](./assets/wood-surface/wood-surface_norm.png) | ![](./assets/wood-surface/wood-surface_disp.png) |
| ![](./assets/red-leather-surface/red-leather-surface_color.png) | ![](./assets/red-leather-surface/red-leather-surface_metal.png) | ![](./assets/red-leather-surface/red-leather-surface_rough.png) | ![](./assets/red-leather-surface/red-leather-surface_norm.png) | ![](./assets/red-leather-surface/red-leather-surface_disp.png) |

## Contributing
Contributions are welcome, just open an issue or a pull request.

## License
The code is licensed under the [MIT License](./LICENSE).
