from flask import Flask
from .config import app_config, Development, Production
from .models import db, bcrypt
from .views.UserViews import user_api as user_blueprint
from flask_migrate import Migrate

migrate = Migrate()

def create_app(env_name):
    """
    Create app
    """
  
    # app initiliazation
    app = Flask(__name__)
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    #VisualStudio was greying out the imported Development and Production classes. This if statement forces VS to register it
    env = app_config[env_name]
    if env is Development or env is Production:
        app.config.from_object(env)

    bcrypt.init_app(app)
    db.init_app(app)
    migrate.init_app(app, db)

    app.register_blueprint(user_blueprint, url_prefix='/api/v1/users')

    return app

