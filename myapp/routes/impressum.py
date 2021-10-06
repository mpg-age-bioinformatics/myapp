from myapp import app, db
import dash
from dash.dependencies import Input, Output, State
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from myapp.models import User
from myapp.email import send_validate_email
from datetime import datetime
from ._utils import META_TAGS, check_email, password_check, navbar_A
from flask_login import current_user
from ._impressum import _impressum

dashapp = dash.Dash("impressum",url_base_pathname='/impressum/', meta_tags=META_TAGS, server=app, external_stylesheets=[dbc.themes.BOOTSTRAP], title=app.config["APP_TITLE"], assets_folder=app.config["APP_ASSETS"])# , assets_folder="/{APP_TITLE}/{APP_TITLE}/static/dash/")

gdpr_text=dcc.Markdown(_impressum)

dashapp.layout=dbc.Row(
    [ 
        dbc.Col( 
            [ 
                html.H1("IMPRESSUM", style={"textAlign":"center", "margin-bottom":"30px"}), 
                gdpr_text 
            ],  # 
            align="top", 
            style={"textAlign":"justify",'margin-left':"15px", 'margin-right':"15px","margin-top":"100px", 'margin-bottom':"50px"},
            md=9, lg=7, xl=5
        ), 
        navbar_A 
    ],
    justify="center"
)