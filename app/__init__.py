from flask import Flask
from flask_cors import CORS


def create_app():
    app = Flask(__name__)
    CORS(app)

    from .llm_api import llm_api
    app.register_blueprint(llm_api)
    return app
