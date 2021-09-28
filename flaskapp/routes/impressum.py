from flaskapp import app, db
import dash
from dash.dependencies import Input, Output, State
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from flaskapp.models import User
from flaskapp.email import send_validate_email
from datetime import datetime
from ._utils import META_TAGS, check_email, password_check, navbar_A
from flask_login import current_user

dashapp = dash.Dash("impressum",url_base_pathname='/impressum/', meta_tags=META_TAGS, server=app, external_stylesheets=[dbc.themes.BOOTSTRAP], title=app.config["APP_TITLE"], assets_folder=app.config["APP_ASSETS"])# , assets_folder="/{APP_TITLE}/{APP_TITLE}/static/dash/")

APP_TITLE=app.config["APP_TITLE"]

gdpr_text=dcc.Markdown(f'''
#### 1. Terms

By accessing this Website, accessible from {app.config["APP_URL"]}, you are agreeing to be bound by these Website Terms 
and Conditions of Use and agree that you are responsible for the agreement with any applicable local laws. 
If you disagree with any of these terms, you are prohibited from accessing this site. The materials contained in 
this Website are protected by copyright and trade mark law.

#### 2. Use License

Permission is granted to temporarily download one copy of the materials on {APP_TITLE}'s Website for personal, 
non-commercial transitory viewing only. This is the grant of a license, not a transfer of title, and under this license you may not:

- modify or copy the materials;
- use the materials for any commercial purpose or for any public display;
- attempt to reverse engineer any software contained on {APP_TITLE}'s Website;
- remove any copyright or other proprietary notations from the materials; or
- transferring the materials to another person or "mirror" the materials on any other server.

This will let {APP_TITLE} to terminate upon violations of any of these restrictions. Upon termination, 
your viewing right will also be terminated and you should destroy any downloaded materials in your possession 
whether it is printed or electronic format. These Terms of Service has been created with the help of the 
[Terms Of Service Generator](https://www.termsofservicegenerator.net).

#### 3. Disclaimer

All the materials on {APP_TITLE} Website are provided "as is". {APP_TITLE} makes no warranties, may it be expressed 
or implied, therefore negates all other warranties. Furthermore, {APP_TITLE} does not make any representations concerning 
the accuracy or reliability of the use of the materials on its Website or otherwise relating to such materials or any sites linked to this Website.

#### 4. Limitations

{APP_TITLE} or its suppliers will not be hold accountable for any damages that will arise with the use or inability to use the 
materials on {APP_TITLE}’s Website, even if {APP_TITLE} or an authorize representative of this Website has been notified, 
orally or written, of the possibility of such damage. Some jurisdiction does not allow limitations on implied warranties 
or limitations of liability for incidental damages, these limitations may not apply to you.

#### 5. Revisions and Errata

The materials appearing on {APP_TITLE}'s Website may include technical, typographical, or photographic errors. 
{APP_TITLE} will not promise that any of the materials in this Website are accurate, complete, or current. 
{APP_TITLE} may change the materials contained on its Website at any time without notice. 
{APP_TITLE} does not make any commitment to update the materials.

#### 6. Links

{APP_TITLE} has not reviewed all of the sites linked to its Website and is not responsible for the contents of any such linked site. 
The presence of any link does not imply endorsement by {APP_TITLE} of the site. The use of any linked website is at the user’s own risk.

### 7. Site Terms of Use Modifications

{APP_TITLE} may revise these Terms of Use for its Website at any time without prior notice. 
By using this Website, you are agreeing to be bound by the current version of these Terms and Conditions of Use.

#### 8. Your Privacy

Please read our Privacy Policy on [{app.config["APP_URL"]}/privacy]({app.config["APP_URL"]}/privacy).

#### 9. Governing Law

Any claim related to {APP_TITLE}'s Website shall be governed by the laws of Germany without regards to its conflict of law provisions.

<NAME> <CONTACT>

''')

dashapp.layout=dbc.Row(
                    [ dbc.Col( 
                        [ html.H1("IMPRESSUM", style={"textAlign":"center", "margin-bottom":"30px"}), gdpr_text ],  # 
                        align="top", 
                        style={"textAlign":"justify",'margin-left':"15px", 'margin-right':"15px","margin-top":"100px", 'margin-bottom':"50px"},
                        md=9, lg=7, xl=5), 
                    navbar_A ] ,
                    justify="center")