import re
from myapp import app
from flask_login import current_user
from flask_caching import Cache
import dash
from dash.dependencies import Input, Output, State
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
import uuid
from werkzeug.utils import secure_filename
import json
from flask import session
import base64

import pandas as pd
import os

META_TAGS=[{'name': 'viewport', 'content': 'width=device-width, initial-scale=1.0, maximum-scale=1.2, minimum-scale=0.5,'} ]

dashapp = dash.Dash("index",url_base_pathname='/', meta_tags=META_TAGS, server=app, external_stylesheets=[dbc.themes.BOOTSTRAP], title=app.config["APP_TITLE"], assets_folder=app.config["APP_ASSETS"])# , assets_folder="/flaski/flaski/static/dash/")
# protect_dashviews(dashapp)

# cache = Cache(dashapp.server, config={
#     'CACHE_TYPE': 'redis',
#     'CACHE_REDIS_URL': 'redis://:%s@%s' %( os.environ.get('REDIS_PASSWORD'), os.environ.get('REDIS_ADDRESS') )  #'redis://localhost:6379'),
# })

image_filename = f'{app.config["APP_ASSETS"]}logo.png' # replace with your own image
encoded_image = base64.b64encode(open(image_filename, 'rb').read())

dashapp.layout=html.Div( [ dcc.Location(id='url', refresh=False), html.Div(id="page-content") ] )

logged_children=[]
nonlogged_children=[]

@dashapp.callback(
    Output('page-content', 'children'),
    Input('url', 'pathname'))
def make_layout(pathname):

    links_style={"color":"#35443f", "margin-left":"12px", "margin-right":"12px", "font-weight": "bold","text-decoration": "none"}

    target=None

    if current_user :
        if current_user.is_authenticated :
            if current_user.active :
                target="/home/"
                open_content=html.Div(id="page-footer",style={"height":"10px"})
                refresh=True

    if not target:
        if pathname not in ['/index/open/', '/open/'] :
            target="/index/open/"
            open_content=html.Div(id="page-footer", style={"height":"10px"})
            refresh=False

        else :
            target="/index/"
            open_content=html.Div([
                            dbc.Row( 
                                html.Footer( [ 
                                    html.A("About", style=links_style, href="/about/"),
                                    html.A("Login", style=links_style, href="/login/"),
                                    html.A("Register", style=links_style, href="/register/"),
                                    html.A("Contact", style=links_style, href="/contact/")
                                ] , 
                                style={"margin-top": 25, "margin-bottom": 5,},
                                ),
                                style={"justify-content":"center"}
                            )
                        ],style={"height":"10px"})
            refresh=False


    page_content=html.Div(
        [
            dbc.Row(
                dbc.Col( 
                    [
                        dcc.Link(
                            [
                                html.Img( src='data:image/png;base64,{}'.format(encoded_image.decode() ) , height="300px", style={ "margin-bottom":5}),
                                html.H1(app.config["APP_TITLE"], style={"textAlign":"center"}),
                            ],
                            href=target,
                            refresh=refresh,
                            style={"color":"black","text-decoration": "none"}
                        ),
                        open_content
                    ], 
                    align="center",
                    style={"textAlign":"center"}
                ), 
                justify="center",
                style={"min-height": "100vh"}
            )
        ]
    )

    return page_content


# @dashapp.callback(
#         Output("navbar-collapse", "is_open"),
#         [Input("navbar-toggler", "n_clicks")],
#         [State("navbar-collapse", "is_open")])
# def toggle_navbar_collapse(n, is_open):
#     if n:
#         return not is_open
#     return is_open

