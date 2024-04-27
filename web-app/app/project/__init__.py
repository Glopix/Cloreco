from flask import Flask
from flask_sse import sse
from celery import Celery, Task
import os
from project.views import main
from project.utils.startup import validate_config_templates, check_data_directory


def celery_init_app(app: Flask) -> Celery:
    class FlaskTask(Task):
        def __call__(self, *args: object, **kwargs: object) -> object:
            with app.app_context():
                return self.run(*args, **kwargs)

    celery_app = Celery(app.name, task_cls=FlaskTask)
    celery_app.config_from_object(app.config["CELERY"])
    celery_app.set_default()
    app.extensions["celery"] = celery_app
    return celery_app

def create_app() -> Flask:
    app = Flask(__name__)

    # set Celery settings from env vars
    app.config.from_mapping(
        CELERY=dict(
            broker_url =        os.getenv('CELERY_BROKER_URL'),
            result_backend =    os.getenv('CELERY_RESULT_BACKEND'),
            task_ignore_result=True,
        ),
    )   

    app.config['SECRET_KEY'] = os.urandom(32)

    # set Celery settings from env vars
    app.config.from_prefixed_env()

    celery_init_app(app)

    app.register_blueprint(main)
    app.register_blueprint(sse, url_prefix='/stream')

    check_data_directory()
    validate_config_templates()

    return app
