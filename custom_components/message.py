from typing import List

import dash_bootstrap_components as dbc
from dash import html
from dash.development.base_component import Component


class Message(dbc.Alert):
    def __init__(self, children: List[Component], color: str = "info"):
        children += [
            html.Br(),
            html.Br(),
            html.A("Back to menu...", href="/"),
        ]

        for child in children:
            if isinstance(child, html.A):
                child.className = "alert-link"

        super().__init__(children, color=color)
