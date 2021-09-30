import re
from flask_login import login_required
import dash_bootstrap_components as dbc
import dash_html_components as html
from flaskapp import app
import base64

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
    [ dbc.NavItem( html.A(app.config['APP_TITLE'], style={"color":"gray","text-decoration": "none","textAlign":"right","margin-bottom":"25px","margin-top":"0px", "margin-right":"20px"},href="/index/")) ],
    fixed='bottom',
    color='white',
    expand="xs",
    # sticky ='bottom',
    style={"textAlign":"right" , "height":"50px"},
    # fluid=True
)


navbar_links={"Home":"/home/","About":"/about/","Impressum":"/impressum/","Privacy":"/privacy/","Settings":"/settings/","Logout":"/logout/"}
def make_navbar_logged(page_title, current_user, links=navbar_links, expand='sm'):
    if type(links) == dict:
        if current_user.administrator :
            if "Admin" not in list( links.keys() ):
                del(links["Logout"])
                links["Admin"]="/admin/"
                links["Logout"]="/logout/"
    
    if links:
        dropdown_children=[]
        for l in list( links.keys() ):
            dropdown_children.append( dbc.DropdownMenuItem(l, href=links[l], external_link=True) )

    else:
        dropdown=None

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
            href=app.config["APP_URL"]
        ),
        dbc.NavbarToggler(id="navbar-toggler", n_clicks=0),
        dbc.Collapse(
            dbc.Nav(
                [
                    dbc.DropdownMenu(
                        label=current_user.username,
                        children=dropdown_children,
                        className="mr-1",
                        nav=True,
                        in_navbar=True,
                        right=True
                    )
                ],
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

