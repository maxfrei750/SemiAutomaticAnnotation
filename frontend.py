import os
from pathlib import Path

import dash
import plotly.express as px
import plotly.io as pio
from dash import Input, Output, State, dcc, html

from prediction import read_image

pio.templates.default = "plotly_white"

PORT_FRONTEND = int(os.environ["PORT_FRONTEND"])

ROOT = Path("/home/tensorflow/")
INPUT_ROOT = ROOT / "input"
ANNOTATED_ROOT = ROOT / "annotated"
OUTPUT_ROOT = ROOT / "output"


def main():
    app = dash.Dash(__name__)

    input_image_paths = list(INPUT_ROOT.glob("*.*"))

    if input_image_paths:
        generate_annotation_layout(app, input_image_paths)
    else:
        app.layout = html.Div(
            [html.Center(html.H1("No images found in input folder."))],
            style={"height": "98vh"},
        )

    app.run_server(host="0.0.0.0", port=PORT_FRONTEND, debug=True, dev_tools_ui=False)


def generate_annotation_layout(app, input_image_paths):
    image_path = input_image_paths[0]  # only use first image
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
    app.layout = html.Div(
        [
            dcc.Graph(
                figure=figure,
                config=graph_config,
                id="figure-annotation",
                style={"height": "95%"},
            ),
            html.Center(
                html.Button("Save & next", id="save-next", n_clicks=0),
            ),
            html.Div(id="dummy"),
        ],
        style={"height": "98vh"},
    )

    @app.callback(
        Output("dummy", "children"),
        Input("save-next", "n_clicks"),
        State("figure-annotation", "relayoutData"),
        prevent_initial_call=True,
    )
    def store_annotations(n_clicks, relayout_data):
        raise NotImplementedError


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


if __name__ == "__main__":
    main()
