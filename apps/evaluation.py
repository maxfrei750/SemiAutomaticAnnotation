import shutil
from pathlib import Path
from typing import List, Tuple

import dash_bootstrap_components as dbc
import pandas as pd
from dash import Input, Output, State, dcc, html
from dash.development.base_component import Component
from PIL import Image

import custom_components
from app import app
from utilities.data import read_image
from utilities.paths import ANNOTATED_ROOT, RESULTS_ROOT, ROOT
from utilities.prediction import predict_masks
from utilities.visualization import visualize_annotation

# TODO: Progressbar? Store the initial number of files and compare with current number.


def gather_image_and_csv_paths() -> Tuple[List[str], List[str]]:
    """Gather pairs of images and csv annotation files.

    :return: List of image paths and list of csv paths.
    """
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


def get_layout() -> Component:
    """Get the layout of the evaluation app.

    :return: Layout of the evaluation app.
    """
    image_paths, csv_paths = gather_image_and_csv_paths()

    if csv_paths:
        layout = html.Div(
            [
                dcc.Location(id="url-evaluation", refresh=True),
                html.Center(
                    [
                        dbc.Spinner(
                            id="loading",
                            # type="default",
                            children=[
                                dbc.Button("start", id="evaluate", n_clicks=0),
                                html.Div(id="dummy-evaluation"),
                            ],
                        ),
                    ],
                    style={"margin-top": "10%"},
                ),
                dcc.Store(id="image-paths", data=image_paths),
                dcc.Store(id="csv-paths", data=csv_paths),
            ],
        )
    else:
        layout = custom_components.Message(
            [
                f"There are currently no valid pairs of csv- and image-files in the "
                f"'./{ANNOTATED_ROOT.relative_to(ROOT.parent)}' folder. Either ",
                html.A("annotate", href="/apps/annotation"),
                " some images, or inspect previously evaluated ",
                html.A("results", href="/apps/results"),
                ".",
            ]
        )
    return layout


@app.callback(
    Output("dummy-evaluation", "children"),
    Output("url-evaluation", "pathname"),
    Input("evaluate", "n_clicks"),
    State("image-paths", "data"),
    State("csv-paths", "data"),
    prevent_initial_call=True,
)
def evaluate_samples(_, image_paths: List[str], csv_paths: List[str]) -> Tuple[None, str]:
    """Evaluate samples.

    :param _: Mandatory callback input. Unused.
    :param image_paths: List of input image paths.
    :param csv_paths:  List of annotation csv paths.
    """

    for csv_path, image_path in zip(csv_paths, image_paths):
        csv_path = Path(csv_path)
        image_path = Path(image_path)

        image = read_image(image_path)
        image_identifier = csv_path.stem[11:]
        boxes = pd.read_csv(csv_path)
        masks = predict_masks(image, boxes)

        mask_root = RESULTS_ROOT / "masks"
        mask_root.mkdir(exist_ok=True, parents=True)

        for mask_id, mask in enumerate(masks):
            mask = mask > 0.5
            mask_path = mask_root / f"mask_{image_identifier}_{mask_id}.png"
            Image.fromarray(mask).save(mask_path)

        visualization_path = RESULTS_ROOT / f"visualization_{image_identifier}.png"
        visualization = visualize_annotation(image, masks, boxes)
        visualization.save(visualization_path)

        shutil.move(image_path, RESULTS_ROOT / image_path.name)
        shutil.move(csv_path, RESULTS_ROOT / csv_path.name)

    return None, "/apps/results"
