from pathlib import Path

import dash_bootstrap_components as dbc
from dash.development.base_component import Component


def get_layout() -> Component:
    """Get layout of the menu.

    :return: Layout of the main menu.
    """

    path_names = ["/apps/annotation", "/apps/evaluation", "/apps/results"]

    nav_items = []

    for path_name in path_names:
        title = str(Path(path_name).name).capitalize()
        nav_items.append(
            dbc.NavItem(
                dbc.NavLink(title, active="partial", href=path_name, id=f"nav-{title.lower()}"),
            )
        )

    layout = dbc.Col(dbc.Nav(nav_items, horizontal=True, pills=True, justified=True))

    return layout
