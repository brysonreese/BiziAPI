from flask import Flask
from flask_mail import Mail
from sqlalchemy import true
from .config import app_config, Development, Production
from .models import db, bcrypt
from .views.UserViews import user_api as user_blueprint
from .views.HouseholdViews import household_api as household_blueprint
from flask_migrate import Migrate
from flask_cors import CORS
import os

migrate = Migrate()

def create_app():
    """
    Create app
    """
    env_name = os.getenv('FLASK_ENV')
    # app initiliazation
    app = Flask(__name__)
    CORS(app)

    #VisualStudio was greying out the imported Development and Production classes. This if statement forces VS to register it
    env = app_config[env_name]
    if env is Development or env is Production:
        app.config.from_object(env)

    bcrypt.init_app(app)
    db.init_app(app)
    migrate.init_app(app, db)

    app.register_blueprint(user_blueprint, url_prefix='/api/v1/users')
    app.register_blueprint(household_blueprint, url_prefix='/api/v1/households')

    return app

