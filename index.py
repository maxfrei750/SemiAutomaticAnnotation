import os

from dash import dcc, html
from dash.dependencies import Input, Output
from dash.development.base_component import Component

from app import app
from apps import annotation, evaluation, menu, results

PORT_FRONTEND = int(os.environ["PORT_FRONTEND"])


app.layout = html.Div([dcc.Location(id="url", refresh=False), html.Div(id="page-content")])


@app.callback(Output("page-content", "children"), Input("url", "pathname"))
def display_page(path_name: str) -> Component:
    """Display an app, according to the specified path name.

    :param path_name: Path of the url.
    :return: Layout of an app, according to the path name.
    """
    if path_name == "/apps/annotation":
        return annotation.get_layout()
    elif path_name == "/apps/evaluation":
        return evaluation.get_layout()
    elif path_name == "/apps/results":
        return results.get_layout()
    else:
        return menu.get_layout()


if __name__ == "__main__":
    app.run_server(host="0.0.0.0", port=PORT_FRONTEND, debug=True, dev_tools_ui=False)
