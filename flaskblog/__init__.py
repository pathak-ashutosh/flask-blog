import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_mail import Mail
from flaskblog.config import Config

## Extensions of the app:
# these extensions are not bound to the create_app function because we don't want the extensions to be confined
# to a particular instance of the app. We want all the instances to use the same extensions.
# Here we're initialising the extensions without passing app as argument because we'll do that in create_app func
db = SQLAlchemy()
bcrypt = Bcrypt()
login_manager = LoginManager()
login_manager.login_view = 'users.login'            # telling login_manager that we should login from 'login' function
                                                    # if we try to access a page which is meant for authenticated (logged in)
                                                    # user only
login_manager.login_message_category = 'info'       # using bootstrap class 'info' to show the login message
mail = Mail()


# moving our application into a function gives the ability to run different instances of the application
# with different configurations
def create_app(config_class = Config):
    # creation of the app:
    app = Flask(__name__)
    app.config.from_object(Config)
    # initialising the extensions:
    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)

    # imported at the end to avoid circular import
    from flaskblog.users.routes import users        # importing users blueprint
    from flaskblog.posts.routes import posts        # importing posts blueprint
    from flaskblog.main.routes import main          # importing main blueprint
    from flaskblog.errors.handlers import errors    # importing errors blueprint
    # registering blueprints to the app:
    app.register_blueprint(users)
    app.register_blueprint(posts)
    app.register_blueprint(main)
    app.register_blueprint(errors)

    return app