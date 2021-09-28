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

dashapp = dash.Dash("privacy",url_base_pathname='/privacy/', meta_tags=META_TAGS, server=app, external_stylesheets=[dbc.themes.BOOTSTRAP], title=app.config["APP_TITLE"], assets_folder=app.config["APP_ASSETS"])# , assets_folder="/{APP_TITLE}/{APP_TITLE}/static/dash/")

APP_TITLE=app.config["APP_TITLE"]

gdpr_text=dcc.Markdown(f'''
Thanks for entrusting {APP_TITLE} with your data. Holding on to your private information is a serious responsibility, and we want you to know how we're handling it.

The entity  responsible for the processing of your personal information in connection with the services is <CONTACT>.

The Data Protection Officer at the entity responsible is <NAME>, <CONTACT>

**What personal data {APP_TITLE} collects**

{APP_TITLE} collects your first name, last name, organization name, and email address. Additionally, {APP_TITLE} collects email and time stamps on performed actions 
like figure download or login to an app.

**What personal data {APP_TITLE} does not collect**

{APP_TITLE} does not collect your input data. You can store your data in our servers but we generally will not look into it other than stated below.

**How {APP_TITLE} collets information**

Every time you visit an App (or eg. download a figure or an error occurs) a timestamp, App, and user email contact is recorded in a MySQL/MariaDB 
which is accessible to {APP_TITLE}’s administrators only. 

**Why {APP_TITLE} collects your information**

{APP_TITLE} is an open source project supported by the private and work time of it’s developers. In order to continuously keep on 
improving {APP_TITLE} we might need to apply for funding. It is therefore important that we are able to demonstrate a concrete 
usage of {APP_TITLE} and from which institutions our usage originates so that we can choose the appropriate funding organizations.

**How {APP_TITLE} uses your information**

We collect usage statistics to better understand our Apps and develop them further for you.

**How we share the information we collect**

When reporting usage statistics we deplete user's first name, last name, and email from that report. We might include 
organizations names in such reports. We do not share any users account with any other public or private organization. 

**How you can access the information we collect**

If you want to permanently remove all traces of your account from our data bank please mail us from your user's email 
address to <EMAIL>.

**Our use of cookies and tracking**

{APP_TITLE} only uses minimal functionality cookies so that your input data does not vanish every time you press 
“Submit” or refresh the page. {APP_TITLE}'s minimal functionality cookies only collect the values that you input 
into an App (eg. range of x-axis) so that the instructions you give to {APP_TITLE} can be executed. Session cookies 
are permanently cleared every time you logout. {APP_TITLE} does not perform tracking. Cookies are text files stored 
in the Internet browser or by the Internet browser on the user's computer system.

**How {APP_TITLE} secures your information**

We take all measures reasonably necessary to protect the confidentiality, integrity, and availability of your 
personal information on {APP_TITLE} and to protect the resilience of our servers.

{APP_TITLE} takes all measures reasonably necessary to protect User Personal Information from unauthorized access, 
alteration, or destruction; maintain data accuracy; and help ensure the appropriate use of User Personal Information.

{APP_TITLE} enforces a written security information program. Our program:

- aligns with industry recognized frameworks;
- includes security safeguards reasonably designed to protect the confidentiality, integrity, availability, and resilience of our Users' data;
- is appropriate to the nature, size, and complexity of {APP_TITLE}'s business operations;
- includes incident response and data breach notification processes.

In the event of a data breach that affects your User Personal Information, we will act promptly to mitigate the 
impact of a breach and notify any affected Users without undue delay.

Transmission of data on {APP_TITLE} is encrypted using SSH, HTTPS (TLS). We manage our own cages and racks at our own 
data centers with high level of physical and network security.

No method of transmission, or method of electronic storage, is 100% secure. Therefore, we cannot guarantee its absolute security.

{APP_TITLE}, the <ORGANIZATION>, and it's personnel can not be hold be responsible for the 
misusage for {APP_TITLE} servers by a third-party as it would be the case of for example an hacking event.

**Other important information**

*Data storage*

{APP_TITLE} personnel do not access private repositories unless required to for security purposes, to assist the repository owner 
with a support matter, to maintain the integrity of the service, or to comply with our legal obligations. However, 
while we do not generally search for content in your repositories, we may scan our servers and content to detect certain tokens 
or security signatures, known active malware, or other content such as violent extremist or terrorist content or child 
exploitation imagery, based on algorithmic fingerprinting techniques.

{APP_TITLE} regularly scans it's servers for old, untouched data and marks it for deletion. Users are informed of this mark and 
are given time to properly backup their data.

Personal data will be deleted too if you ask us to delete it or either above purposes are achieved. Data will be delete once it 
reaches an age of 10 years.

*Data analysis*

{APP_TITLE} purpose is to support researchers on the analysis of their data. For this we constantly enhance the number and quality 
of our app promptly responding to user's requests. {APP_TITLE}, the <ORGANIZATION>, and it's personnel 
can not be hold responsible for any data analysis performed with {APP_TITLE} nor for any misinterpretation that might come from an 
undesirable or misunderstood function. {APP_TITLE}'s code is public and open source and we encourage all users to follow it's code 
as a trace to their analysis.   

*What are my rights as a data subject?*

As an individual whose personal data is gathered as part of the aforementioned services, you have, in principle, the following 
rights, to the extent that no legal exceptions are applicable in individual cases:

- Information (Article 15 GDPR)
- Correction (Article 16 GDPR)
- Deletion (Article 17 (1) GDPR)
- Restriction of processing (Article 18 GDPR)
- Data transmission (Article 20 GDPR)
- Revocation of processing (Article 21 GDPR)
- Revocation of consent (Article 7 (3) GDPR)
- Right to complain to the regulator (Article 77 GDPR).

**Contacting {APP_TITLE}**

Please feel free to contact us if you have questions about our Privacy and Data Statement. Contact details:

<CONTACT>

''')

dashapp.layout=dbc.Row(
                    [ dbc.Col( 
                        [ html.H1("DATA AND PRIVACY", style={"textAlign":"center", "margin-bottom":"30px"}), gdpr_text ],  # 
                        align="top", 
                        style={"textAlign":"justify",'margin-left':"15px", 'margin-right':"15px","margin-top":"100px", 'margin-bottom':"50px"},
                        md=9, lg=7, xl=5), 
                    navbar_A ] ,
                    justify="center")