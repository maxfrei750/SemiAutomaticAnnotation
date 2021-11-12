import json
import os

import numpy as np
import pandas as pd
import requests
import tensorflow as tf
from object_detection.utils import ops

from utilities import sort_box_coordinates

# TODO: Type annotations.
# TODO: Documentation.


def predict_masks(image: np.ndarray, boxes: pd.DataFrame) -> np.ndarray:
    """Predict instance masks for an image and a given set of boxes.

    :param image: input image [Y,X,3]
    :param boxes: pandas dataframe with columns ["y0", "x0", "y1", "x1"]
    :return: instance masks [N, Y, X]
    """

    image_height, image_width, _ = image.shape

    boxes = boxes.copy()

    # normalize boxes
    boxes["x0"] /= image_width
    boxes["y0"] /= image_height
    boxes["x1"] /= image_width
    boxes["y1"] /= image_height

    # reorder coordinates
    boxes = boxes[["y0", "x0", "y1", "x1"]]

    # Remove points outside of the image.
    boxes[boxes < 0] = 0
    boxes[boxes > 1] = 1

    sort_box_coordinates(boxes)

    boxes = boxes.to_numpy().astype(np.float32)

    inference_url = os.environ["MODEL_API_URL"]
    data = json.dumps(
        {
            "signature_name": "serving_default",
            "instances": [
                {
                    "input_tensor": image.tolist(),
                    "boxes": boxes.tolist(),
                }
            ],
        }
    )
    headers = {"content-type": "application/json"}
    response = requests.post(inference_url, data=data, headers=headers)
    masks = response.json()["predictions"][0]["detection_masks"]
    masks = ops.reframe_box_masks_to_image_masks(
        tf.convert_to_tensor(masks), tf.convert_to_tensor(boxes), image_height, image_width
    )
    return masks.numpy()
