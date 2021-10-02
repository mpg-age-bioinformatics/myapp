from myapp import app, db
import dash
from dash.dependencies import Input, Output, State
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from myapp.models import User
from myapp.email import send_validate_change_email
from datetime import datetime
import time
from ._utils import META_TAGS, check_email, password_check, navbar_A, protect_dashviews, make_navbar_logged
from flask_login import current_user, logout_user
from flask import session
import pyqrcode
import io
import base64


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
                            dbc.Input(type=input_type, id=id_, value=value, placeholder=placeholder, style={"width":"330px","margin-left":"2px"}),
                        ),
                    ],
                    row=True,
                ),
                ],
                # inline=True,
                # style={"margin-top":"2px"},
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
        style={"width":"330px","margin-left":"2px"}
    )

    notify=dbc.Form( [ 
        dbc.FormGroup(
            [ 
                dbc.Label("", html_for="notify", style={"min-width":"150px","margin-left":"20px"}), # xs=2,sm=3,md=3,lg=2,xl=2,
                dbc.Col(
                    notify
                ),
            ],
            row=True,
        ),
        ],
        # style={"margin-top":"10px"},
        )

    submit_btn=dbc.Form( [ 
        dbc.FormGroup(
            [ 
                dbc.Label("", style={"min-width":"150px","margin-left":"20px"}), # xs=2,sm=3,md=3,lg=2,xl=2,
                dbc.Col(
                    [ 
                        dbc.Button(id='submit-button-state', n_clicks=0, children='Submit changes', style={"width":"330px","margin-left":"2px","margin-top":4, "margin-bottom":4}),
                    ]
                ),
            ],

            row=True,
        ),
        ],
        # style={"margin-top":"10px"},
        )


    imgByteArr = io.BytesIO()
    big_code = pyqrcode.create(current_user.get_totp_uri())
    big_code.svg(imgByteArr, scale=6 )
    imgByteArr = imgByteArr.getvalue()
    encoded=base64.b64encode(imgByteArr)
    img=html.Img(src='data:image/svg+xml;base64,{}'.format(encoded.decode()), height="200px")

    modal_body=dbc.ModalBody(
                        [ 
                            dbc.Row(dbc.Col(img,style={"textAlign":"center"})),
                            dbc.Row(
                                [
                                    dbc.Col(
                                        dbc.Input(type="text", id="otp-input", placeholder="type code"),
                                        width={"size":5,"offset":2},
                                        style={"margin-right":"2px"}
                                    ),
                                    dbc.Col(
                                        dbc.Button( "Enable", id="otp-enable", className="ml-auto", n_clicks=0 ) ,
                                        width=1,
                                        style={"textAlign":"left"}
                                        # style={"margin":"2px"}
                                    )
                                ],
                                # justify="left",
                                no_gutters=True,
                                align="center",
                                style={"margin-bottom":"15px"}
                            ),
                            html.Div(id="backup-codes-output"),
                            dbc.Row("You can user Google Authenticator on your phone to scan the QR code and enable \
                            Two-Factor Authentication.",style={"textAlign":"justify","margin":"2px"})
                        ]
                    )




    modal = html.Div(
        [
            # dbc.Button("Open", id="open-centered"),
            dbc.Modal(
                [
                    dbc.ModalHeader("2FA QR Code"),
                    modal_body,
                    dbc.ModalFooter(
                        dbc.Row(
                            [
                                dbc.Button(
                                    "Backup codes",
                                    id="backup-codes-btn",
                                    className="ml-auto",
                                    n_clicks=0,
                                    disabled=True,
                                    style={"margin":"2px"}
                                ),
                                dbc.Button(
                                    "Close",
                                    id="close-centered",
                                    className="ml-auto",
                                    n_clicks=0,
                                    style={"margin":"2px"}
                                )
                            ],
                            no_gutters=False,
                            justify="end",
                        ),
                    ),
                ],
                id="modal-centered",
                centered=True,
                is_open=False,
            ),
        ]
    )

    show_qrcode=dbc.Button("Show QR code", id="open-centered")

    user_settings=dbc.Row(
        dbc.Col(
            dbc.Card(
                [
                    html.H4("General settings",style={"margin-top":"5%","margin-bottom":"30px"}),
                    firstname_input,
                    html.Div(id="firstname-feedback"),
                    lastname_input,
                    html.Div(id="lastname-feedback"),
                    username_input,
                    html.Div(id="username-feedback"),
                    email_input,
                    html.Div(id="email-feedback"),
                    email_input_2,
                    html.Div(id="email2-feedback"),
                    password_input,
                    password_input_2,
                    html.Div(id="pass-power"),
                    html.Div(id="pass-feedback"),
                    html.Div(id="pass2-feedback"),
                    notify,
                    html.Div(id="checkbox-feedback"),
                    submit_btn,
                    html.Div(id="submission-feedback"),
                    html.H4("Two-Factor Authentication",style={"margin-top":"5%","margin-bottom":"30px"}),
                    html.P("Two-Factor Authentication (2FA) works by adding an additional layer. of \
                        security to your online accounts. It requires an additional login credential \
                            – beyond just the username and password – to gain account access, and \
                                getting that second credential requires access to something that ", style={"max-width":"500px"}),
                    show_qrcode,
                    modal,
                ],
                body=True,
                className="border-0",
                style={"max-width":"550px"}
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

def make_response(text,color,id="some-id",is_open=True, duration=None):
    r=dbc.Form( [ 
        dbc.FormGroup(
            [ 
                dbc.Label("", style={"min-width":"150px","margin-left":"20px"}), # xs=2,sm=3,md=3,lg=2,xl=2,
                dbc.Col(
                    [ 
                        dbc.Alert( text ,id=id, color=color,is_open=is_open, duration=duration, style={"width":"330px","margin-left":"2px"}),
                    ]
                ),
            ],

            row=True,
        ),
        ],
        # style={"margin-top":"10px"},
        )
    return r

@dashapp.callback(
    Output("navbar-collapse", "is_open"),
    [Input("navbar-toggler", "n_clicks")],
    [State("navbar-collapse", "is_open")],
    )
def toggle_navbar_collapse(n, is_open):
    if n:
        return not is_open
    return is_open

@dashapp.callback(
    Output("backup-codes-output", "children"),
    [ Input("backup-codes-btn", "n_clicks") ],
    prevent_initial_call=True)
def generate_backup_codes(n1):
    if n1:
        return html.Div("backup-codes")

@dashapp.callback(
    Output("backup-codes-btn", "disabled"),
    [ Input("otp-enable", "n_clicks") ],
    prevent_initial_call=True)
def enable_2fa(n1):
    print("!!!!!!", n1)
    if n1:
        return False


@dashapp.callback(
    Output("modal-centered", "is_open"),
    [Input("open-centered", "n_clicks"), Input("close-centered", "n_clicks")],
    [State("modal-centered", "is_open")],
)
def toggle_modal(n1, n2, is_open):
    if n1 or n2:
        return not is_open
    return is_open

@dashapp.callback(
    Output('pass-power', 'children'),
    Input('input-password', 'value'),
    prevent_initial_call=True)
def check_pass_power(passA):
    passdic=password_check(passA)
    if passdic["passtype"] == "weak":
        return make_response( "please use a strong password" ,color="danger")
    elif passdic["passtype"] == "medium":
        return make_response( "please use a strong password" ,color="warning")
    elif passdic["passtype"] == "strong":
        return make_response( "strong password" ,id="alert-auto", color="success", is_open=True, duration=1500)

@dashapp.callback(
    Output("alert-auto", "is_open"),
    [Input("alert-toggle-auto", "n_clicks")],
    [State("alert-auto", "is_open")],
)
def toggle_alert(n, is_open):
    if n:
        return not is_open
    return is_open

@dashapp.callback(
    Output('firstname-feedback', 'children'),
    Output('lastname-feedback', 'children'),
    Output('username-feedback', 'children'),
    Output('email-feedback', 'children'),
    Output('email2-feedback', 'children'),
    Output('pass-feedback', 'children'),
    Output('pass2-feedback', 'children'),
    Output('checkbox-feedback', 'children'),
    Output('submission-feedback', 'children'),
    Input('submit-button-state', 'n_clicks'),
    State('first_name', 'value'),
    State('last_name', 'value'),
    State('username', 'value'),
    State('input-email', 'value'),
    State('input-email-2', 'value'),
    State('input-password', 'value'),
    State('input-password-2', 'value'),
    State('notify', 'value'),
    prevent_initial_call=True
    )
def submit_changes(n_clicks,first_name, last_name, username, emailA, emailB, passA, passB, notify):
    first_name_=None
    last_name_=None
    username_=None
    emailA_=None
    emailB_=None
    passA_=None
    passB_=None
    notify_=None
    submission_=None

    if ( first_name ) and (first_name != current_user.firstname):
        user=User.query.filter_by(id=current_user.id).first()
        user.firstname=first_name
        db.session.add(user)
        db.session.commit()
        first_name_=make_response("First name changed." ,color="success") #dbc.Alert( "First name changed." ,color="success") # style={"font-size":"10px"}
    if ( last_name ) and (last_name != current_user.lastname):
        user=User.query.filter_by(id=current_user.id).first()
        user.lastname=last_name
        db.session.add(user)
        db.session.commit()
        last_name_=make_response( "Last name changed." ,color="success")
    if  ( username ) and (username != current_user.username) :
        user=User.query.filter_by(username=username).first()
        if user:
            if user.username == username:
                username_=make_response( "Username alread exists. Please pick a different username." ,color="danger")
            else:
                user=None
        if not user:
            user=User.query.filter_by(id=current_user.id).first()
            user.username=username
            db.session.add(user)
            db.session.commit()
            username_=make_response( "Username changed." ,color="success")
    # if not email:
    #     email_=dbc.Alert( "*required" ,color="warning")
    if (emailA) and (emailA != current_user.email):
        if emailA != emailB :
            emailB_=make_response( "Emails do not match." ,color="warning")
        elif not check_email(emailA) :
            emailA_=make_response( "Invalid email address." ,color="warning")
        else:
            user = User.query.filter_by(email=emailA).first()
            if user:
                if user.email == emailA:
                    emailA_=make_response( "Email already in use. Please pick a different email address." ,color="danger")
                else:
                    user=None
            if not user:
                user=User.query.filter_by(id=current_user.id).first()
                user.email=emailA
                user.confirmed_on=None
                db.session.add(user)
                db.session.commit()

                send_validate_change_email(user)

                session.clear()
                logout_user()
                time.sleep(2)

                emailA_=dcc.Location(pathname="/logout/email/", id='login')
                return first_name_,last_name_,username_, emailA_, emailB_, passA_,passB_,notify_,submission_

    if ( passA ) and ( not current_user.check_password(passA) ):
        passdic=password_check(passA)
        if passdic["passtype"] != "strong" :
            passA_=make_response( "Please use a strong password." ,color="warning")
        elif not passB:
            passB_=make_response( "*required" ,color="warning")
        elif passA != passB:
            passB_=make_response( "Passwords do not match" ,color="warning")
        else:
            user=User.query.filter_by(id=current_user.id).first()
            user.set_password(passA)
            user.password_set=datetime.utcnow()
            db.session.add(user)
            db.session.commit()
            passA_=make_response( "Password changed." ,color="success")
 
    if  ( notify  )and ( not current_user.notifyme ):
        user=User.query.filter_by(id=current_user.id).first()
        user.notifyme=True
        notify_=make_response( "Notifications enabled." ,color="success")

    elif ( not notify ) and ( current_user.notifyme ):
        user=User.query.filter_by(id=current_user.id).first()
        user.notifyme=False
        notify_=make_response( "Notifications disabled." ,color="warning")

    return first_name_,last_name_,username_, emailA_, emailB_, passA_,passB_,notify_,submission_
