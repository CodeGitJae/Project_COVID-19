from flask import Flask

def create_app():
    app = Flask(__name__)

    from .views import main_views
    app.register_blueprint(main_views.bp)

    from .views import chart_views
    app.register_blueprint(chart_views.bp)

    from .views import world_views
    app.register_blueprint(world_views.bp)

    return app