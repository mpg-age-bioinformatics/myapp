from flaskapp import app, db
import dash
from dash.dependencies import Input, Output, State
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from flaskapp.models import User
from flaskapp.email import send_validate_email
from datetime import datetime
from ._utils import META_TAGS, check_email, password_check, navbar_A
from flask_login import current_user

dashapp = dash.Dash("about",url_base_pathname='/about/', meta_tags=META_TAGS, server=app, external_stylesheets=[dbc.themes.BOOTSTRAP], title=app.config["APP_TITLE"], assets_folder=app.config["APP_ASSETS"])# , assets_folder="/flaski/flaski/static/dash/")

about=dcc.Markdown('''

flaskapp is a backbone for flask-dash mixed apps with user level authentication and an administrator dashboard.

''')

dashapp.layout=dbc.Row(
                    [ dbc.Col( 
                        [ html.H1("About", style={"textAlign":"center", "margin-bottom":"30px"}), about ],  # 
                        align="top", 
                        style={"textAlign":"justify",'margin-left':"15px", 'margin-right':"15px","margin-top":"100px"},
                        md=8, lg=6, xl=4), 
                    navbar_A ] ,
                    justify="center")