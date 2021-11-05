from pathlib import Path
from typing import List, Tuple

import numpy as np
import pandas as pd
from dash import Input, Output, State, dcc, html
from PIL import Image

from app import app
from prediction import predict_masks
from utilities import read_image
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


def get_layout() -> html.Div:
    image_paths, csv_paths = gather_image_and_csv_paths()

    if csv_paths:
        layout = html.Div(
            [
                html.Center(
                    [
                        html.H1("Evaluation"),
                        dcc.Loading(
                            id="loading",
                            type="default",
                            children=html.Button("start", id="evaluate", n_clicks=0),
                        ),
                    ]
                ),
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
    Output("evaluate", "children"),
    Input("evaluate", "n_clicks"),
    State("image-paths", "data"),
    State("csv-paths", "data"),
    prevent_initial_call=True,
)
def evaluate_samples(_, image_paths: List[str], csv_paths: List[str]):

    for csv_path, image_path in zip(csv_paths, image_paths):
        image = read_image(image_path)
        image_identifier = Path(csv_path).stem[11:]
        boxes = pd.read_csv(csv_path)
        masks = predict_masks(image, boxes)

        for mask_id, mask in enumerate(masks):
            mask = mask > 0.5
            mask_path = OUTPUT_ROOT / f"mask_{image_identifier}_{mask_id}.png"
            Image.fromarray(mask).save(mask_path)

        visualization_path = OUTPUT_ROOT / f"visualization_{image_identifier}.png"
        visualization = visualize_annotation(image, masks, boxes)
        visualization.save(visualization_path)

        # TODO: Move input image and annotations to "output"

    return "start"
