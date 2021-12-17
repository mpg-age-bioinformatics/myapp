import re
from flask_login import login_required
import dash_bootstrap_components as dbc
from dash import dcc, html
from myapp import app
import base64
from ._vars import user_navbar_links, other_nav_dropdowns

META_TAGS=[{'name': 'viewport', 'content': 'width=device-width, initial-scale=1.0, maximum-scale=1.2, minimum-scale=0.5,'} ]

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
                style={"color":"gray","text-decoration": "none","textAlign":"right","margin-bottom":"25px","margin-top":"0px", "margin-right":"20px"},
                href="/index/"
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
            dropdown_children.append( dbc.DropdownMenuItem(l, href=nav_dic[l], external_link=True) )

    dd=dbc.DropdownMenu(
        label=label,
        children=dropdown_children,
        className="mr-1",
        nav=True,
        in_navbar=True,
        right=True
    )

    return [ dd ]


def make_navbar_logged(page_title, current_user, other_dropdowns=other_nav_dropdowns, user_links=user_navbar_links, expand='sm'):
    if type(user_links) == dict:
        if current_user.administrator :
            if "Admin" not in list( user_links.keys() ):
                del( user_links["fixed_separator_2"] )
                del( user_links["Logout"] )
                user_links["Admin"]="/admin/"
                user_links["fixed_separator_2"]="-"
                user_links["Logout"]="/logout/"

    user_drop_down=make_nav_dropdown(user_links,current_user.username)

    other_dd=[]
    for o in other_dropdowns :
        label= list(o.keys())[0]
        dd_links=o[label]
        previous_dd=make_nav_dropdown(dd_links,label)
        other_dd=other_dd+previous_dd

    dropdowns=other_dd+user_drop_down


    # if user_links:
    #     dropdown_children=[]
    #     for l in list( user_links.keys() ):
    #         if user_links[l] == "-":
    #             dropdown_children.append( dbc.DropdownMenuItem(divider=True) )
    #         elif user_links[l] == "__title__":
    #             dropdown_children.append( dbc.DropdownMenuItem(l, header=True) ),
    #         else:
    #             dropdown_children.append( dbc.DropdownMenuItem(l, href=user_links[l], external_link=True) )


    # else:
    #     dropdown_children=[]

    image_filename = f'{app.config["APP_ASSETS"]}logo.png' # replace with your own image
    encoded_image = base64.b64encode(open(image_filename, 'rb').read())
    img=html.Img(src='data:image/png;base64,{}'.format(encoded_image.decode()), height="30px")
    navbar=dbc.Navbar(
        [
            html.A(
                # Use row and col to control vertical alignment of logo / brand
                dbc.Row(
                    [
                        dbc.Col(img),
                        dbc.Col(dbc.NavbarBrand(page_title, className="ml-2")),
                    ],
                    align="center",
                    no_gutters=True,
                ),
                href=f'{app.config["APP_URL"]}/home/'
            ),
        dbc.NavbarToggler(id="navbar-toggler", n_clicks=0),
        dbc.Collapse(
            dbc.Nav(
                dropdowns,
                navbar=True,
                className="ml-auto",
            ),
            id="navbar-collapse", navbar=True, is_open=False
        )
        ],
        color="light",
        # dark=True,
        sticky="top",
        # light=True
        expand=expand
    )

    return navbar

