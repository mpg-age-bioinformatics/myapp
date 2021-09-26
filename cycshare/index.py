import re
from flaski import app
from flask_login import current_user
from flask_caching import Cache
from flaski.routines import check_session_app
import dash
from dash.dependencies import Input, Output, State
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from ._utils import handle_dash_exception, parse_table, protect_dashviews, validate_user_access, \
    make_navbar, make_footer, make_options, make_table, META_TAGS, make_min_width, \
    change_table_minWidth, change_fig_minWidth
from ._aadatalake import read_results_files, read_gene_expression, read_genes, read_significant_genes, \
    filter_samples, filter_genes, filter_gene_expression, nFormat, read_dge,\
        make_volcano_plot, make_ma_plot, make_pca_plot, make_annotated_col
import uuid
from werkzeug.utils import secure_filename
import json
from flask import session

import pandas as pd
import os

META_TAGS=[{'name': 'viewport', 'content': 'width=device-width, initial-scale=1.0, maximum-scale=1.2, minimum-scale=0.5,'} ]


dashapp = dash.Dash("index",url_base_pathname=f'/index/' , meta_tags=META_TAGS, server=app, external_stylesheets=[dbc.themes.BOOTSTRAP], title="cycshare")# , assets_folder="/flaski/flaski/static/dash/")
# protect_dashviews(dashapp)

cache = Cache(dashapp.server, config={
    'CACHE_TYPE': 'redis',
    'CACHE_REDIS_URL': 'redis://:%s@%s' %( os.environ.get('REDIS_PASSWORD'), os.environ.get('REDIS_ADDRESS') )  #'redis://localhost:6379'),
})

dashapp.layout=html.Div(children=[html.H1(children='Hello Dash')])

@dashapp.callback(
        Output("navbar-collapse", "is_open"),
        [Input("navbar-toggler", "n_clicks")],
        [State("navbar-collapse", "is_open")])
def toggle_navbar_collapse(n, is_open):
    if n:
        return not is_open
    return is_open

