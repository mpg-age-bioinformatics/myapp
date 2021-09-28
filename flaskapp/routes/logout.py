from flaskapp import app
from flask import session
from flask_login import logout_user
import dash
from dash.dependencies import Input, Output
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from flaskapp.models import User
from ._utils import META_TAGS
import time

dashapp = dash.Dash("logout",url_base_pathname='/logout/', meta_tags=META_TAGS, server=app, external_stylesheets=[dbc.themes.BOOTSTRAP], title=app.config["APP_TITLE"], assets_folder=app.config["APP_ASSETS"])# , assets_folder="/flaski/flaski/static/dash/")

dashapp.layout=html.Div([ dcc.Location(id='url', refresh=False),  
                          dcc.Loading( id="loading-output-1",
                                       type="default",
                                       children=html.Div(id="redirect-field"),
                                       style={"margin-top":"50%"} )])

@dashapp.callback( Output('redirect-field', 'children'),
                   Input('url', 'pathname'))
def do_logout(pathname):
    session.clear()
    logout_user()
    time.sleep(2)
    return dcc.Location(pathname="/login/logout/", id='login')