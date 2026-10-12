from flask import Flask
from flask_cors import CORS
from config import Config
# from app.routes.simulation_routes import simulation_bp
# from app.routes.queueing_routes import queueing_bp


def create_app():

    app = Flask(__name__)

    app.config.from_object(Config)

    CORS(app)

    from app.routes.health_routes import health_bp
    from app.routes.dataset_routes import dataset_bp
    from app.routes.simulation_routes import simulation_bp
    from app.routes.queueing_routes import queueing_bp

    app.register_blueprint(
        health_bp,
        url_prefix="/api"
    )

    app.register_blueprint(
        dataset_bp,
        url_prefix="/api"
    )
    
    app.register_blueprint(
    simulation_bp,
    url_prefix="/api"
    )
    
    app.register_blueprint(
    queueing_bp,
    url_prefix="/api"
    )

    return app