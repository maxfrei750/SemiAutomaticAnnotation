import os
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union

import dash
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px
from dash import Input, Output, State, dcc, html
from dash.development.base_component import Component
from PIL import Image
from plotly.graph_objects import Figure

import custom_components
from app import app
from utilities.custom_types import AnyPath
from utilities.data import read_image
from utilities.paths import ANNOTATED_ROOT, INPUT_ROOT, ROOT


def style_cursor(figure: Figure):
    """Style the cursor of a figure to allow an easy annotation.

    :param figure: Plotly figure.
    """
    crosshair_kwargs = {
        "showspikes": True,
        "spikemode": "across",
        "spikesnap": "cursor",
        "spikethickness": 0.5,
        "visible": False,
    }
    figure.update_xaxes(**crosshair_kwargs)
    figure.update_yaxes(**crosshair_kwargs)
    figure.update_traces(hoverinfo="none", hovertemplate="")


def style_annotations(figure: Figure):
    """Style the annotations of a figure.

    :param figure: Plotly figure.
    """
    figure.update_layout(
        dragmode="drawrect",
        newshape={
            "fillcolor": None,
            "opacity": 0.4,
            "line": {"color": "red", "width": 3},
        },
    )


def get_layout() -> Component:
    """Return the layout of the annotation app.

    :return: Layout of the annotation app.
    """
    num_images_initial = len(get_image_paths())
    current_image_path = get_current_image_path()

    layout = dbc.Col(
        [
            dbc.Row(
                get_graph_or_message(current_image_path),
                id="graph-or-message",
                className="flex-fill",
            ),
            dbc.Row(
                dbc.Col(
                    [
                        html.Div(
                            [
                                dbc.Button(
                                    "Save & next",
                                    id="save-next",
                                    n_clicks=0,
                                    disabled=True,
                                ),
                                dbc.Progress(
                                    id="progress-annotation",
                                    max=num_images_initial,
                                    style={"height": "1vh", "margin-top": "1vh"},
                                ),
                            ],
                            id="annotation-button-and-progress",
                            className="invisible" if current_image_path is None else "visible",
                        )
                    ],
                    className="text-center",
                    width={"size": 2, "offset": 5},
                ),
            ),
            dcc.Store(id="image-path", data=str(current_image_path)),
            dcc.Store(id="num-images-initial", data=num_images_initial),
            dcc.Store(id="store-annotation", data=[]),
            dcc.Location(id="url-annotation", refresh=True),
        ],
        className="d-flex flex-column",
    )

    return layout


def get_graph(image_path: AnyPath) -> dcc.Graph:
    """Get a graph suitable for annotation, with an image.

    :param image_path: Path of the image.
    :return: Plotly graph.
    """
    graph_config = {
        "displaylogo": False,
        "displayModeBar": True,
        "scrollZoom": True,
        "modeBarButtons": [["eraseshape", "autoScale2d"]],
    }

    return dcc.Graph(
        config=graph_config,
        id="graph-annotation",
        figure=get_figure(image_path),
    )


def get_graph_or_message(image_path: Optional[AnyPath]) -> Union[dcc.Graph, Component]:
    """Get either an annotation graph or an error message, if there is no image.

    :param image_path: Path to an image. Can be `None`.
    :return: Either a plotly graph with an image or a html component showing an error message.
    """
    if image_path is None:
        return custom_components.Message(
            dcc.Markdown(
                f"There are currently no files in the `./{INPUT_ROOT.relative_to(ROOT.parent)}` folder. Either put "
                f"some images that you want to annotate into the folder and **[refresh](/apps/annotation)** this page, "
                f"**[evaluate](/apps/evaluation)** previously annotated images, or inspect previously evaluated "
                f"**[results](/apps/results)**."
            )
        )
    else:
        return get_graph(image_path)


def get_figure(image_path: Optional[AnyPath]) -> Figure:
    """Get a figure showing an image, styled for annotation.

    :param image_path: Path to the image. Can be `None`.
    :return: Plotly figure that is styled for annotation, showing an image, or None, if there is no image.
    """
    if image_path is not None:
        image = read_image(image_path)
        figure = px.imshow(image)
        style_annotations(figure)
        style_cursor(figure)

        figure.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            modebar=dict(bgcolor="rgba(0,0,0,0)"),
            margin=dict(l=20, r=20, t=40, b=20),
        )

        return figure


def get_current_image_path() -> Optional[AnyPath]:
    """Get the first image in the `input` folder.

    :return: Path of the first image in the `input` folder.
    """
    image_paths = get_image_paths()
    if image_paths:
        return image_paths[0]


def get_image_paths() -> List[AnyPath]:
    """Get list of the paths of the images in the `input` folder.

    :return: List of paths of the images in the `input` folder.
    """
    image_paths = sorted(list(INPUT_ROOT.glob("?*.*")))
    return image_paths


@app.callback(
    Output("graph-or-message", "children"),
    Output("image-path", "data"),
    Output("annotation-button-and-progress", "className"),
    Output("url-annotation", "pathname"),
    Output("progress-annotation", "value"),
    Input("save-next", "n_clicks"),
    State("store-annotation", "data"),
    State("image-path", "data"),
    State("num-images-initial", "data"),
    prevent_initial_call=True,
)
def save_annotations_and_move_input_image(
    _, annotations: List[Dict], image_path: str, num_images_initial: int
) -> Tuple[Union[dcc.Graph, Component], str, str, str, int]:
    """Save annotations as csv-file. Move csv file and image file to the `annotated` folder.

    :param _: Mandatory input for the callback. Unused.
    :param annotations: List of dictionaries with keys ["x0", "y0", "x1", "y1"].
    :param image_path: Path of the input image.
    :param num_images_initial: Number of images that can be annotated.
    """

    annotations = pd.DataFrame(annotations)

    image_path = Path(image_path)

    image_id = image_path.stem

    if image_id.startswith("image_"):  # Catch if the image file name already has the suffix.
        image_id = image_id[6:]

    ANNOTATED_ROOT.mkdir(exist_ok=True, parents=True)

    csv_path = ANNOTATED_ROOT / f"annotation_{image_id}.csv"
    annotations.to_csv(csv_path, index=False)

    output_image_path = ANNOTATED_ROOT / f"image_{image_id}.png"
    Image.open(image_path).save(output_image_path)
    os.remove(image_path)

    image_path = get_current_image_path()

    if image_path is None:
        button_and_progress_class = "invisible"
        path_name = "/apps/evaluation"
        content = None
    else:
        button_and_progress_class = "visible"
        path_name = "/apps/annotation"
        content = get_graph(image_path)

    num_images_left = len(get_image_paths())
    sample_index = num_images_initial - num_images_left

    return content, str(image_path), button_and_progress_class, path_name, sample_index


@app.callback(
    Output("save-next", "disabled"),
    Input("graph-annotation", "relayoutData"),
    Input("save-next", "disabled"),
)
def disable_button(relayout_data: Optional[Dict], is_button_disabled: bool) -> bool:
    """Check if the `Save & next` button should be activated or not. )

    :param relayout_data: Graph annotation data.
    :param is_button_disabled: Current state of the button.
    :return: True, if the button should be activated, false, if not.
    """

    if relayout_data is None:  # New image has been loaded.
        return True

    if "shapes" in relayout_data:  # There might be annotations.
        if relayout_data["shapes"]:  # There are annotations.
            return False
        else:  # There were annotations but they have been deleted by the user.
            return True
    else:  # There are no annotations.
        return is_button_disabled


@app.callback(
    Output("store-annotation", "data"),
    Input("graph-annotation", "relayoutData"),
    State("store-annotation", "data"),
)
def update_annotation_store(
    relayout_data: Optional[Dict], current_store_state: List[Dict]
) -> List[Dict]:
    """Update the annotation data store `store-annotation`, if necessary. This workaround is necessary, to always have
    access to a full set of annotations, independently from the `relayoutData` property of the `graph-annotation`
    element, which can have all sorts of values, depending on the user interaction.

    :param relayout_data: Graph annotation data.
    :param current_store_state: Current state of the data store.
    :return: Updated state of the data store.
    """

    if "shapes" in relayout_data:  # There exist annotations or all annotations have been deleted.
        shapes = relayout_data["shapes"]
        wanted_keys = ["x0", "y0", "x1", "y1"]
        annotations = [dict((k, shape[k]) for k in wanted_keys if k in shape) for shape in shapes]

        return annotations
    elif any(
        ["shapes" in key for key in relayout_data]
    ):  # An annotation is currently being updated.

        # Get the index of the annotation that is being manipulated.
        updated_index = None  # Prevent that `updated_index` is ever undefined.
        for key in relayout_data:
            if "shapes" in key:
                # Keys have the format `shapes[0].x0`.
                updated_index = int(key[7:][:-4])

        x0 = [relayout_data[key] for key in relayout_data if "x0" in key][0]
        x1 = [relayout_data[key] for key in relayout_data if "x1" in key][0]
        y0 = [relayout_data[key] for key in relayout_data if "y0" in key][0]
        y1 = [relayout_data[key] for key in relayout_data if "y1" in key][0]

        annotations = current_store_state.copy()
        annotations[updated_index] = dict(x0=x0, x1=x1, y0=y0, y1=y1)

        return annotations
    else:  # Edge cases (e.g. freshly loaded page or zooming).
        return dash.no_update
