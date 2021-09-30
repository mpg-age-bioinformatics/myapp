from dash_html_components.H3 import H3
from flaskapp import app, db
import dash
from dash.dependencies import Input, Output, State
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from flaskapp.models import User, PrivateRoutes, PRIVATE_ROUTES
from flaskapp.email import send_contact
from datetime import datetime
from ._utils import META_TAGS ,check_email, navbar_A, protect_dashviews, make_options
from flask_login import current_user, logout_user

def get_urls(app):
    urls=['%s' % rule for rule in app.url_map.iter_rules()]
    def clean_url(url):
        url=url.split("/")[1]
        if len(url) > 0:
            if (url[0]!="_") and ( ":" not in url):
                return url
        return None
    urls=[ clean_url(s) for s in urls ]
    urls=list(set(urls))
    urls=[ s for s in urls if s ]
    public=[ "assets", "static", "forgot" ,"impressum", "login", "about" ,"contact", "register", "logout", "privacy"]
    public=[ "assets", "static", "forgot" ,"impressum", "login", "contact", "register", "logout", "privacy"]
    urls=[ s for s in urls if s not in public ]
    return urls

def get_user_status(email):
    user=User.query.filter_by(email=email).first()

    if user.view_apps:
        view_apps=f'- view_apps: {", ".join(user.view_apps)}'
    else:
        view_apps='- view_apps: None'
    if user.user_apps:
        user_apps=f'- user_apps: {", ".join(user.user_apps)}'
    else:
        user_apps='- user_apps: None'

    user=f'''**{user.email}**\n\n\
    - name: {user.firstname} {user.lastname}\n\
    - registered on: {user.registered_on}\n\
    - confirmed on: {user.confirmed_on}\n\
    - last seen: {user.last_seen}\n\
    - is authenticated: {user.is_authenticated}\n\
    - active: {user.active}\n\
    - inactive reason: {user.inactive_reason}\n\
    - notifyme: {user.notifyme}\n\
    - administrator: {user.administrator}\n\
    {view_apps}\n\
    {user_apps}\n\n\
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

    email_options = dcc.Dropdown( options=emails, placeholder="select user", id='opt-status-emails', multi=True, style={"width":"350px", "margin-right":"8px"})
    activate_button=html.Button(id='status-activate-button', n_clicks=0, children='Activate', style={"width":"100px", "margin-right":"4px"})

    deactivate_msg=dcc.Textarea( id='status-deactivate-text', placeholder="  deactivate reason..",style={ "margin-right":"8px", "max-width":"542px", "min-width":"350px", 'height': 32 } )
    deactivate_bt=html.Button(id='status-deactivate-button', n_clicks=0, children='Deactivate', style={"width":"100px"})

    change_active_status = html.Div([ 
        dbc.Label(html.H4("User status"),html_for="change-status-form"), 
        dbc.Form( [ dbc.FormGroup(
                        [ email_options,activate_button ],
                        className="mr-3"
                        ),
                    ],
                inline=True,
                style={"width":"auto","margin-top":"10px"}
                ),
        dbc.Form( [ dbc.FormGroup(
                        [ deactivate_msg,deactivate_bt ],
                        className="mr-3"
                        ),
                    ],
                style={"width":"auto","margin-top":"10px"},
                inline=True,
                ),
        html.Div(id="status-deactivate-text-feedback",style={'margin-top':"10px"}),
        html.Div(id="status-activate-feedback",style={'margin-top':"10px"}),
        html.Div(id='status-deactivate-feedback',style={'margin-top':"10px"}),
        html.Div(id='status-current-feedback',style={'margin-top':"10px"})
        ], id="change-status-form" )

    ### private routes

    # routes=get_urls(app)
    routes_=make_options(PRIVATE_ROUTES)

    empty_=make_options([])

    routes_options = dcc.Dropdown( options=routes_, value=None, placeholder="route", id='opt-routes', multi=False, style={"width":"350px", "margin-right":"8px"})
    list_route_button=html.Button(id='list_route-button-state', disabled=True,  n_clicks=0, children='List', style={"width":"100px", "margin-right":"4px"})

    no_access_email_options = dcc.Dropdown( options=empty_, placeholder="select a route first", id='opt-noroutes-emails', multi=True, style={"width":"350px", "margin-right":"8px"})
    grant_route_button=html.Button(id='grant_route-button-state', disabled=True,  n_clicks=0, children='Grant', style={"width":"100px", "margin-right":"4px"})

    private_email_options = dcc.Dropdown( options=empty_, placeholder="select a route first", id='opt-routes-emails', multi=True, style={"width":"350px", "margin-right":"8px"})
    revoke_route_button=html.Button(id='revoke_route-button-state', disabled=True,  n_clicks=0, children='Revoke', style={"width":"100px", "margin-right":"4px"})

    grant_domain_text=dbc.Input(type="text", id="domain-text", placeholder="select a route first",style={"width":"350px", "margin-right":"8px"})
    grant_domain_button=html.Button(id='grant_domain-button-state', disabled=True,  n_clicks=0, children='Add', style={"width":"100px", "margin-right":"4px"})

    private_domain_options = dcc.Dropdown( options=empty_, placeholder="select a route first", id='opt-routes-domains', multi=True, style={"width":"350px", "margin-right":"8px"})
    revoke_domain_button=html.Button(id='revoke_domain-button-state', disabled=True,  n_clicks=0, children='Remove', style={"width":"100px", "margin-right":"4px"})



    routes_form = html.Div([ 
        dbc.Label(html.H4("Private routes"),html_for="list_route_form", style={"margin-top":"40px"}), 
        dbc.Form( [ dbc.FormGroup(
                        [ routes_options, list_route_button],
                        className="mr-3"
                        ),
                  ],
                  inline=True,
                  id="list_route_form",
                  style={"width":"auto","margin-top":"10px"}
                ),
        dbc.Form( [ dbc.FormGroup(
                        [ no_access_email_options, grant_route_button ],
                        className="mr-3"
                    ),
                ],
                inline=True,
                id="add_route_form",
                style={"width":"auto","margin-top":"10px"}
                ),
        dbc.Form( [ dbc.FormGroup(
                        [ private_email_options, revoke_route_button ],
                        className="mr-3"
                    ),
                ],
                inline=True,
                id="rm_route_form",
                style={"width":"auto","margin-top":"10px"}
                ),
        dbc.Form( [ dbc.FormGroup(
                        [ grant_domain_text, grant_domain_button ],
                        className="mr-3"
                    ),
                ],
                inline=True,
                id="rm_route_form",
                style={"width":"auto","margin-top":"10px"}
                ),
        dbc.Form( [ dbc.FormGroup(
                        [ private_domain_options, revoke_domain_button ],
                        className="mr-3"
                    ),
                ],
                inline=True,
                id="rm_route_form",
                style={"width":"auto","margin-top":"10px"}
                ),
        html.Div(id="routes-feedback",style={'margin-top':"10px"}) ])


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
            ),
 
        ],
        inline=True,
        id="notify_form"
    ),
    html.Div(id="notify-feedback",style={'margin-top':"10px"}),
    html.Div(id="notifyall-feedback",style={'margin-top':"10px"})])

    protected_content=dbc.Row( [
        dbc.Col( [ html.Div(id="submission-feedback"), 
                    change_active_status,
                    routes_form, 
                    make_admin_form,
                    notify_section,
                    ],
                md=10, lg=9, xl=8, align="center",style={ "margin-left":2, "margin-right":2 ,'margin-bottom':"50px"}),
        navbar_A
    ],
    align="center",
    justify="center",
    style={"min-height": "95vh", 'verticalAlign': 'center'})

    return protected_content

@dashapp.callback(
    Output('status-current-feedback', 'children'),
    Input('opt-status-emails', 'value'),
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

@dashapp.callback(
    Output('status-activate-feedback', 'children'),
    Input('status-activate-button', 'n_clicks'),
    State('opt-status-emails', 'value'),
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
    Output('status-deactivate-feedback', 'children'),
    Output('status-deactivate-text-feedback', 'children'),
    Input('status-deactivate-button', 'n_clicks'),
    State('status-deactivate-text', 'value'),
    State('opt-status-emails', 'value'),
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
        msg=dbc.Alert( msg ,color="danger",  dismissable=True, style={"max-width":"458px"})

    non_admin_emails= [ u.email for u in User.query.all() if not u.administrator ]
    non_admin_emails.sort()
    non_admin_emails=make_options(non_admin_emails)

    admin_emails= [ u.email for u in User.query.all() if u.administrator ]
    admin_emails.sort()
    admin_emails=make_options(admin_emails)

    return admin_emails, non_admin_emails, 0, 0, None, None, msg

@dashapp.callback(
    Output('grant_domain-button-state', 'disabled'),
    Input('domain-text', 'value'),
)
def toggle_add_domain(value):
    if value :
        return False
    else:
        return True

@dashapp.callback(
    Output('revoke_domain-button-state', 'disabled'),
    Input('opt-routes-domains', 'value'),
)
def toggle_rm_domain(value):
    if value :
        return False
    else:
        return True


##### this needs to output n_clicks of grant and revoke instead of doing it in the next call
@dashapp.callback(
    Output('list_route-button-state', 'disabled'),
    Output('opt-noroutes-emails', 'options'),
    Output('opt-noroutes-emails', 'placeholder'),
    Output('opt-routes-emails', 'options'),
    Output('opt-routes-emails', 'placeholder'),
    Output('opt-noroutes-emails', 'value'),
    Output('opt-routes-emails', 'value'),
    Output('opt-routes-domains', 'options'),
    Output('opt-routes-domains', 'value'),
    Output('opt-routes-domains', 'placeholder'),
    Output('domain-text', 'placeholder'),
    Output('domain-text', 'value'),
    Input('opt-routes', 'value')    )
def toggle_private_routes(route):
    if not route:
        empty_=make_options([])
        return True, empty_, "select a route first", empty_, "select a route first", None, None, empty_, None, "select a route first", "select a route first", None
    
    route_obj=PrivateRoutes.query.filter_by(route=route).first()
    if not route_obj :
        print("!!!! No routes")
        emails= [ u.email for u in User.query.all() ]
        emails.sort()
        emails=make_options(emails)
        empty_=make_options([])

        return True, emails, "select user", empty_, "no users here", None, None, empty_, None, "no domains here", "add domain, eg. gmail.com",  None

    if not route_obj.users_domains :
        print("!!!! No routes")
        users_domains=make_options([])
        users_domains_placeholder="no domains here"
    else:
        users_domains=make_options(route_obj.users_domains)
        users_domains_placeholder="remove a domain"
    users_domains_value=None
    
    if not route_obj.users :
        emails= [ u.email for u in User.query.all() ]
        emails.sort()
        emails=make_options(emails)
        empty_=make_options([])

        return True, emails, "select user", empty_, "no users here", None, None, users_domains, users_domains_value, users_domains_placeholder, "add domain, eg. gmail.com", None

    users=route_obj.users
    granted_emails=[]
    for u in users:
        user=User.query.filter_by(id=u).first()
        granted_emails.append(user.email)
    granted_emails.sort()

    no_granted_emails=[ u.email for u in User.query.all() ]
    no_granted_emails=[ u for u in no_granted_emails if u not in granted_emails ]
    no_granted_emails.sort()

    if no_granted_emails:
        su="select user"
    else:
        su="no users here"


    granted_emails=make_options(granted_emails)
    no_granted_emails=make_options(no_granted_emails)


    return False, no_granted_emails, su, granted_emails, "select user", None, None, users_domains, users_domains_value, users_domains_placeholder, "add domain, eg. gmail.com", None


@dashapp.callback(
    Output('opt-routes', 'value'),
    Output('routes-feedback', 'children'),
    Output('list_route-button-state',"n_clicks"),
    Output('grant_route-button-state',"n_clicks"),
    Output('revoke_route-button-state',"n_clicks"),
    Output('grant_domain-button-state',"n_clicks"),
    Output('revoke_domain-button-state',"n_clicks"),
    Input('list_route-button-state',"n_clicks"),
    Input('grant_route-button-state',"n_clicks"),
    Input('revoke_route-button-state',"n_clicks"),
    Input('grant_domain-button-state',"n_clicks"),
    Input('revoke_domain-button-state',"n_clicks"),
    State('opt-routes', 'value'),
    State('opt-noroutes-emails', 'value'),
    State('opt-routes-emails', 'value'),
    State('domain-text', 'value'),
    State('opt-routes-domains', 'value'),
    prevent_initial_call=True
    )
def change_routes(l_clicks, g_clicks, r_clicks, add_domain_clicks, rm_domain_clicks ,route, grant_emails, revoke_emails, domain, domains_out ):
    if l_clicks == 1:
        route_obj=PrivateRoutes.query.filter_by(route=route).first()
        users=route_obj.users
        emails=[]
        if users:
            for u in users:
                email=User.query.filter_by(id=u).first()
                emails.append(email.email)
            emails.sort()
        domains=[]
        if route_obj.users_domains :
            domains=domains+route_obj.users_domains
            domains=f'''\n\n-domains- {", ".join(domains)}'''
        else:
            domains=""
        msg=f'''{route}: {", ".join(emails)}'''
        msg=msg+domains
        msg=dbc.Alert( msg ,color="primary", style={"max-width":"458px"},  dismissable=True)

        return None, msg, 0, 0 ,0, 0, 0
    
    if g_clicks == 1:
        route_obj=PrivateRoutes.query.filter_by(route=route).first()
        if not route_obj:
            route_obj=PrivateRoutes(route=route)
        if route_obj.users:
            users_ids=route_obj.users
        else:
            users_ids=[]
        for email in grant_emails:
            u=User.query.filter_by(email=email).first()
            user_apps=u.user_apps
            if not user_apps:
                user_apps=[route_obj.id]
            u.user_apps=user_apps
            db.session.add(u)
            db.session.commit()
            users_ids.append(u.id)
        route_obj.users=users_ids
        db.session.add(route_obj)
        db.session.commit()

        msg=f'''{route}: {", ".join(grant_emails)}\nGranted!'''

        msg=dbc.Alert( msg ,color="success", style={"max-width":"458px"},  dismissable=True)

        return None, msg, 0, 0, 0, 0, 0

    if add_domain_clicks == 1:
        route_obj=PrivateRoutes.query.filter_by(route=route).first()
        if not route_obj:
            route_obj=PrivateRoutes(route=route)
        if route_obj.users_domains:
            domains=route_obj.users_domains
        else:
            domains=[]
        domains.append(domain)
        route_obj.users_domains=domains
        db.session.add(route_obj)
        db.session.commit()

        msg=f'''{route}: {domain}\nGranted!'''

        msg=dbc.Alert( msg ,color="success", style={"max-width":"458px"},  dismissable=True)

        return None, msg, 0, 0, 0, 0, 0

    if rm_domain_clicks == 1:
        route_obj=PrivateRoutes.query.filter_by(route=route).first()
        domains=route_obj.users_domains
        domains=[s for s in domains if s not in domains_out ]
        route_obj.users_domains=domains
        db.session.add(route_obj)
        db.session.commit()

        msg=f'''{route}: {", ".join(domains_out)}\nRemoved!'''

        msg=dbc.Alert( msg ,color="danger", style={"max-width":"458px"},  dismissable=True)

        return None, msg, 0, 0, 0, 0, 0

    if r_clicks == 1:
        route_obj=PrivateRoutes.query.filter_by(route=route).first()
        users_ids=route_obj.users
        revoke_ids=[]
        for email in revoke_emails:
            u=User.query.filter_by(email=email).first()
            user_apps=u.user_apps
            user_apps=[ s for s in user_apps if s != route_obj.id ]
            u.user_apps=user_apps
            db.session.add(u)
            db.session.commit()
            revoke_ids.append(u.id)
        users_ids = [ s for s in users_ids if s not in revoke_ids ]
        route_obj.users=users_ids
        db.session.add(route_obj)
        db.session.commit()

        msg=f'''{route}: {", ".join(revoke_emails)}\nRevoked!'''
        msg=dbc.Alert( msg ,color="danger", style={"max-width":"458px"},  dismissable=True)

        return None, msg, 0, 0, 0, 0, 0
            

@dashapp.callback(
    Output('grant_route-button-state',"disabled"),
    Input('opt-noroutes-emails','value')  )
def toggle_grant_route(value):
    # print("!!!!!", value)
    if value:
        return False
    else:
        return True

@dashapp.callback(
    Output('revoke_route-button-state',"disabled"),
    Input('opt-routes-emails','value') )
def toggle_revoke_route(value):
    if value:
        return False
    else:
        return True