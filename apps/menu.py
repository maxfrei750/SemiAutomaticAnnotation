from dash import dcc, html
from dash.development.base_component import Component


def get_layout() -> Component:
    """Get layout of the main menu.

    :return: Layout of the main menu.
    """
    layout = html.Center(
        html.Div(
            [
                html.Br(),
                html.Br(),
                html.H1(dcc.Link("Annotation", href="/apps/annotation")),
                html.H1(dcc.Link("Evaluation", href="/apps/evaluation")),
                html.H1(dcc.Link("Results", href="/apps/results")),
            ]
        )
    )

    return layout
