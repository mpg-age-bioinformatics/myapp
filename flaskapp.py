from flaskapp import app, db
from flaskapp.models import User, UserLogging
import pandas as pd

@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User}

if __name__ == "__main__":
    from flaskapp import app
    import os, datetime