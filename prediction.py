import json
import os

import numpy as np
import requests
import tensorflow as tf
from object_detection.utils import ops


def predict_masks(image: np.ndarray, boxes: np.ndarray) -> np.ndarray:
    """Predict instance masks for an image and a given set of boxes.

    :param image: input image [Y,X,3]
    :param boxes: pandas dataframe with columns ["y0", "x0", "y1", "x1"]
    :return: instance masks [N, Y, X]
    """

    image_height, image_width, _ = image.shape

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

    # Ensure that x0<x1 and y0<y1.
    boxes_unsorted = boxes.copy()

    boxes["x0"] = boxes_unsorted[["x0", "x1"]].min(axis=1)
    boxes["x1"] = boxes_unsorted[["x0", "x1"]].max(axis=1)
    boxes["y0"] = boxes_unsorted[["y0", "y1"]].min(axis=1)
    boxes["y1"] = boxes_unsorted[["y0", "y1"]].max(axis=1)

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
