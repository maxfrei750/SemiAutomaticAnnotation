from typing import List, Optional

from dash import dcc, html
from dash.development.base_component import Component


def get_layout(message: str, links: Optional[List[dcc.Link]] = None) -> Component:
    """Get the layout of an error message, with optional links for the user.

    :param message: Message to be displayed.
    :param links: Optional links for the user to click.
    :return: Layout of the message.
    """
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
