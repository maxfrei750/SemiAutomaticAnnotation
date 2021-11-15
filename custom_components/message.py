from typing import List

import dash_bootstrap_components as dbc
from dash import html
from dash.development.base_component import Component


class Message(dbc.Col):
    def __init__(self, children: List[Component], color: str = "info"):
        for child in children:
            if isinstance(child, html.A):
                child.className = "alert-link"

        super().__init__(
            dbc.Alert(children, color=color),
            style={"margin-top": "2%"},
            width={"size": 6, "offset": 3},
        )
