import re
from myapp import app, PAGE_PREFIX
from flask_login import current_user
from flask_caching import Cache
import dash
from dash.dependencies import Input, Output, State
from dash import dcc, html
import dash_bootstrap_components as dbc
import uuid
from werkzeug.utils import secure_filename
import json
from flask import session
import base64
from ._utils import navbar_A


import pandas as pd
import os

META_TAGS=[{'name': 'viewport', 'content': 'width=device-width, initial-scale=1.0, maximum-scale=1.2, minimum-scale=0.5,'} ]

dashapp = dash.Dash("ext", url_base_pathname=f"{PAGE_PREFIX}/ext/", meta_tags=META_TAGS, server=app, external_stylesheets=[dbc.themes.BOOTSTRAP], title=app.config["APP_TITLE"], assets_folder=app.config["APP_ASSETS"])# , assets_folder="/flaski/flaski/static/dash/")

image_filename = f'{app.config["APP_ASSETS"]}logo.png' # replace with your own image
encoded_image = base64.b64encode(open(image_filename, 'rb').read())

dashapp.layout=html.Div( [ dcc.Location(id='url', refresh=False), html.Div(id="page-content") ] )

# logged_children=[]
# nonlogged_children=[]

@dashapp.callback(
    Output('page-content', 'children'),
    Input('url', 'pathname'))
def make_layout(pathname):

    links_style={"color":"#35443f", "margin-left":"12px", "margin-right":"12px", "font-weight": "bold","text-decoration": "none"}

    target=pathname.split(f"{PAGE_PREFIX}/ext/")[-1]
    target=f'https://{target}'

    app_title=app.config["APP_TITLE"]

    page_content=html.Div(
        [
            dbc.Row(
                [

                
                    dbc.Col( 
                        [
                            dcc.Link(
                                [
                                    # html.Img( src='data:image/png;base64,{}'.format(encoded_image.decode() ) , height="300px", style={ "margin-bottom":5}),
                                    html.H3([ f"You are leaving {app_title} and being redirected to:",\
                                        html.Br(),\
                                        html.Br(),\
                                        target,\
                                        html.Br(),\
                                        html.Br(),\
                                        "Click here to continue."], 
                                        style={"textAlign":"center","overflow-wrap": "break-word"}),
                                ],
                                href=target,
                                refresh=True,
                                style={"color":"black","text-decoration": "none"}                        
                                ),
                        ], 
                        sm=9,md=7, lg=5, xl=5, 
                        align="center",
                        style={"textAlign":"center", "height": "100%" },
                    ),
                    navbar_A,
                ],
                justify="center",
                style={"min-height": "100vh", "margin-bottom":"0px","margin-left":"5px","margin-right":"5px"}
            )
        ]
    )

    return page_content


@dashapp.callback(
        Output("navbar-collapse", "is_open"),
        [Input("navbar-toggler", "n_clicks")],
        [State("navbar-collapse", "is_open")])
def toggle_navbar_collapse(n, is_open):
    if n:
        return not is_open
    return is_open

