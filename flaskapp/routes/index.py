import re
from flaskapp import app
from flask_login import current_user
from flask_caching import Cache
import dash
from dash.dependencies import Input, Output, State
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
import uuid
from werkzeug.utils import secure_filename
import json
from flask import session

import pandas as pd
import os

META_TAGS=[{'name': 'viewport', 'content': 'width=device-width, initial-scale=1.0, maximum-scale=1.2, minimum-scale=0.5,'} ]

dashapp = dash.Dash("index",url_base_pathname='/', meta_tags=META_TAGS, server=app, external_stylesheets=[dbc.themes.BOOTSTRAP], title=app.config["APP_TITLE"])# , assets_folder="/flaski/flaski/static/dash/")
# protect_dashviews(dashapp)

# cache = Cache(dashapp.server, config={
#     'CACHE_TYPE': 'redis',
#     'CACHE_REDIS_URL': 'redis://:%s@%s' %( os.environ.get('REDIS_PASSWORD'), os.environ.get('REDIS_ADDRESS') )  #'redis://localhost:6379'),
# })

dashapp.layout=dbc.Row( 
                    dbc.Col( html.H1(app.config["APP_TITLE"], style={"textAlign":"center"}), align="center" ),
                    justify="center",
                    style={"min-height": "100vh"})

# @dashapp.callback(
#         Output("navbar-collapse", "is_open"),
#         [Input("navbar-toggler", "n_clicks")],
#         [State("navbar-collapse", "is_open")])
# def toggle_navbar_collapse(n, is_open):
#     if n:
#         return not is_open
#     return is_open

