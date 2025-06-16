from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from celery import Celery, Task
from celery.schedules import crontab
from dotenv import load_dotenv
import os

load_dotenv()

db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()

from project.models import *

celery_app = Celery(__name__)

beat_schedule = {
    'poll_all_triggers_every_minute': {
        'task': 'project.tasks.poll_all_triggers_task',
        'schedule': crontab()
    }
}

def celery_init_app(app: Flask, celery: Celery) -> Celery:
    celery.conf.broker_url = app.config['CELERY_BROKER_URL']
    celery.conf.result_backend = app.config['CELERY_RESULT_BACKEND']
    celery.conf.update(app.config)
    celery.conf.beat_schedule = beat_schedule
    
    class ContextTask(Task):
        abstract = True
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)
    
    celery.Task = ContextTask
    celery.autodiscover_tasks(['project'])
    return celery

def create_app() -> Flask:
    app = Flask(__name__)

    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
    app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY')
    app.config['CELERY_BROKER_URL'] = os.getenv('CELERY_BROKER_URL')
    app.config['CELERY_RESULT_BACKEND' ]= os.getenv('CELERY_RESULT_BACKEND')

    CORS(app)
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)

    celery_init_app(app, celery_app)

    # from .auth.routes import auth_bp
    from .api.routes.system import system_bp
    from .api.routes.auth import auth_bp
    from .api.routes.connector import connector_bp
    from .api.routes.workflow import workflow_bp
    from .connectors.github.route import github_auth_bp
    from .connectors.slack.route import slack_auth_bp
    from .connectors.trello.route import trello_auth_bp
    # from .workflow.webhook_routes import webhook_bp
    # from .connector.routes import connector_bp

    app.register_blueprint(system_bp, url_prefix="/")
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(workflow_bp, url_prefix='/api/workflows')
    app.register_blueprint(connector_bp, url_prefix='/api/connectors')
    # app.register_blueprint(webhook_bp, url_prefix='/api/webhooks')
    app.register_blueprint(github_auth_bp, url_prefix='/api/connection/github')
    app.register_blueprint(slack_auth_bp, url_prefix='/api/connection/slack')
    app.register_blueprint(trello_auth_bp, url_prefix='/api/connection/trello')

    return app