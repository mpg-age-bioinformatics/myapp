from flaskapp import app, db
import dash
from dash.dependencies import Input, Output, State
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from flaskapp.models import User
from flaskapp.email import send_contact
from datetime import datetime
from ._utils import META_TAGS ,check_email, navbar_A, protect_dashviews, make_options
from flask_login import current_user

dashapp = dash.Dash("admin",url_base_pathname='/admin/', meta_tags=META_TAGS, server=app, external_stylesheets=[dbc.themes.BOOTSTRAP], title=app.config["APP_TITLE"], assets_folder=app.config["APP_ASSETS"])

protect_dashviews(dashapp)

dashapp.layout=html.Div( [ dcc.Location(id='url', refresh=False), html.Div(id="protected-content") ] )

@dashapp.callback(
    Output('protected-content', 'children'),
    Input('url', 'pathname'))
def make_layout(pathname):
    # if not current_user.administrator :
    #     return dcc.Location(pathname="/index/", id='index')

    emails= [ u.email for u in User.query.all() ]
    emails.sort()
    emails=make_options(emails)

    email_input = dbc.FormGroup(
        [
            dcc.Dropdown( options=emails, id='opt-emails', multi=False),
        ]
    )

    activate_button=html.Button(id='activate-button-state', n_clicks=0, children='Activate', style={"width":"auto","margin-top":4, "margin-bottom":4})
    deactivate_button=html.Button(id='deactivate-button-state', n_clicks=0, children='Deactivate', style={"width":"auto","margin-top":4, "margin-bottom":4})


    


    protected_content=dbc.Row( [
        dbc.Col( [ dbc.Form([  html.Div(id="submission-feedback"),
                                email_input,
                                activate_button,
                                deactivate_button,
                                html.Div(id="activate-feedback"),
                                html.Div(id="deactivate-feedback")
                            ])
                ],
                md=8, lg=6, xl=4, align="center",style={ "margin-left":2, "margin-right":2 ,'margin-bottom':"50px"}),
        navbar_A
    ],
    align="center",
    justify="center",
    style={"min-height": "95vh", 'verticalAlign': 'center'})

    return protected_content

### need to finish this bit
# @dashapp.callback(
#     Output('submission-feedback', 'children'),
#     Input('url', 'pathname'))
# def check_sent(pathname):
#     if pathname == "/admin/activate/":
#         return dbc.Alert( "User has" ,color="success")

# @dashapp.callback(
#     Output('activate-feedback', 'children'),
#     Input('activate-button-state', 'n_clicks'),
#     State('input-email', 'value'),
#     prevent_initial_call=True)
# def activate_email(n_clicks, email):
    

#     return dbc.Alert( "User is now active." ,color="success")

    