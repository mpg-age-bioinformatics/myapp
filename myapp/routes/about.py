from myapp import app, db
import dash
from dash.dependencies import Input, Output, State
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from myapp.models import User
from myapp.email import send_validate_email
from datetime import datetime
from ._utils import META_TAGS, check_email, password_check, navbar_A, protect_dashviews
from flask_login import current_user
from ._about import _about

dashapp = dash.Dash("about",url_base_pathname='/about/', meta_tags=META_TAGS, server=app, external_stylesheets=[dbc.themes.BOOTSTRAP], title=app.config["APP_TITLE"], assets_folder=app.config["APP_ASSETS"])# , assets_folder="/flaski/flaski/static/dash/")

# protect_dashviews(dashapp)


about=dcc.Markdown(_about)

links_style={"color":"#35443f", "margin-left":"12px", "margin-right":"12px", "font-weight": "bold","text-decoration": "none"}
privacy_impressum=html.Div([
    dbc.Row( 
        html.Footer( 
            [ 
                html.A("Impressum", style=links_style, href="/impressum/"),
                html.A("Privacy", style=links_style, href="/privacy/"),
            ] , 
            style={"margin-top": 25, "margin-bottom": 5,},
        ),
        style={"justify-content":"center"}
    )
])

dashapp.layout=dbc.Row(
    [ 
        dbc.Col( 
            [ 
                html.H1("About", style={"textAlign":"center", "margin-bottom":"30px"}), 
                about, 
                privacy_impressum 
            ], 
            align="top", 
            style={"textAlign":"justify",'margin-left':"15px", 'margin-right':"15px","margin-top":"100px",'margin-bottom':"50px"},
            sm=10, md=10, lg=8, xl=5
        ), 
        navbar_A 
    ] ,
    justify="center",
)