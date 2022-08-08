from myapp import app, db, PRIVATE_ROUTES, PAGE_PREFIX
import dash
from dash.dependencies import Input, Output, State
from dash import dcc, html
import dash_bootstrap_components as dbc
from myapp.models import User, PrivateRoutes
from datetime import datetime
from ._utils import META_TAGS, navbar_A, protect_dashviews, make_options, make_navbar_logged
import base64
from flask_login import current_user

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
        view_apps=[]
        for i in user.view_apps :
            route_obj=PrivateRoutes.query.filter_by(id=i).first()
            if not route_obj :
                continue
            view_apps.append(route_obj.route)
        if not view_apps:
            view_apps='- view_apps: None'
        else:
            view_apps=f'- view_apps: {", ".join(view_apps)}'
    else:
        view_apps='- view_apps: None'
    
    if user.user_apps:
        user_apps=[]
        for i in user.user_apps :
            route_obj=PrivateRoutes.query.filter_by(id=i).first()
            if not route_obj:
                continue
            user_apps.append(route_obj.route)
        if not user_apps:
            user_apps=f'- user_apps: None'
        else:
            user_apps=f'- user_apps: {", ".join(user_apps)}'
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

dashapp = dash.Dash("admin",url_base_pathname=f'{PAGE_PREFIX}/admin/', meta_tags=META_TAGS, server=app, external_stylesheets=[dbc.themes.BOOTSTRAP], title=app.config["APP_TITLE"], assets_folder=app.config["APP_ASSETS"])

protect_dashviews(dashapp)

dashapp.layout=html.Div( [ dcc.Location(id='url', refresh=False), html.Div(id="protected-content") ] )

options_field_style={}#{"width":"335px"}
button_style={"width":"100%"}#, "margin-top":"0px", "margin-bottom":"10px"}#{"width":"100px", "margin-top":"4px","margin-bottom":"4px"}
h4_style={"margin-top":"40px"}
div_feedback_style={}#'margin-top':"10px"}
form_style={}#"width":"auto","margin-top":"10px"}
alert_short_style={"max-width":"458px"}

@dashapp.callback(
    Output('protected-content', 'children'),
    Input('url', 'pathname'))
def make_layout(pathname):
    if not current_user.administrator :
        return dcc.Location(pathname=f"{PAGE_PREFIX}/index/", id='index')

    def make_form_row(input_field, button_field):
        form_row=dbc.Form( 
            [ 
                dbc.Row(
                    [ 
                        dbc.Col(input_field, width=8), dbc.Label(button_field, style={"margin":0}, width=4)
                    ],
                    # row=True,
                    style={"max-width":"510px"},
                    className="mb-3 g-1",
                ),
            ],
            style=form_style
        )
        return form_row


    #### User status

    ## we collect all emails for this because in future we might want
    ## to add some more actions to the Activate button
    emails= [ u.email for u in User.query.all() ]
    emails.sort()
    emails=[ "all" ] + emails
    emails=make_options(emails)

    opt_status_emails= dcc.Dropdown( options=emails, placeholder="select user", id='opt-status-emails', multi=True, style=options_field_style)
    status_activate_btn=html.Button(id='status-activate-button', n_clicks=0, children='Activate', style=button_style)

    status_deactivate_text=dbc.Input(type="text", id='status-deactivate-text', placeholder="deactivate reason",style=options_field_style)
    status_deactivate_btn=html.Button(id='status-deactivate-button', n_clicks=0, children='Deactivate', style=button_style)

    user_status_form = html.Div(
        [ 
            dbc.Label(html.H4("User status"), style=h4_style),
            make_form_row(opt_status_emails, status_activate_btn),
            make_form_row(status_deactivate_text, status_deactivate_btn),
            html.Div(id="status-deactivate-text-feedback",style=div_feedback_style),
            html.Div(id="status-activate-feedback",style=div_feedback_style),
            html.Div(id='status-deactivate-feedback',style=div_feedback_style),
            html.Div(id='status-current-feedback',style=div_feedback_style)
        ]
    )

    ### private routes

    # routes=get_urls(app)
    private_routes=make_options(PRIVATE_ROUTES)

    empty_=make_options([])

    opt_routes_priv_routes = dcc.Dropdown( options=private_routes, value=None, placeholder="route", id='opt-routes-priv-routes', multi=False, style=options_field_style)
    routes_list_btn=html.Button(id='routes-list-button', disabled=True,  n_clicks=0, children='List', style=button_style)

    opt_routes_no_access = dcc.Dropdown( options=empty_, placeholder="select a route first", id='opt-routes-no-access', multi=True, style=options_field_style)
    routes_grant_btn=html.Button(id='routes-grant-button', disabled=True,  n_clicks=0, children='Grant', style=button_style)

    opt_routes_access = dcc.Dropdown( options=empty_, placeholder="select a route first", id='opt-routes-access', multi=True, style=options_field_style)
    routes_revoke_btn=html.Button(id='routes-revoke-button', disabled=True,  n_clicks=0, children='Revoke', style=button_style)

    routes_domain_text=dbc.Input(type="text", id='routes-domain-text', placeholder="select a route first",style=options_field_style)
    routes_add_btn=html.Button(id='routes-add-button', disabled=True,  n_clicks=0, children='Add', style=button_style)

    opt_routes_domains = dcc.Dropdown( options=empty_, placeholder="select a route first", id='opt-routes-domains', multi=True, style=options_field_style)
    routes_rm_btn=html.Button(id='routes-rm-button', disabled=True,  n_clicks=0, children='Remove', style=button_style)

    private_routes_form = html.Div(
        [ 
            dbc.Label(html.H4("Private routes"), style=h4_style),
            make_form_row(opt_routes_priv_routes, routes_list_btn),
            make_form_row(opt_routes_no_access, routes_grant_btn),
            make_form_row(opt_routes_access, routes_revoke_btn),
            make_form_row(routes_domain_text, routes_add_btn),
            make_form_row(opt_routes_domains, routes_rm_btn),
            html.Div(id="routes-feedback",style=div_feedback_style) 
        ]
    )


    #### Administrators

    non_admin_emails= [ u.email for u in User.query.all() if not u.administrator ]
    non_admin_emails.sort()
    non_admin_emails=make_options(non_admin_emails)

    admin_emails= [ u.email for u in User.query.all() if u.administrator ]
    admin_emails.sort()
    admin_emails=make_options(admin_emails)

    opt_admin_std_emails = dcc.Dropdown( options=non_admin_emails, placeholder="standard users", id='opt-admin-std-emails', multi=True, style=options_field_style)
    opt_admin_emails = dcc.Dropdown( options=admin_emails, placeholder="administrators", id='opt-admin-emails', multi=True, style=options_field_style)

    admin_grant_button=html.Button(id='admin-grant-button',disabled=True,  n_clicks=0, children='Grant', style=button_style)
    rm_admin_button=html.Button(id='admin-revoke-button',disabled=True, n_clicks=0, children='Revoke', style=button_style)

    administrators_form = html.Div(
        [ 
            dbc.Label(html.H4("Administrators"),style=h4_style),
            make_form_row(opt_admin_std_emails, admin_grant_button),
            make_form_row(opt_admin_emails, rm_admin_button),
            html.Div(id="admin-feedback",style=div_feedback_style) 
        ]
    )

    #### Notify

    notify_form = html.Div(
        [ 
            dbc.Label(html.H4("Notify"), style=h4_style),
            dbc.Form( 
                [ 
                    html.Div(
                        [ 
                            html.Button(id='notify-button', n_clicks=0, children='Notify', style={"width":"100px","margin":"3px"}), 
                            html.Button(id='notify-all-button', n_clicks=0, children='Notify All', style={"width":"100px","margin":"3px"})
                        ],
                    # row=True,
                    style={"max-width":"510px","margin-left":"0px" },
                    ),
                ],
                style=form_style
                ),
            html.Div(id="notify-feedback",style=div_feedback_style),
            html.Div(id='notify-all-feedback',style=div_feedback_style)
        ]
    )

    navbar=make_navbar_logged("Administrator Dashboard",current_user)

    protected_content=html.Div(
        [ 
            navbar,
            dbc.Row(
                [
                    dbc.Col( 
                        dbc.Card(
                            [  
                                html.Div(id="submission-feedback"), 
                                user_status_form,
                                private_routes_form, 
                                administrators_form,
                                notify_form,
                            ],
                            body=True,
                            className="border-0"
                        ),
                        md=10, lg=9, xl=8, align="center",style={ "margin-left":2, "margin-right":2 ,'margin-bottom':"50px"}),
                    navbar_A
                ],
                align="center",
                justify="center",
                style={"min-height": "95vh", 'verticalAlign': 'center'}
            )
        ]
    )

    return protected_content

###########################
####### User status #######
###########################

@dashapp.callback(
    Output('status-current-feedback', 'children'),
    Input('opt-status-emails', 'value'),
    prevent_initial_call=True
    )
def status_current(emails):
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
def status_activate(n_clicks, emails):
    if not emails :
        return dbc.Alert( "Please select a user." ,color="warning", style=alert_short_style,  dismissable=True)
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
def status_deactivate(n_clicks, reason, emails):
    if not emails :
        return None, dbc.Alert( "Please select a user." ,color="warning", style=alert_short_style,dismissable=True)
    if not reason :
        return None, dbc.Alert( "Please give in a reason." ,color="warning", style=alert_short_style,dismissable=True)
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



##############################
####### Private routes #######
##############################

@dashapp.callback(
    Output('routes-add-button', 'disabled'),
    Input('routes-domain-text', 'value'),
)
def routes_toggle_add_domain_btn(value):
    if value :
        return False
    else:
        return True

@dashapp.callback(
    Output('routes-rm-button', 'disabled'),
    Input('opt-routes-domains', 'value'),
)
def routes_toggle_rm_domain_btn(value):
    if value :
        return False
    else:
        return True

@dashapp.callback(
    Output('routes-list-button', 'disabled'),
    Output('opt-routes-no-access', 'options'),
    Output('opt-routes-no-access', 'placeholder'),
    Output('opt-routes-access', 'options'),
    Output('opt-routes-access', 'placeholder'),
    Output('opt-routes-no-access', 'value'),
    Output('opt-routes-access', 'value'),
    Output('opt-routes-domains', 'options'),
    Output('opt-routes-domains', 'value'),
    Output('opt-routes-domains', 'placeholder'),
    Output('routes-domain-text', 'placeholder'),
    Output('routes-domain-text', 'value'),
    Input('opt-routes-priv-routes', 'value')    )
def routes_read_priv_routes(route):

    if not route:
        empty_=make_options([])
        return True, empty_, "select a route first", empty_, "select a route first", None, None, empty_, None, "select a route first", "select a route first", None
    
    route_obj=PrivateRoutes.query.filter_by(route=route).first()
    if not route_obj :
        emails= [ u.email for u in User.query.all() ]
        emails.sort()
        emails=make_options(emails)
        empty_=make_options([])

        return True, emails, "select user", empty_, "no users here", None, None, empty_, None, "no domains here", "add domain, eg. gmail.com",  None

    if not route_obj.users_domains :
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

        if route_obj.users_domains:
            list_btn=False
        else:
            list_btn=True

        return list_btn, emails, "select user", empty_, "no users here", None, None, users_domains, users_domains_value, users_domains_placeholder, "add domain, eg. gmail.com", None

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
    Output('opt-routes-priv-routes', 'value'),
    Output('routes-feedback', 'children'),
    Output('routes-list-button',"n_clicks"),
    Output('routes-grant-button',"n_clicks"),
    Output('routes-revoke-button',"n_clicks"),
    Output('routes-add-button',"n_clicks"),
    Output('routes-rm-button',"n_clicks"),
    Input('routes-list-button',"n_clicks"),
    Input('routes-grant-button',"n_clicks"),
    Input('routes-revoke-button',"n_clicks"),
    Input('routes-add-button',"n_clicks"),
    Input('routes-rm-button',"n_clicks"),
    State('opt-routes-priv-routes', 'value'),
    State('opt-routes-no-access', 'value'),
    State('opt-routes-access', 'value'),
    State('routes-domain-text', 'value'),
    State('opt-routes-domains', 'value'),
    prevent_initial_call=True
    )
def routes_change_btns(l_clicks, g_clicks, r_clicks, add_domain_clicks, rm_domain_clicks ,route, grant_emails, revoke_emails, domain, domains_out ):
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
        msg=dbc.Alert( msg ,color="primary", style=alert_short_style,  dismissable=True)

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
            print("--",user_apps)
            if not user_apps:
                print("--NOT")
                user_apps=[route_obj.id]
            u.user_apps=list(set(user_apps))
            db.session.add(u)
            db.session.commit()
            users_ids.append(u.id)
        route_obj.users=users_ids
        db.session.add(route_obj)
        db.session.commit()

        msg=f'''{route}: {", ".join(grant_emails)}\nGranted!'''

        msg=dbc.Alert( msg ,color="success", style=alert_short_style,  dismissable=True)

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
        route_obj.users_domains=list(set(domains))
        db.session.add(route_obj)
        db.session.commit()

        msg=f'''{route}: {domain}\nGranted!'''

        msg=dbc.Alert( msg ,color="success", style=alert_short_style,  dismissable=True)

        return None, msg, 0, 0, 0, 0, 0

    if rm_domain_clicks == 1:
        route_obj=PrivateRoutes.query.filter_by(route=route).first()
        domains=route_obj.users_domains
        domains=[s for s in domains if s not in domains_out ]
        route_obj.users_domains=domains
        db.session.add(route_obj)
        db.session.commit()

        msg=f'''{route}: {", ".join(domains_out)}\nRemoved!'''

        msg=dbc.Alert( msg ,color="danger", style=alert_short_style,  dismissable=True)

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
        msg=dbc.Alert( msg ,color="danger", style=alert_short_style,  dismissable=True)

        return None, msg, 0, 0, 0, 0, 0
            
@dashapp.callback(
    Output('routes-grant-button',"disabled"),
    Input('opt-routes-no-access','value')  )
def routes_toggle_grant_btn(value):
    if value:
        return False
    else:
        return True

@dashapp.callback(
    Output('routes-revoke-button',"disabled"),
    Input('opt-routes-access','value') )
def routes_toggle_revoke_btn(value):
    if value:
        return False
    else:
        return True

##############################
####### Administrators #######
##############################

@dashapp.callback(
    Output('admin-grant-button', 'disabled'),
    Input('opt-admin-std-emails', 'value'),
    prevent_initial_call=True
    )
def admin_toggle_grant_btn(value):
    if value:
        return False
    else:
        return True

@dashapp.callback(
    Output('admin-revoke-button', 'disabled'),
    Input('opt-admin-emails', 'value'),
    prevent_initial_call=True
    )
def admin_toggle_revoke_btn(value):
    if value:
        return False
    else:
        return True

@dashapp.callback(
    Output('opt-admin-emails', 'options'),
    Output('opt-admin-std-emails', 'options'),
    Output('admin-grant-button', 'n_clicks'),
    Output('admin-revoke-button', 'n_clicks'),
    Output('opt-admin-emails', 'value'),
    Output('opt-admin-std-emails', 'value'),
    Output('admin-feedback', 'children'),
    Input('admin-grant-button', 'n_clicks'),
    Input('admin-revoke-button', 'n_clicks'),
    State('opt-admin-emails', 'value'),
    State('opt-admin-std-emails', 'value'),
    prevent_initial_call=True
    )
def admin_change_btns(mk_clicks,rm_clicks,admin_emails, non_admin_emails):
    if mk_clicks == 1:
        for email in non_admin_emails:
            user=User.query.filter_by(email=email).first()
            user.administrator=True
            db.session.add(user)
            db.session.commit()
        msg="Granted: "+", ".join(non_admin_emails)
        msg=dbc.Alert( msg ,color="success",  dismissable=True,style=alert_short_style)
        mk_clicks=0
    if rm_clicks == 1:
        for email in admin_emails:
            user=User.query.filter_by(email=email).first()
            user.administrator=False
            db.session.add(user)
            db.session.commit()
        mk_clicks=0
        msg="Revoked: "+", ".join(admin_emails)
        msg=dbc.Alert( msg ,color="danger",  dismissable=True, style=alert_short_style)

    non_admin_emails= [ u.email for u in User.query.all() if not u.administrator ]
    non_admin_emails.sort()
    non_admin_emails=make_options(non_admin_emails)

    admin_emails= [ u.email for u in User.query.all() if u.administrator ]
    admin_emails.sort()
    admin_emails=make_options(admin_emails)

    return admin_emails, non_admin_emails, 0, 0, None, None, msg


##############################
########### Notify ###########
##############################

@dashapp.callback(
    Output('notify-feedback', 'children'),
    Input('notify-button', 'n_clicks'),
    prevent_initial_call=True
    )
def notify_users(n_clicks):
    emails= [ u.email for u in User.query.all() ]
    emails=", ".join(emails)
    return dbc.Alert( emails ,color="primary", style=alert_short_style,  dismissable=True)

@dashapp.callback(
    Output('notify-all-feedback', 'children'),
    Input('notify-all-button', 'n_clicks'),
    prevent_initial_call=True
    )
def notify_all_users(n_clicks):
    emails= [ u.email for u in User.query.all() if u.notifyme ]
    emails=", ".join(emails)
    return dbc.Alert( emails ,color="warning", style=alert_short_style,  dismissable=True)

@dashapp.callback(
    Output("navbar-collapse", "is_open"),
    [Input("navbar-toggler", "n_clicks")],
    [State("navbar-collapse", "is_open")],
    )
def toggle_navbar_collapse(n, is_open):
    if n:
        return not is_open
    return is_open