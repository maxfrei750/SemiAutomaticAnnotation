from dash import html

from . import error_message
from .paths import ANNOTATED_ROOT


def get_layout():
    annotated_csv_paths = list(ANNOTATED_ROOT.glob("*.csv"))

    if annotated_csv_paths:
        layout = html.Div(
            [
                html.Center(
                    [
                        html.H1("There are annotated images."),
                        html.Button("Evaluate!", id="evaluate", n_clicks=0),
                    ]
                )
            ],
            style={"height": "98vh"},
        )
    else:
        layout = error_message.get_layout("There are no csv-files in folder 'annotated'.")
    return layout
