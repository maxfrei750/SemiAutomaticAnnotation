import shutil
from pathlib import Path

import pandas as pd
import plotly.express as px
from dash import Input, Output, State, dcc, html

from app import app
from utilities import read_image

from . import error_message
from .paths import ANNOTATED_ROOT, INPUT_ROOT


def style_cursor(figure):
    # Style cursor
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


def style_annotations(figure):
    # Style annotation
    figure.update_layout(
        dragmode="drawrect",
        newshape={
            "fillcolor": None,
            "opacity": 0.4,
            "line": {"color": "red", "width": 3},
        },
    )


def get_layout():
    image_paths = list(INPUT_ROOT.glob("*.*"))

    if image_paths:
        image_path = image_paths[0]  # only use first image
        image = read_image(image_path)
        figure = px.imshow(image)
        style_annotations(figure)
        style_cursor(figure)
        graph_config = {
            "displaylogo": False,
            "displayModeBar": True,
            "scrollZoom": True,
            "modeBarButtons": [["eraseshape", "autoScale2d"]],
        }
        layout = html.Div(
            [
                dcc.Graph(
                    figure=figure,
                    config=graph_config,
                    id="figure-annotation",
                    style={"height": "95%"},  # TODO: Make filling flexible
                ),
                html.Center(
                    html.A(
                        html.Button(
                            "Save & next",
                            id="save-next",
                            n_clicks=0,
                        ),
                        href="/apps/annotation",
                    ),
                ),
                html.Div(id="dummy"),
                dcc.Store(id="image-path", data=str(image_path)),
            ],
            style={"height": "98vh"},
        )
    else:
        layout = error_message.get_layout(
            "No files in folder 'input'.", [dcc.Link("Evaluation", href="/apps/evaluation")]
        )

    return layout


@app.callback(
    Output("dummy", "children"),
    Input("save-next", "n_clicks"),
    State("figure-annotation", "relayoutData"),
    State("image-path", "data"),
    prevent_initial_call=True,
)
def save_annotations_and_move_input_image(_, relayout_data, input_image_path):

    shapes = relayout_data.get("shapes")

    if shapes is not None:
        wanted_keys = ["x0", "y0", "x1", "y1"]
        annotations = pd.DataFrame(
            [dict((k, shape[k]) for k in wanted_keys if k in shape) for shape in shapes]
        )

        input_image_path = Path(input_image_path)

        csv_path = ANNOTATED_ROOT / f"annotation_{input_image_path.stem}.csv"

        annotations.to_csv(csv_path, index=False)

        output_image_path = ANNOTATED_ROOT / f"image_{input_image_path.name}"
        shutil.move(input_image_path, output_image_path)


@app.callback(
    Output("save-next", "disabled"),
    Input("figure-annotation", "relayoutData"),
)
def enable_disable_button(relayout_data):
    return "shapes" not in relayout_data
