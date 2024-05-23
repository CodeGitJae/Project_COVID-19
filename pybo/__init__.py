from flask import Flask

from .views import citygungu_views

def create_app():
    app = Flask(__name__)

    from .views import main_views

    app.register_blueprint(main_views.bp)
    app.register_blueprint(citygungu_views.bp)

    return app