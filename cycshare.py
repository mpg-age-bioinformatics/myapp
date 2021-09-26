from cycshare import app, db
from cycshare.models import User, UserLogging
import sys
import pandas as pd
import datetime

@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User}

if __name__ == "__main__":
    from cycshare import app
    import os, datetime