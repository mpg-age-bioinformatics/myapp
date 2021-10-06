from myapp import app, db
import dash
from dash.dependencies import Input, Output, State
from dash import dcc, html
# import dash as html
import dash_bootstrap_components as dbc
from myapp.models import User
from myapp.email import send_validate_email
from datetime import datetime
from ._utils import META_TAGS, check_email, password_check, navbar_A, protect_dashviews, make_navbar_logged
from flask_login import current_user


dashapp = dash.Dash("home",url_base_pathname='/home/', meta_tags=META_TAGS, server=app, external_stylesheets=[dbc.themes.BOOTSTRAP], title=app.config["APP_TITLE"], assets_folder=app.config["APP_ASSETS"])# , assets_folder="/flaski/flaski/static/dash/")

protect_dashviews(dashapp)

dashapp.layout=html.Div( [ 
                dcc.Location(id='url', refresh=False),
                html.Div(id="protected-content"),
                ] 
            )

@dashapp.callback(
    Output('protected-content', 'children'),
    Input('url', 'pathname'))
def make_layout(pathname):
    protected_content=html.Div(
        [
            make_navbar_logged("Home",current_user),
            dbc.Container(
                dbc.Row( 
                    dbc.Col(
                        [
                            html.H1("Home is where the Dom is.")
                        ],
                        align="center",
                    ),
                align="center",
                justify="center",
                style={'textAlign':'center',"height":"87vh"}
                ),
            ),
            navbar_A
        ],
        style={"height":"100vh","verticalAlign":"center"}
    )
    return protected_content


@dashapp.callback(
    Output("navbar-collapse", "is_open"),
    [Input("navbar-toggler", "n_clicks")],
    [State("navbar-collapse", "is_open")],
    )
def toggle_navbar_collapse(n, is_open):
    if n:
        return not is_open
    return is_open