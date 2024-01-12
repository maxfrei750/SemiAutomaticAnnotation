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

    num_samples = len(image_paths)

    if csv_paths:
        layout = html.Div(
            [
                dcc.Location(id="url-evaluation", refresh=True),
                html.Center(
                    [
                        dbc.Spinner(
                            id="loading",
                            size="lg",
                            children=[
                                dcc.RadioItems(
                                    ["Deep-MARC", "Deep-MAC"],
                                    "Deep-MARC",
                                    id="model-selection",
                                    style={"margin-bottom": "10%"},
                                ),
                                dbc.Button("Start", id="evaluate", n_clicks=0, size="lg"),
                                html.Div(id="dummy-evaluation"),
                            ],
                        ),
                    ],
                    style={"margin-top": "10%"},
                ),
                dbc.Col(
                    dbc.Progress(
                        id="progress-evaluation",
                        max=num_samples,
                    ),
                    width={"size": 6, "offset": 3},
                    style={"margin-top": "2%"},
                ),
                dcc.Interval(id="interval-progress", interval=1000),
                dcc.Store(id="image-paths", data=image_paths),
                dcc.Store(id="csv-paths", data=csv_paths),
            ],
        )
    else:
        layout = custom_components.Message(
            dcc.Markdown(
                f"There are currently no valid pairs of csv- and image-files in the "
                f"`./{ANNOTATED_ROOT.relative_to(ROOT.parent)}` folder. Either **[annotate](/apps/annotation)** some "
                f"images or inspect previously evaluated **[results](/apps/results)**."
            )
        )
    return layout


@app.callback(
    Output("progress-evaluation", "value"),
    Input("interval-progress", "n_intervals"),
    State("image-paths", "data"),
    prevent_initial_call=True,
)
def update_progress(_, image_paths: List[str]) -> int:
    num_samples_total = len(image_paths)
    num_samples_left = len(gather_image_and_csv_paths()[0])

    sample_index = num_samples_total - num_samples_left

    return sample_index


@app.callback(
    Output("dummy-evaluation", "children"),
    Output("url-evaluation", "pathname"),
    Input("evaluate", "n_clicks"),
    State("model-selection", "value"),
    State("image-paths", "data"),
    State("csv-paths", "data"),
    prevent_initial_call=True,
)
def evaluate_samples(
    _, model_selection: str, image_paths: List[str], csv_paths: List[str]
) -> Tuple[None, str]:
    """Evaluate samples.

    :param _: Mandatory callback input. Unused.
    :param model_selection: Model selection.
    :param image_paths: List of input image paths.
    :param csv_paths:  List of annotation csv paths.
    """

    print(f"🚀🚀🚀🚀 Evaluating with {model_selection}...", flush=True)

    models = {"Deep-MAC": "deepmac", "Deep-MARC": "deepmarc"}
    model_name = models[model_selection]
    model_results_root = RESULTS_ROOT / model_name

    for csv_path, image_path in zip(csv_paths, image_paths):
        csv_path = Path(csv_path)
        image_path = Path(image_path)

        image = read_image(image_path)
        image_identifier = csv_path.stem[11:]
        boxes = pd.read_csv(csv_path)
        masks = predict_masks(image, boxes, model_name)

        mask_root = model_results_root / "masks"
        mask_root.mkdir(exist_ok=True, parents=True)

        for mask_id, mask in enumerate(masks):
            mask = mask > 0.5
            mask_path = mask_root / f"mask_{image_identifier}_{mask_id}.png"
            Image.fromarray(mask).save(mask_path)

        visualization_path = model_results_root / f"visualization_{image_identifier}.png"
        visualization = visualize_annotation(image, masks, boxes)
        visualization.save(visualization_path)

        shutil.move(image_path, model_results_root / image_path.name)
        shutil.move(csv_path, model_results_root / csv_path.name)

    return None, "/apps/results"
