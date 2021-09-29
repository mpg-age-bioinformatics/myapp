from dash_html_components.H3 import H3
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
from flask_login import current_user, logout_user

def get_user_status(email):
    user=User.query.filter_by(email=email).first()
    user=f'''**{user.email}**\n\n\
    - name: {user.firstname} {user.lastname}\n\
    - registered on: {user.registered_on}\n\
    - confirmed on: {user.confirmed_on}\n\
    - last seen: {user.last_seen}\n\
    - is authenticated: {user.is_authenticated}\n\
    - active: {user.active}\n\
    - inactive reason: {user.inactive_reason}\n\
    - notifyme: {user.notifyme}\n\
    - administrator: {user.administrator}\n\n\
*{datetime.now()}*'''
    return user

dashapp = dash.Dash("admin",url_base_pathname='/admin/', meta_tags=META_TAGS, server=app, external_stylesheets=[dbc.themes.BOOTSTRAP], title=app.config["APP_TITLE"], assets_folder=app.config["APP_ASSETS"])

protect_dashviews(dashapp)

dashapp.layout=html.Div( [ dcc.Location(id='url', refresh=False), html.Div(id="protected-content") ] )

@dashapp.callback(
    Output('protected-content', 'children'),
    Input('url', 'pathname'))
def make_layout(pathname):
    # if not current_user.administrator :
    #     return dcc.Location(pathname="/index/", id='index')


    #### User status

    emails= [ u.email for u in User.query.all() ]
    emails.sort()
    emails=[ "all" ] + emails
    emails=make_options(emails)

    email_options = dcc.Dropdown( options=emails, placeholder="select user", id='opt-emails', multi=True, style={"width":"350px", "margin-right":"8px"})

    activate_button=html.Button(id='activate-button-state', n_clicks=0, children='Activate', style={"width":"100px", "margin-right":"4px"})
    # deactivate_button=html.Button(id='deactivate-button-state', n_clicks=0, children='Deactivate', style={"width":"auto", "margin-left":"4px"})

    # dbc.Label("User status",html_for="change_active_status_form")
    change_active_status = html.Div([ 
        dbc.Label(html.H4("User status"),html_for="change_active_status_form"), 
        dbc.Form( [ dbc.FormGroup(
                [
                    email_options,
                    activate_button
                ],
                className="mr-3"
            ),
        ],
        inline=True,
        id="change_active_status_form"
    )])

    deactivate_msg=dcc.Textarea( id='text-reason', placeholder="deactivate reason..",style={ "margin-right":"8px", "max-width":"542px", "min-width":"350px", 'height': 32 } )
    deactivate_bt=html.Button(id='reason-button-state', n_clicks=0, children='Deactivate', style={"width":"100px"})

    deactivate=html.Div([ 
        dbc.Form( [ dbc.FormGroup(
                [
                    deactivate_msg,deactivate_bt
                ],
                className="mr-3"
            ),
        ],
        style={"width":"auto",},
        inline=True,
        id="change_active_status_form"
    )],style={"width":"auto","margin-top":"10px"})


    #### Administrators

    non_admin_emails= [ u.email for u in User.query.all() if not u.administrator ]
    non_admin_emails.sort()
    non_admin_emails=make_options(non_admin_emails)

    admin_emails= [ u.email for u in User.query.all() if u.administrator ]
    admin_emails.sort()
    admin_emails=make_options(admin_emails)

    non_admin_options = dcc.Dropdown( options=non_admin_emails, placeholder="standard users", id='opt-non_admin_emails', multi=True, style={"width":"350px", "margin-right":"8px"})
    admin_options = dcc.Dropdown( options=admin_emails, placeholder="administrators", id='opt-admin_emails', multi=True, style={"width":"350px", "margin-right":"8px"})

    make_admin_button=html.Button(id='makeadmin-button-state',disabled=True,  n_clicks=0, children='Grant', style={"width":"100px", "margin-right":"4px"})
    rm_admin_button=html.Button(id='rmadmin-button-state',disabled=True, n_clicks=0, children='Revoke', style={"width":"100px", "margin-right":"4px"})

    make_admin_form = html.Div([ 
        dbc.Label(html.H4("Administrators"),html_for="make_admin_form", style={"margin-top":"40px"}), 
        dbc.Form( [ dbc.FormGroup(
                                [
                                    non_admin_options,
                                    make_admin_button
                                ],
                                className="mr-3"
                                ),
                  ],
                  inline=True,
                  id="make_admin_form",
                  style={"width":"auto","margin-top":"10px"}
                ),
        dbc.Form( [ dbc.FormGroup(
                [
                    admin_options,
                    rm_admin_button
                ],
                className="mr-3"
            ),
        ],
        inline=True,
        id="rm_admin_form",
        style={"width":"auto","margin-top":"10px"}
        ),
        html.Div(id="admin-feedback",style={'margin-top':"10px"}) ])

    #### Notify

    notify_section = html.Div([ 
        dbc.Label(html.H4("Notify"),html_for="notify_form", style={"margin-top":"40px"}), 
        dbc.Form( [ dbc.FormGroup(
                [
                    html.Button(id='notify-button-state', n_clicks=0, children='Notify', style={"width":"auto", "margin-right":"4px"}),
                    html.Button(id='notifyall-button-state', n_clicks=0, children='Notify All', style={"width":"auto", "margin-left":"4px"}), 

                ],
                className="mr-3"
            )
        ],
        inline=True,
        id="notify_form"
    )])

    protected_content=dbc.Row( [
        dbc.Col( [ dbc.Form([  html.Div(id="submission-feedback"),
                                change_active_status,
                                deactivate,
                                html.Div(id="input-reason-feedback",style={'margin-top':"10px"}),
                                html.Div(id="activate-feedback",style={'margin-top':"10px"}),
                                html.Div(id="deactivate-feedback",style={'margin-top':"10px"}),
                                html.Div(id="current-status-feedback",style={'margin-top':"10px"}),
                            ]),

                    make_admin_form,

                    dbc.Form([  notify_section,
                                html.Div(id="notify-feedback",style={'margin-top':"10px"}),
                                html.Div(id="notifyall-feedback",style={'margin-top':"10px"}),
                            ])
                ],
                md=10, lg=9, xl=8, align="center",style={ "margin-left":2, "margin-right":2 ,'margin-bottom':"50px"}),
        navbar_A
    ],
    align="center",
    justify="center",
    style={"min-height": "95vh", 'verticalAlign': 'center'})

    return protected_content

@dashapp.callback(
    Output('current-status-feedback', 'children'),
    Input('opt-emails', 'value'),
    prevent_initial_call=True
    )
def current_status(emails):
    if not emails:
        return None
    status=[]
    if "all" in emails:
        emails= [ u.email for u in User.query.all() ]
    for email in emails:
        user=get_user_status(email)
        status.append(user)
    status="\n\n*************\n\n".join(status)
    status=dcc.Markdown(status)
    return dbc.Alert( status ,color="#EFEFEF",  dismissable=True)

# @app.callback(
#     Output("current-status-alert", "is_open"),
#     [Input("alert-toggle-fade", "n_clicks")],
#     [State("alert-fade", "is_open")],
# )
# def toggle_alert(n, is_open):
#     if n:
#         return not is_open
#     return is_open

@dashapp.callback(
    Output('activate-feedback', 'children'),
    Input('activate-button-state', 'n_clicks'),
    State('opt-emails', 'value'),
    prevent_initial_call=True
    )
def activate_user(n_clicks, emails):
    if not emails :
        return dbc.Alert( "Please select a user." ,color="warning", style={"max-width":"458px"},  dismissable=True)
    if "all" in emails:
        emails= [ u.email for u in User.query.all() ]
    status=[]
    for email in emails:
        user=User.query.filter_by(email=email).first()
        user.active=True
        db.session.add(user)
        db.session.commit()
        user=get_user_status(email)
        status.append(user)
    status="\n\n*************\n\n".join(status)
    status=dcc.Markdown(status)
    return dbc.Alert( status ,color="success",  dismissable=True)

@dashapp.callback(
    Output('deactivate-feedback', 'children'),
    Output('input-reason-feedback', 'children'),
    Input('reason-button-state', 'n_clicks'),
    State('text-reason', 'value'),
    State('opt-emails', 'value'),
    prevent_initial_call=True
    )
def submit_deactivate(n_clicks, reason, emails):
    if not emails :
        return None, dbc.Alert( "Please select a user." ,color="warning", style={"max-width":"458px"},dismissable=True)
    if not reason :
        return None, dbc.Alert( "Please give in a reason." ,color="warning", style={"max-width":"458px"},dismissable=True)
    if "all" in emails:
        emails= [ u.email for u in User.query.all() if not u.administrator ]
    status=[]
    for email in emails:
        user=User.query.filter_by(email=email).first()
        user.active=False
        db.session.add(user)
        db.session.commit()
        user=get_user_status(email)
        status.append(user)
    status="\n\n*************\n\n".join(status)
    status=dcc.Markdown(status)
    return dbc.Alert( status ,color="danger",  dismissable=True), None

@dashapp.callback(
    Output('notify-feedback', 'children'),
    Input('notify-button-state', 'n_clicks'),
    prevent_initial_call=True
    )
def notify_users(n_clicks):
    emails= [ u.email for u in User.query.all() ]
    emails=", ".join(emails)
    return dbc.Alert( emails ,color="primary", style={"max-width":"458px"},  dismissable=True)

@dashapp.callback(
    Output('notifyall-feedback', 'children'),
    Input('notifyall-button-state', 'n_clicks'),
    prevent_initial_call=True
    )
def notifyall_users(n_clicks):
    emails= [ u.email for u in User.query.all() if u.notifyme ]
    emails=", ".join(emails)
    return dbc.Alert( emails ,color="warning", style={"max-width":"458px"},  dismissable=True)

@dashapp.callback(
    Output('makeadmin-button-state', 'disabled'),
    Input('opt-non_admin_emails', 'value'),
    prevent_initial_call=True
    )
def togle_grant_button(value):
    if value:
        return False
    else:
        return True

@dashapp.callback(
    Output('rmadmin-button-state', 'disabled'),
    Input('opt-admin_emails', 'value'),
    prevent_initial_call=True
    )
def togle_revoke_button(value):
    if value:
        return False
    else:
        return True

@dashapp.callback(
    Output('opt-admin_emails', 'options'),
    Output('opt-non_admin_emails', 'options'),
    Output('makeadmin-button-state', 'n_clicks'),
    Output('rmadmin-button-state', 'n_clicks'),
    Output('opt-admin_emails', 'value'),
    Output('opt-non_admin_emails', 'value'),
    Output('admin-feedback', 'children'),
    Input('makeadmin-button-state', 'n_clicks'),
    Input('rmadmin-button-state', 'n_clicks'),
    State('opt-admin_emails', 'value'),
    State('opt-non_admin_emails', 'value'),
    prevent_initial_call=True
    )
def change_admins(mk_clicks,rm_clicks,admin_emails, non_admin_emails):
    if mk_clicks == 1:
        for email in non_admin_emails:
            user=User.query.filter_by(email=email).first()
            user.administrator=True
            db.session.add(user)
            db.session.commit()
        msg="Granted: "+", ".join(non_admin_emails)
        print(msg)
        msg=dbc.Alert( msg ,color="success",  dismissable=True,style={"max-width":"458px"})
        mk_clicks=0
    if rm_clicks == 1:
        for email in admin_emails:
            user=User.query.filter_by(email=email).first()
            user.administrator=False
            db.session.add(user)
            db.session.commit()
        mk_clicks=0
        msg="Revoked: "+", ".join(admin_emails)
        msg=dbc.Alert( msg ,color="danger",  dismissable=True,style={"max-width":"458px"})




    non_admin_emails= [ u.email for u in User.query.all() if not u.administrator ]
    non_admin_emails.sort()
    non_admin_emails=make_options(non_admin_emails)

    admin_emails= [ u.email for u in User.query.all() if u.administrator ]
    admin_emails.sort()
    admin_emails=make_options(admin_emails)

    return admin_emails, non_admin_emails, 0, 0, None, None, msg

