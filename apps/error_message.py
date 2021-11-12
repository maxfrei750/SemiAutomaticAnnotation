from typing import List, Optional

from dash import dcc, html

# TODO: Type annotations.
# TODO: Documentation.


def get_layout(message: str, links: Optional[List[dcc.Link]] = None):

    if links is None:
        links = []

    layout = html.Div(
        [
            html.Center(
                [
                    html.H1(message),
                ]
                + [html.H1(link) for link in links]
            )
        ],
        style={"height": "98vh"},
    )

    return layout
