from flaskapp import app, db
import dash
from dash.dependencies import Input, Output, State
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from flaskapp.models import User
from flaskapp.email import send_validate_email
from datetime import datetime
from ._utils import META_TAGS, check_email, password_check, navbar_A, protect_dashviews, make_navbar_logged
from flask_login import current_user


dashapp = dash.Dash("settings",url_base_pathname='/settings/', meta_tags=META_TAGS, server=app, external_stylesheets=[dbc.themes.BOOTSTRAP], title=app.config["APP_TITLE"], assets_folder=app.config["APP_ASSETS"])# , assets_folder="/flaski/flaski/static/dash/")

protect_dashviews(dashapp)


dashapp.layout=html.Div( [ 
    dcc.Location(id='url', refresh=False),
    html.Div(id="protected-content"),
     ] )

@dashapp.callback(
    Output('protected-content', 'children'),
    Input('url', 'pathname'))
def make_layout(pathname):
    topnavbar=make_navbar_logged("Settings",current_user)

    def make_text_form_row(label,value,placeholder,id_,input_type="text"):
        form_row=dbc.Form( [ 
                dbc.FormGroup(
                    [ 
                        dbc.Label(label, html_for=id_, style={"min-width":"150px","margin-left":"20px"}), # xs=2,sm=3,md=3,lg=2,xl=2,
                        dbc.Col(
                            dbc.Input(type=input_type, id=id_, value=value, placeholder=placeholder, style={"width":"300px","margin-left":"2px"}),
                        ),
                    ],
                    row=True,
                ),
                ],
                # inline=True,
                style={"margin-top":"10px"},
                )
        return form_row

    firstname_input=make_text_form_row("First name",current_user.firstname,"First name","first_name")
    lastname_input=make_text_form_row("Last name",current_user.lastname,"Last name","last_name")
    username_input=make_text_form_row("Username",current_user.username,"username","username")
    email_input=make_text_form_row("Email",current_user.email,"Enter email","input-email", "email")
    email_input_2=make_text_form_row("Repeat email",current_user.email,"Enter email again","input-email-2", "email")
    password_input=make_text_form_row("Password",None,"Enter password","input-password", "password")
    password_input_2=make_text_form_row("Repeat password",None,"Enter password again","input-password-2", "password")


    if current_user.notifyme:
        notify_value=["notify"]
    else:
        notify_value=[]

    notify=dcc.Checklist(
        options=[
            {'label': " Notify me on product news.", 'value': 'notify'},
        ],
        value=notify_value,
        id="notify",
        style={"width":"300px","margin-left":"2px"}
    )

    notify=dbc.Form( [ 
        dbc.FormGroup(
            [ 
                dbc.Label("", html_for="check_box", style={"min-width":"150px","margin-left":"20px"}), # xs=2,sm=3,md=3,lg=2,xl=2,
                dbc.Col(
                    notify
                ),
            ],
            row=True,
        ),
        ],
        style={"margin-top":"10px"},
        )

    submit_btn=dbc.Form( [ 
        dbc.FormGroup(
            [ 
                dbc.Label("", style={"min-width":"150px","margin-left":"20px"}), # xs=2,sm=3,md=3,lg=2,xl=2,
                dbc.Col(
                    [ 
                        html.Button(id='submit-button-state', n_clicks=0, children='Submit changes', style={"width":"300px","margin-left":"2px","margin-top":4, "margin-bottom":4}),
                    ]
                ),
            ],

            row=True,
        ),
        ],
        style={"margin-top":"10px"},
        )



    firstname_input.style={"margin-top":"5%"}



    user_settings=dbc.Row(
        dbc.Col(
            dbc.Card(
                [
                    firstname_input,
                    lastname_input,
                    username_input,
                    html.Div(id="username-feedback"),
                    email_input,
                    html.Div(id="email-feedback"),
                    email_input_2,
                    html.Div(id="email2-feedback"),
                    password_input,
                    html.Div(id="pass-power"),
                    html.Div(id="pass-feedback"),
                    password_input_2,
                    html.Div(id="pass2-feedback"),
                    notify,
                    html.Div(id="checkbox-feedback"),
                    submit_btn,
                    html.Div(id="submission-feedback"),
                ],
                body=True,
                className="border-0"
            ),
            sm=11, md=9, lg=7, xl=6, align="center",style={ "margin-left":2, "margin-right":2 }
        ),
        align="center",
        justify="center",
        style={"min-height": "450px", 'verticalAlign': 'center','margin-bottom':"50px"}
        )

    protected_content=html.Div([
        topnavbar,
        user_settings,
        navbar_A
    ]
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