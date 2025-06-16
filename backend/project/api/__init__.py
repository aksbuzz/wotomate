from flask import Flask

def register_routes(app: Flask):
  from .routes.auth import auth_bp
  from .routes.connector import connector_bp

  app.register_blueprint(auth_bp, url_prefix='/api/v1/auth')
  app.register_blueprint(connector_bp, url_prefix='/api/v1/connectors')