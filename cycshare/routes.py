from flask import render_template, Flask, Response, request, url_for, redirect, session, send_file, flash, jsonify
from cycshare import app
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

import pandas as pd
import os

# @app.route('/', methods=['GET', 'POST'])
# @app.route('/index', methods=['GET', 'POST'])
# def index():
#     return render_template('index.html')