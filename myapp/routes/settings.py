from myapp import app, db, PAGE_PREFIX
import dash
from dash.dependencies import Input, Output, State
from dash import dcc, html
import dash_bootstrap_components as dbc
from myapp.models import User
from myapp.email import send_validate_change_email, send_email
from datetime import datetime
import time
from ._utils import META_TAGS, check_email, password_check, navbar_A, protect_dashviews, make_navbar_logged
from flask_login import current_user, logout_user
from flask import session, render_template
import pyqrcode
import io
import base64
import os
import random


dashapp = dash.Dash("settings",url_base_pathname=f'{PAGE_PREFIX}/settings/', meta_tags=META_TAGS, server=app, external_stylesheets=[dbc.themes.BOOTSTRAP], title="Settings", assets_folder=app.config["APP_ASSETS"])# , assets_folder="/flaski/flaski/static/dash/")

protect_dashviews(dashapp)

dashapp.layout=html.Div( 
    [ 
        dcc.Location(id='url', refresh=False),
        html.Div(id="app-redirect"),
        html.Div(id="protected-content"),
    ] 
)

@dashapp.callback(
    Output('protected-content', 'children'),
    Input('url', 'pathname'))
def make_layout(pathname):
    topnavbar=make_navbar_logged("Settings",current_user)

    def make_text_form_row(label,value,placeholder,id_,input_type="text"):
        form_row=dbc.Row(
            [ 
                dbc.Label(label, html_for=id_, width=4), # xs=2,sm=3,md=3,lg=2,xl=2, style={"min-width":"150px","margin-left":"20px"}
                dbc.Col(
                    dbc.Input(type=input_type, id=id_, value=value, placeholder=placeholder, ), #style={"width":"330px","margin-left":"2px"}
                    width=8
                ),
            ],
            # row=True,
            className="mb-3",
        )
        return form_row

    firstname_input=make_text_form_row("First name",current_user.firstname,"First name","first_name")
    lastname_input=make_text_form_row("Last name",current_user.lastname,"Last name","last_name")
    username_input=make_text_form_row("Username",current_user.username,"username","username")
    email_input=make_text_form_row("Email",current_user.email,"Enter email","input-email", "email")
    email_input_2=make_text_form_row("Repeat email",current_user.email,"Enter email again","input-email-2", "email")
    current_password_input=make_text_form_row("Current password",None,"Enter password","current-password", "password")
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

    notify=dbc.Row(
        [ 
            dbc.Label("", html_for="notify", style={"min-width":"150px","margin-left":"20px"}), # xs=2,sm=3,md=3,lg=2,xl=2,
            dbc.Col( notify ),
        ],
    )

    if current_user.otp_enabled:
        otp_changes=dbc.Input(type="text", id="changes-otp", placeholder="2FA token", style={"width":"100%","margin-top":"6px"})                    
    else:
        otp_changes=dbc.Label("", id="changes-otp",style={"width":"100%"})

    submit_btn=dbc.Row(
        [ 
            dbc.Label(dbc.Button(id='submit-button-state', n_clicks=0, children='Submit', color="secondary",style={"width":"100%"}), html_for="changes-otp", width=4), # xs=2,sm=3,md=3,lg=2,xl=2, style={"min-width":"150px","margin-left":"20px"}
            dbc.Col(
                otp_changes,
                width=8
            ),
        ],
        className="mb-3",
    )

    if not current_user.otp_enabled:
        btn_text="QR code"
    else:
        btn_text="Disable"

    imgByteArr = io.BytesIO()
    big_code = pyqrcode.create(current_user.get_totp_uri())
    big_code.svg(imgByteArr, scale=6 )
    imgByteArr = imgByteArr.getvalue()
    encoded=base64.b64encode(imgByteArr)
    img=dbc.Row(dbc.Col(html.Img(src='data:image/svg+xml;base64,{}'.format(encoded.decode()), height="200px"),style={"textAlign":"center"}))
    otp_field=html.Div(
        [
            dbc.Row(
                [
                    dbc.Col(
                        dbc.Input(type="text", id="otp-input", placeholder="type code"),
                        # style={"margin-right":"0px"},
                        width=4,
                    ),
                ],
                className="g-0",
                align="center",
                justify="center",
                style={"margin-bottom":"15px"}
            ),
            html.Div(id="enable-feedback")
        ]
    )
    body_text=dbc.Row("You can use Google Authenticator on your phone to scan the QR code and enable \
    Two-Factor Authentication.",style={"textAlign":"justify","margin":"2px"})

    modal_body=dbc.ModalBody(
            [ 
                img,
                otp_field,
                html.Div(id="backup-codes-output"),
                body_text
            ]
        )

    modal = html.Div(
        [
            dbc.Modal(
                [
                    dbc.ModalHeader("2FA QR Code"),
                    modal_body,
                    dbc.ModalFooter(
                        html.Div(
                            [
                                dbc.Button(
                                    "Backup codes",
                                    id="backup-codes-btn",
                                    color="secondary",
                                    className="me-1",
                                    n_clicks=0,
                                    disabled=True,
                                ),
                                dbc.Button(
                                    children="Enable",
                                    id="enable-disable",
                                    color="secondary",
                                    className="me-1",
                                    n_clicks=0,
                                    disabled=True,
                                ),
                                dbc.Button(
                                    "Close",
                                    id="close-centered",
                                    color="secondary",
                                    className="me-1",
                                    n_clicks=0,
                                    href=f'{app.config["PAGE_PREFIX"]}/settings',
                                    external_link=True
                                )
                            ],
                        ),
                    ),
                ],
                id="modal-centered",
                centered=True,
                is_open=False,
            ),
        ]
    )    

    show_qrcode=dbc.Row(
        [ 
            dbc.Label(dbc.Button(id="open-centered", n_clicks=0, children=btn_text, color="secondary", style={"width":"100%"}), width=4), # xs=2,sm=3,md=3,lg=2,xl=2, style={"min-width":"150px","margin-left":"20px"}
            dbc.Col(
                dbc.Label("",style={"width":"100%"}),
                width=8
            ),
        ],
        className="mb-3",
    )

    if current_user.otp_enabled :
        otp_status="Enabled"
    else:
        otp_status="Disabled"


    user_settings=dbc.Row(
        dbc.Col(
            dbc.Card(
                [
                    html.H4("General settings",style={"margin-top":"5%","margin-bottom":"30px"}),
                    dbc.Form(
                        [
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
                            current_password_input,
                            html.Div(id="current-pass-feedback"),
                            password_input,
                            password_input_2,
                            html.Div(id="pass-power"),
                            html.Div(id="pass-feedback"),
                            html.Div(id="pass2-feedback"),
                            notify,
                            html.Div(id="checkbox-feedback"),
                            submit_btn,
                            html.Div(id="submission-feedback"),
                        ]
                    ),

                    html.H4("Two-Factor Authentication",style={"margin-top":"5%","margin-bottom":"30px"}),
                    html.P("Two-Factor Authentication (2FA) works by adding an additional layer. of \
                        security to your online accounts. It requires an additional login credential \
                            – beyond just the username and password – to gain account access, and \
                                getting that second credential requires access to something that's yours, eg. your phone.", style={"max-width":"500px"}),
                    html.P(f"Status: {otp_status}", style={"max-width":"500px"}),      
                    show_qrcode,
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

    protected_content=html.Div(
        [
            topnavbar,
            user_settings,
            modal,
            navbar_A
        ]
    )

    return protected_content

def make_response(text,color,id="some-id",is_open=True, duration=None):
    r=dbc.Form( 
        [ 
            html.Div(
                [ 
                    dbc.Label("", style={"min-width":"150px","margin-left":"20px"}), # xs=2,sm=3,md=3,lg=2,xl=2,
                    dbc.Col(
                        [ 
                            dbc.Alert( text ,id=id, color=color,is_open=is_open, duration=duration, style={"width":"330px","margin-left":"2px"}),
                        ]
                    ),
                ],
                # row=True,
            ),
        ],
    )
    return r

@dashapp.callback(
    Output("enable-disable", "disabled"),
    Input("otp-input", "value"),
    prevent_initial_call=True)
def enable_enable(n1):
    if n1:
        if current_user.otp_enabled:
            return True
        return False
    else:
        return True

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
    Output("backup-codes-btn", "n_clicks"),
    [ Input("backup-codes-btn", "n_clicks") ],
    prevent_initial_call=True)
def generate_backup_codes(n1):
    if n1 == 1:
        backup_tokens=[]
        for i in 1, 2, 3, 4 , 5, 6 :
            t=random.randint(100000000, 999999999)
            backup_tokens.append(str(t) )
        user=User.query.filter_by(id=current_user.id).first()
        user.set_backup_tokens(backup_tokens) 
        db.session.add(user)
        db.session.commit()

        rand=html.Div(
            [   
                dbc.Row(
                    dbc.Col( html.P("Single use tokens") ,style={"textAlign":"center"}),
                    className="g-0",
                    align="center",
                    justify="center"
                ),
                dbc.Row(
                    [
                        dbc.Col(backup_tokens[0], style={"textAlign":"center"} ),
                        dbc.Col(backup_tokens[1], style={"textAlign":"center"} ),
                        dbc.Col(backup_tokens[2] , style={"textAlign":"center"}),
                    ],
                    className="g-0",
                    align="center",
                    justify="center"
                ),
                dbc.Row(
                    [
                        dbc.Col(backup_tokens[3], style={"textAlign":"center"} ),
                        dbc.Col(backup_tokens[4] , style={"textAlign":"center"}),
                        dbc.Col(backup_tokens[5] , style={"textAlign":"center"}),
                    ],
                    className="g-0",
                    align="center",
                    justify="center"                    
                    )
            ],
            style={"margin-bottom":"20px"}
        )

        return rand , -1
    if n1 == 0:
        return None, 0
        
@dashapp.callback(
    Output("modal-centered", "is_open"),
    Output("open-centered", "n_clicks"),
    Output("close-centered", "n_clicks"),
    Output("enable-disable", "n_clicks"),
    Output("app-redirect", "children"),
    Output("backup-codes-btn", "disabled"),
    Output("enable-feedback", "children"),
    Output("otp-input", "value"),
    [Input("open-centered", "n_clicks"), Input("close-centered", "n_clicks"),Input("enable-disable", "n_clicks")],
    [State("modal-centered", "is_open"), State("otp-input", "value")],
)
def toggle_modal(n1, n2,disable, is_open,otp):
    msg=None
    if disable == 1:
        if not current_user.otp_enabled :
            user=User.query.filter_by(id=current_user.id).first()
            if user.verify_totp(otp) : 
                user.otp_enabled=True
                db.session.add(user)
                db.session.commit()


                body="2FA has been enabled."
                send_email(f'[{app.config["APP_TITLE"]}] 2FA enabled', \
                    sender=app.config['MAIL_USERNAME'], \
                    recipients=[ current_user.email ], \
                    text_body=render_template('email/general.txt',
                        firstname=current_user.firstname, body=body,app_name=app.config["APP_TITLE"]),
                    html_body=render_template('email/general.html',
                        firstname=current_user.firstname, body=body,app_name=app.config["APP_TITLE"]),\
                    reply_to=app.config['MAIL_USERNAME'] )

                msg= dbc.Row(
                        [
                            dbc.Col(
                                dbc.Alert( "2FA Enabled" ,color="success",  dismissable=True),
                                style={"margin-right":"2px","textAlign":"center"},
                                width=10,
                            ),
                        ],
                        className="g-0",
                        align="center",
                        justify="center",
                        style={"margin-bottom":"10px"}
                    )
                return True, 0,0,0, None, False, msg, None
            else:
                msg= dbc.Row(
                        [
                            dbc.Col(
                                dbc.Alert( "Could not verify token" ,color="danger", dismissable=True),
                                style={"margin-right":"2px", "textAlign":"center"} ,
                                width=10,
                            ),
                        ],
                        className="g-0",
                        align="center",
                        justify="center",
                        style={"margin-bottom":"15px"}
                    )
                return True, 0,0,0, None, True, msg, otp
        else:
            return True, 0,0,0, None, True, msg, otp
    if n1 == 1:
        if not current_user.otp_enabled :
            return True, 0,0,0, None, True, msg, otp
        else:
            user=User.query.filter_by(id=current_user.id).first()
            user.otp_secret = base64.b32encode(os.urandom(10)).decode('utf-8')
            user.otp_enabled=False
            user.otp_backup=None
            db.session.add(user)
            db.session.commit()

            body="2FA has been disabled."
            send_email(f'[{app.config["APP_TITLE"]}] 2FA disabled', \
                sender=app.config['MAIL_USERNAME'], \
                recipients=[ current_user.email ], \
                text_body=render_template('email/general.txt',
                    firstname=current_user.firstname, body=body,app_name=app.config["APP_TITLE"]),
                html_body=render_template('email/general.html',
                    firstname=current_user.firstname, body=body,app_name=app.config["APP_TITLE"]),\
                reply_to=app.config['MAIL_USERNAME'] )

            return is_open, 0,0,0, dcc.Location(pathname=f"{PAGE_PREFIX}/settings/2fa/",refresh=True, id="settings-disable"), False, msg, otp
    if n2 == 1 :
        return not is_open, 0,0,0, dcc.Location(pathname=f"{PAGE_PREFIX}/settings/",refresh=True, id="settings-enable"), False, msg, otp
    return is_open, 0,0,0, None, False, msg, otp

@dashapp.callback(
    Output('pass-power', 'children'),
    Input('input-password', 'value'),
    prevent_initial_call=True)
def check_pass_power(passA):
    if passA:
        passdic=password_check(passA)
        if passdic["passtype"] == "weak":
            return make_response( "please use a strong password" ,color="danger")
        elif passdic["passtype"] == "medium":
            return make_response( "please use a strong password" ,color="warning")
        elif passdic["passtype"] == "strong":
            return make_response( "strong password" ,id="alert-auto", color="success", is_open=True, duration=1500)
    else:
        return None

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
    Output('current-pass-feedback', 'children'),
    Output('pass-feedback', 'children'),
    Output('pass2-feedback', 'children'),
    Output('checkbox-feedback', 'children'),
    Output('submission-feedback', 'children'),
    Output('current-password', 'value'),
    Output('input-password', 'value'),
    Output('input-password-2', 'value'),
    Input('submit-button-state', 'n_clicks'),
    State('first_name', 'value'),
    State('last_name', 'value'),
    State('username', 'value'),
    State('input-email', 'value'),
    State('input-email-2', 'value'),
    State('current-password', 'value'),
    State('input-password', 'value'),
    State('input-password-2', 'value'),
    State('notify', 'value'),
    State('changes-otp','value'),
    prevent_initial_call=True
    )
def submit_changes(n_clicks,first_name, last_name, username, emailA, emailB, cpass, passA, passB, notify, otp):
    first_name_=None
    last_name_=None
    username_=None
    emailA_=None
    emailB_=None
    cpass_=None
    passA_=None
    passB_=None
    notify_=None
    submission_=None
    clear_cpass_=None
    clear_passA_=None
    clear_passB_=None

    if current_user.otp_enabled:
        if not otp :
            submission_ = make_response( "Please provide 2FA token." ,color="warning")
            return first_name_,last_name_,username_, emailA_, emailB_, cpass_, passA_,passB_,notify_,submission_,clear_cpass_, clear_passA_, clear_passB_
        if not current_user.verify_totp( otp ) :
            submission_ = make_response( "Could not verify token" ,color="danger")
            return first_name_,last_name_,username_, emailA_, emailB_, cpass_, passA_,passB_,notify_,submission_,clear_cpass_, clear_passA_, clear_passB_

    if ( first_name ) and (first_name != current_user.firstname):
        user=User.query.filter_by(id=current_user.id).first()
        user.firstname=first_name
        db.session.add(user)
        db.session.commit()
        first_name_=make_response("First name changed." ,color="success", duration=1500)
    if ( last_name ) and (last_name != current_user.lastname):
        user=User.query.filter_by(id=current_user.id).first()
        user.lastname=last_name
        db.session.add(user)
        db.session.commit()
        last_name_=make_response( "Last name changed." ,color="success", duration=1500)
    if  ( username ) and (username != current_user.username) :
        user=User.query.filter_by(username=username).first()
        if user:
            if user.username == username:
                username_=make_response( "Username already exists. Please pick a different username." ,color="danger")
            else:
                user=None
        if not user:
            user=User.query.filter_by(id=current_user.id).first()
            user.username=username
            db.session.add(user)
            db.session.commit()

            body="You username has been changed."
            send_email(f'[{app.config["APP_TITLE"]}] username changed', \
                sender=app.config['MAIL_USERNAME'], \
                recipients=[ current_user.email ], \
                text_body=render_template('email/general.txt',
                    firstname=current_user.firstname, body=body,app_name=app.config["APP_TITLE"]),
                html_body=render_template('email/general.html',
                    firstname=current_user.firstname, body=body,app_name=app.config["APP_TITLE"]),\
                reply_to=app.config['MAIL_USERNAME'] )

            username_=make_response( "Username changed." ,color="success", duration=1500)

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

                emailA_=dcc.Location(pathname=f"{PAGE_PREFIX}/logout/email/", id='login')
                return first_name_,last_name_,username_, emailA_, emailB_, cpass_, passA_,passB_,notify_,submission_,clear_cpass_, clear_passA_, clear_passB_

    if ( passA ) and ( not current_user.check_password(passA) ):
        passdic=password_check(passA)
        if  ( not current_user.check_password(cpass) ) :
            cpass_= make_response( "Wrong password" ,color="danger")
        elif passdic["passtype"] != "strong" :
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

            body="You password has been changed."
            send_email(f'[{app.config["APP_TITLE"]}] password changed', \
                sender=app.config['MAIL_USERNAME'], \
                recipients=[ current_user.email ], \
                text_body=render_template('email/general.txt',
                    firstname=current_user.firstname, body=body,app_name=app.config["APP_TITLE"]),
                html_body=render_template('email/general.html',
                    firstname=current_user.firstname, body=body,app_name=app.config["APP_TITLE"]),\
                reply_to=app.config['MAIL_USERNAME'] )


            passA_=make_response( "Password changed." ,color="success", duration=1500)
 
    if  ( notify  )and ( not current_user.notifyme ):
        user=User.query.filter_by(id=current_user.id).first()
        user.notifyme=True
        notify_=make_response( "Notifications enabled." ,color="success", duration=1500)

    elif ( not notify ) and ( current_user.notifyme ):
        user=User.query.filter_by(id=current_user.id).first()
        user.notifyme=False
        notify_=make_response( "Notifications disabled." ,color="warning")

    return first_name_,last_name_,username_, emailA_, emailB_, cpass_, passA_,passB_,notify_,submission_,clear_cpass_, clear_passA_, clear_passB_