import numpy as np
import pandas as pd
import tensorflow as tf
from PIL import Image

from custom_types import AnyPath

# TODO: Create module utilities. Move visualization and prediction there.
# TODO: Type annotations.
# TODO: Documentation.


def read_image(path: AnyPath) -> np.array:
    """Read an image.

    :param path: input path
    :return: image [Y, X, 3]
    """
    with tf.io.gfile.GFile(path, "rb") as f:
        image = Image.open(f).convert("RGB")
        return np.array(image, dtype=np.uint8)


def sort_box_coordinates(boxes: pd.DataFrame) -> pd.DataFrame:
    """Ensure that x0<x1 and y0<y1.

    :param boxes: dataframe with columns ["x0", "x1", "y0", "y1"].
    :return: dataframe with columns ["x0", "x1", "y0", "y1"], where x0<x1 and y0<y1.
    """

    boxes_unsorted = boxes.copy()
    boxes["x0"] = boxes_unsorted[["x0", "x1"]].min(axis=1)
    boxes["x1"] = boxes_unsorted[["x0", "x1"]].max(axis=1)
    boxes["y0"] = boxes_unsorted[["y0", "y1"]].min(axis=1)
    boxes["y1"] = boxes_unsorted[["y0", "y1"]].max(axis=1)
