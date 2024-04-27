#!/usr/bin/env python3
from project import create_app

app = create_app()
celery = app.extensions["celery"]
app.app_context().push()
