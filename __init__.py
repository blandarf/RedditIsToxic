from flask import Flask

from decouple import config

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'secretkey123'

    from views import views
    app.register_blueprint(views, url_prefix='/')
    return app






