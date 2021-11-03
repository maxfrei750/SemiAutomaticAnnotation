from pathlib import Path
from typing import List, Tuple

import numpy as np
import pandas as pd
from dash import Input, Output, State, dcc, html
from PIL import Image

from app import app
from prediction import predict_masks, read_image
from visualization import visualize_annotation

from . import error_message
from .paths import ANNOTATED_ROOT, OUTPUT_ROOT


def gather_image_and_csv_paths() -> Tuple[List[str], List[str]]:
    csv_paths_unfiltered = list(ANNOTATED_ROOT.glob("*.csv"))

    image_paths = []
    csv_paths = []

    for csv_path in csv_paths_unfiltered:
        csv_path = Path(csv_path)
        image_identifier = csv_path.stem[11:]

        new_image_paths = list(ANNOTATED_ROOT.glob(f"image_{image_identifier}*"))

        # skip samples, where there is no 1:1 pair of csv and image files
        if len(new_image_paths) != 1:
            continue

        image_paths.append(str(new_image_paths[0]))
        csv_paths.append(str(csv_path))

    return image_paths, csv_paths


def get_layout():
    image_paths, csv_paths = gather_image_and_csv_paths()

    if csv_paths:
        layout = html.Div(
            [
                html.Center(
                    [
                        html.H1("There are annotated images."),
                        html.Button("Evaluate now", id="evaluate", n_clicks=0),
                    ]
                ),
                html.Div(id="dummy1"),
                dcc.Store(id="image-paths", data=image_paths),
                dcc.Store(id="csv-paths", data=csv_paths),
            ],
            style={"height": "98vh"},
        )
    else:
        layout = error_message.get_layout(
            "There are no valid pairs of csv- and image-files in folder 'annotated'."
        )
    return layout


@app.callback(
    Output("dummy1", "children"),
    Input("evaluate", "n_clicks"),
    State("image-paths", "data"),
    State("csv-paths", "data"),
    prevent_initial_call=True,
)
def evaluate_samples(_, image_paths, csv_paths):

    for csv_path, image_path in zip(csv_paths, image_paths):
        image = read_image(image_path)
        image_height, image_width, _ = image.shape

        image_identifier = Path(csv_path).stem[11:]

        boxes = pd.read_csv(csv_path)

        # normalize boxes
        boxes["x0"] /= image_width
        boxes["y0"] /= image_height
        boxes["x1"] /= image_width
        boxes["y1"] /= image_height

        # reorder coordinates
        boxes = boxes[["y0", "x0", "y1", "x1"]]

        boxes = boxes.to_numpy()

        masks = predict_masks(image, boxes)

        visualization_path = OUTPUT_ROOT / f"visualization_{image_identifier}.png"
        visualization = visualize_annotation(image, masks, boxes)
        visualization.save(visualization_path)

        # TODO: Save masks
        # TODO: Add progress bar
        # TODO: Move input image and annotations to "output"
