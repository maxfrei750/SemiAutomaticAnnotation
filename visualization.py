import random
from typing import List, Optional

import numpy as np
from matplotlib import cm
from matplotlib.colors import LinearSegmentedColormap
from PIL import Image as PILImage
from PIL import ImageDraw, ImageOps
from skimage import img_as_ubyte

from custom_types import ColorFloat, ColorInt


def get_viridis_colors(num_colors: int) -> List[ColorFloat]:
    """Get a number of colors from the viridis color map, but leave out the very saturated colors
        at the beginning and end of the colormap.

    :param num_colors: Number of colors to be retrieved.
    :return: List of colors in float format.
    """
    color_min = (0.231, 0.322, 0.545)
    color_max = (0.369, 0.788, 0.384)

    if num_colors == 1:
        return [color_min]

    colormap = LinearSegmentedColormap.from_list("custom_viridis", colors=[color_min, color_max])

    colors = []

    for i in range(num_colors):
        color = colormap(i / (num_colors - 1))[:3]
        colors.append(color)

    return colors


def get_random_viridis_colors(num_colors: int) -> List[ColorFloat]:
    """Get a number of random colors from the viridis color map.

    :param num_colors: Number of colors to be retrieved.
    :return: List of colors in float format.
    """
    colors = []

    for i_color in range(num_colors):
        # color = cm.hsv(random.uniform(0, 0.6))

        colormap = cm.get_cmap("viridis")
        color = colormap(random.uniform(0, 1))
        colors.append(color)

    return colors


def visualize_annotation(
    image: np.ndarray,
    masks: Optional[np.ndarray] = None,
    boxes: Optional[np.ndarray] = None,
    line_width: int = 3,
) -> PILImage:
    """Overlay an image with an annotation of multiple instances.

    :param image: Image [Y, W, 3]
    :param masks: numpy array [N, H, W]
    :param boxes: normalized boxes in {y0,x0,y1,x1} format, numpy array [N, 4]
    :param display_mask_outlines_only: If true, only the outlines of masks are displayed.
    :param line_width: Line width for bounding boxes and mask outlines.
    :return: A PIL image object of the original image with overlayed annotations.
    """

    if masks is not None:
        num_instances = len(masks)
    elif boxes is not None:
        num_instances = len(boxes)
    else:
        raise ValueError("Neither masks nor boxes were specified.")

    image = img_as_ubyte(image)
    image = PILImage.fromarray(image)
    result = image.convert("RGB")

    colors_float = get_random_viridis_colors(num_instances)

    # unnormalize boxes
    boxes[:, [0, 2]] *= image.height
    boxes[:, [1, 3]] *= image.width

    for (
        mask,
        box,
        color_float,
    ) in zip(masks, boxes, colors_float):

        color_int = _color_float_to_int(color_float)

        if mask is not None:
            mask = mask.squeeze()

            mask = mask >= 0.5

            result = _overlay_image_with_mask(
                result,
                mask,
                color_int,
            )

        if box is not None:
            ImageDraw.Draw(result).rectangle(
                [(box[1], box[0]), (box[3], box[2])], outline=color_int, width=line_width
            )

    return result


def _color_float_to_int(color_float: ColorFloat) -> ColorInt:
    """Convert a color in float format into int format.

    :param color_float: Color in float format.
    :return: Color in int format.
    """
    color_int = (
        int(round(color_float[0] * 255)),
        int(round(color_float[1] * 255)),
        int(round(color_float[2] * 255)),
    )
    return color_int


def _overlay_image_with_mask(
    image: PILImage, mask: np.ndarray, color_int: ColorInt, alpha: float = 0.25
) -> PILImage:
    """Overlay an image with a mask.

    :param image: Image [H, W, 3]
    :param mask: nd.array [H, W]
    :param color_int: Color of the overlay in int format.
    :return: PIL image with overlayed mask.
    """
    overlay = PILImage.fromarray(mask).convert("L")
    mask_colored = ImageOps.colorize(overlay, black="black", white=color_int)

    mask = PILImage.fromarray(mask.astype(float) * alpha * 255).convert("L")

    image = PILImage.composite(mask_colored, image, mask)
    return image
