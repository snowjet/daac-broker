from functools import wraps
import json
from os import environ as env
from werkzeug.exceptions import HTTPException

from dotenv import load_dotenv, find_dotenv
from flask import Flask
from flask import jsonify
from flask import redirect
from flask import render_template
from flask import session
from flask import url_for
from authlib.flask.client import OAuth
from six.moves.urllib.parse import urlencode

from flask_bootstrap import Bootstrap

from core.config import auth0_config, LOG_LEVEL
from api.auth0 import create_auth0_blueprint
from api.admin import admin_blueprint
from api.users import users_blueprint

if LOG_LEVEL == "DEBUG":
    DEBUG = True
else:
    DEBUG = False

app = Flask(__name__)
app.secret_key = auth0_config["SECRET_KEY"]
app.config['BOOTSTRAP_SERVE_LOCAL'] = False

bootstrap = Bootstrap(app)

oauth = OAuth(app)

auth0_blueprint = create_auth0_blueprint(oauth)
app.register_blueprint(auth0_blueprint)
app.register_blueprint(admin_blueprint)
app.register_blueprint(users_blueprint)

@app.route("/")
def home():
    return render_template("home.html")


if __name__ == '__main__':
    app.run(debug=DEBUG, host='0.0.0.0')