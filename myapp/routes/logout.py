from myapp import app, PAGE_PREFIX
from flask import session
from flask_login import logout_user
import dash
from dash.dependencies import Input, Output
from dash import dcc, html
import dash_bootstrap_components as dbc
from myapp.models import User
from ._utils import META_TAGS
import time

dashapp = dash.Dash("logout",url_base_pathname=f'{PAGE_PREFIX}/logout/', meta_tags=META_TAGS, server=app, external_stylesheets=[dbc.themes.BOOTSTRAP], title="Logout", assets_folder=app.config["APP_ASSETS"])# , assets_folder="/flaski/flaski/static/dash/")

dashapp.layout=html.Div(
    [ 
        dcc.Location(id='url', refresh=False),  
        dcc.Loading( 
            id="loading-output-1",
            type="default",
            children=html.Div(id="redirect-field"),
            style={"margin-top":"50%"} 
            )
    ]
)

@dashapp.callback( Output('redirect-field', 'children'),
                   Input('url', 'pathname'))
def do_logout(pathname):
    session.clear()
    logout_user()
    time.sleep(2)
    return dcc.Location(pathname=f"{PAGE_PREFIX}/login/logout/", id='login')