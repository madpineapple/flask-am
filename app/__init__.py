from flask import Flask

def create_app():
    app = Flask(__name__)
    
    from .llm_api import llm_api
    app.register_blueprint(llm_api)
    return app
