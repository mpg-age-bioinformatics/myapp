from myapp import app, db, PAGE_PREFIX
import dash
from dash.dependencies import Input, Output, State
from dash import dcc, html
import dash_bootstrap_components as dbc
from myapp.models import User
from myapp.email import send_validate_email
from datetime import datetime
from ._utils import META_TAGS, check_email, password_check, navbar_A
from flask_login import current_user
from ._privacy import _privacy

dashapp = dash.Dash("privacy",url_base_pathname=f'{PAGE_PREFIX}/privacy/', meta_tags=META_TAGS, server=app, external_stylesheets=[dbc.themes.BOOTSTRAP], title=app.config["APP_TITLE"], assets_folder=app.config["APP_ASSETS"])# , assets_folder="/{APP_TITLE}/{APP_TITLE}/static/dash/")

gdpr_text=dcc.Markdown(_privacy)

dashapp.layout=dbc.Row(
    [ 
        dbc.Col(
            [ 
                html.H1("DATA AND PRIVACY", style={"textAlign":"center", "margin-bottom":"30px"}),
                gdpr_text 
            ],  # 
            align="top", 
            style={"textAlign":"justify",'margin-left':"15px", 'margin-right':"15px","margin-top":"100px", 'margin-bottom':"50px"},
            md=9, lg=7, xl=5), 
            navbar_A 
    ] ,
    justify="center"
)