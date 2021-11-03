import logging

import numpy as np

from prediction import predict_masks, read_image
from visualization import visualize_annotation

logging.disable(logging.WARNING)


def test_api():

    image_path = "/home/tensorflow/input/image3.jpg"

    image = read_image(image_path)

    boxes = np.array(
        [
            [0.000, 0.160, 0.362, 0.812],
            [0.340, 0.286, 0.472, 0.619],
            [0.437, 0.008, 0.650, 0.263],
            [0.382, 0.003, 0.538, 0.594],
            [0.518, 0.444, 0.625, 0.554],
        ]
    )

    masks = predict_masks(image, boxes)

    visualization = visualize_annotation(image, masks, boxes)
    visualization.save("output/test.png")


if __name__ == "__main__":
    test_api()
