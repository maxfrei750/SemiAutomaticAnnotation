import os
from typing import Tuple

import dash_bootstrap_components as dbc
from dash import dcc
from dash.dependencies import Input, Output
from dash.development.base_component import Component

from app import app
from apps import annotation, evaluation, menu, results

PORT_FRONTEND = int(os.environ["PORT_FRONTEND"])

app.layout = dbc.Container(
    [
        dbc.Row(dcc.Location(id="url-index", refresh=True)),
        dbc.Row(id="navigation", className="bg-secondary"),
        dbc.Row(
            id="page-content",
            style={"margin-bottom": "1vh"},
            className="flex-fill",
        ),
    ],
    fluid=True,
    className="vh-100 d-flex flex-column",
)


@app.callback(
    Output("page-content", "children"),
    Output("navigation", "children"),
    Output("url-index", "pathname"),
    Input("url-index", "pathname"),
)
def display_page(path_name: str) -> Tuple[Component, Component, str]:
    """Display an app, according to the specified path name.

    :param path_name: Path of the current url.
    :return: Layout of an app and the menu, according to the path name.
    """
    if path_name == "/apps/evaluation":
        page_layout = evaluation.get_layout()
    elif path_name == "/apps/results":
        page_layout = results.get_layout()
    else:
        path_name = "/apps/annotation"
        page_layout = annotation.get_layout()

    return page_layout, menu.get_layout(), path_name


if __name__ == "__main__":
    app.run_server(host="0.0.0.0", port=PORT_FRONTEND, debug=True, dev_tools_ui=False)
