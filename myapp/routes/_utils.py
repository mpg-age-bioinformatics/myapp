import re
from flask_login import login_required
import dash_bootstrap_components as dbc
from dash import dcc, html
from myapp import app, PAGE_PREFIX  
import base64
from ._vars import user_navbar_links, other_nav_dropdowns, _PRIVATE_ROUTES, _PUBLIC_VIEWS, _META_TAGS
from myapp.models import PrivateRoutes

_PR = [ s for s in _PRIVATE_ROUTES if s not in _PUBLIC_VIEWS ]

META_TAGS=[{'name': 'viewport', 'content': 'width=device-width, initial-scale=1.0, maximum-scale=1.2, minimum-scale=0.5,'} ]

META_TAGS_=META_TAGS[0]
for k in list(_META_TAGS.keys()):
    META_TAGS_[k]=_META_TAGS[k]
META_TAGS[0]=META_TAGS_

regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'

def check_email(email):
    # pass the regular expression
    # and the string into the fullmatch() method
    if(re.fullmatch(regex, email)):
        return True
    else:
        return False

def password_check(password):
    """
    Verify the strength of 'password'
    Returns a dict indicating the wrong criteria
    A password is considered strong if:
        8 characters length or more
        1 digit or more
        1 symbol or more
        1 uppercase letter or more
        1 lowercase letter or more
    """

    # calculating the length
    length_error = len(password) < 8

    # searching for digits
    digit_error = re.search(r"\d", password) is None

    # searching for uppercase
    uppercase_error = re.search(r"[A-Z]", password) is None

    # searching for lowercase
    lowercase_error = re.search(r"[a-z]", password) is None

    # searching for symbols
    symbol_error = re.search(r"[ !#$%&'()*+,-./[\\\]^_`{|}~"+r'"]', password) is None

    # overall result
    password_ok = not ( length_error or digit_error or uppercase_error or lowercase_error or symbol_error )

    if length_error or digit_error :
        pass_type="weak"
    elif uppercase_error or lowercase_error or symbol_error:
        pass_type="medium"
    else:
        pass_type="strong"   

    return {
        'password_ok' : password_ok,
        'length_error' : length_error,
        'digit_error' : digit_error,
        'uppercase_error' : uppercase_error,
        'lowercase_error' : lowercase_error,
        'symbol_error' : symbol_error,
        'passtype' : pass_type
    }

def protect_dashviews(dashapp):
    for view_func in dashapp.server.view_functions:
        if view_func.startswith(dashapp.config.url_base_pathname):
            dashapp.server.view_functions[view_func] = login_required(
                dashapp.server.view_functions[view_func])

def make_options(valuesin):
    opts=[]
    for c in valuesin:
        opts.append( {"label":c, "value":c} )
    return opts

navbar_A = dbc.NavbarSimple(
    [ 
        dbc.NavItem( 
            html.A(
                app.config['APP_TITLE'], 
                target='_blank',
                style={"color":"gray","text-decoration": "none","textAlign":"right","margin-bottom":"25px","margin-top":"0px", "margin-right":"20px"},
                href=f"{PAGE_PREFIX}/index/"
            )
        ) 
    ],
    fixed='bottom',
    color='white',
    expand=True, #"xs",
    # sticky ='bottom',
    style={"textAlign":"right" , "height":"50px"},
    # fluid=True
)

def make_nav_dropdown(nav_dic, label):
    dropdown_children=[]
    for l in list( nav_dic.keys() ):
        if nav_dic[l] == "-":
            dropdown_children.append( dbc.DropdownMenuItem(divider=True) )
        elif nav_dic[l] == "__title__":
            dropdown_children.append( dbc.DropdownMenuItem(l, header=True) ),
        else:
            l_=nav_dic[l]
            if "http" in l_ :
                dropdown_children.append( dbc.DropdownMenuItem(l, href=f"{l_}", target='_blank', external_link=True) )
            else:
                dropdown_children.append( dbc.DropdownMenuItem(l, href=f"{PAGE_PREFIX}{l_}", target='_blank', external_link=True, ) )

    dd=dbc.DropdownMenu(
        label=label,
        children=dropdown_children,
        className="mr-1",#"mb-3",
        nav=True,
        in_navbar=True,
        align_end=True,
        # style={"optionHeight":"280px"}#,'overflow-y': 'auto'}
        # style={'max-height': '280px','overflow-y': 'auto'} #,'overflow-y': 'auto'}
        # style={"white-space": "nowrap", "overflow": "scroll", "text-overflow": "ellipsis"}
        #optionHeight=280
        # style={'height': '280px','overflow-y': 'auto'}
    )

    return [ dd ]

def make_navbar_logged(page_title, current_user, other_dropdowns=other_nav_dropdowns, user_links=user_navbar_links, expand='sm'):
    if type(user_links) == dict:
        user_links_=user_links.copy()
        if current_user.administrator :
            if "Admin" not in list( user_links.keys() ):
                del( user_links_["fixed_separator_2"] )
                del( user_links_["Logout"] )
                user_links_["Admin"]=f"/admin/"
                user_links_["fixed_separator_2"]="-"
                user_links_["Logout"]=f"/logout/"
        user_drop_down=make_nav_dropdown(user_links_,current_user.username)
    else:
        user_drop_down=make_nav_dropdown(user_links,current_user.username)

    other_dd=[]
    for o in other_dropdowns :
        label= list(o.keys())[0]
        dd_links_=o[label]

        dd_links={}
        for l in list(dd_links_.keys() ):
            app_route=dd_links_[l].split("/")[1]
            if app_route in _PR :
                route_obj=PrivateRoutes.query.filter_by(route=app_route).first()
                if not route_obj :
                    continue

                users=route_obj.users
                if not users :
                    continue

                uid=current_user.id
                if uid not in users :
                    udomains=route_obj.users_domains
                    if not udomains:
                        continue
                    if current_user.domain not in udomains :
                        continue

            l_=dd_links_[l]
            dd_links[l]=f"{l_}"

        previous_dd=make_nav_dropdown(dd_links,label)
        other_dd=other_dd+previous_dd

    dropdowns=other_dd+user_drop_down

    dd=dbc.Row(
        [
            dbc.Col(
                [
                    dbc.Nav(
                        dropdowns,
                        navbar=True,
                        className="ms-2"
                    ),
                ]
            )
        ],
        className="ms-auto g-0", #flex-nowrap mt-3 mt-md-0"
        align="center",
    )

    image_filename = f'{app.config["APP_ASSETS"]}logo.png' # replace with your own image
    encoded_image = base64.b64encode(open(image_filename, 'rb').read())
    img=html.Img(src='data:image/png;base64,{}'.format(encoded_image.decode()), height="30px")
    navbar = dbc.Navbar(
        dbc.Container(
            [
                html.A(
                    # Use row and col to control vertical alignment of logo / brand
                    dbc.Row(
                        [
                            dbc.Col(img),
                            dbc.Col(dbc.NavbarBrand(page_title, className="ms-2")),
                        ],
                        align="center",
                        className="g-0",
                    ),
                    href=f'{app.config["APP_URL"]}/home/',
                    target='_blank',
                    style={"textDecoration": "none"},
                ),
                dbc.NavbarToggler(id="navbar-toggler", n_clicks=0),
                dbc.Collapse(
                    dd,
                    id="navbar-collapse",
                    is_open=False,
                    navbar=True,
                ),
            ],fluid=True
        ),
        color="light",
        sticky="top",
        expand=expand,
        # style={"overflow":"auto"}
        
    )

    return navbar


