DEBUG = True
TEMPLATE_DEBUG = DEBUG
ROOT_URLCONF = 'debppa.urls'

import os.path

TEMPLATE_DIRS = (
    os.path.join(os.path.dirname(__file__), 'templates'),
    )

DATABASE_ENGINE = "sqlite3"
DATABASE_NAME = "./database"

INSTALLED_APPS = (
        "django.contrib.auth",
        "django.contrib.contenttypes",
        "django.contrib.sessions",
        "django.contrib.sites",
        "django.contrib.admin",
        "debppa.ppa"
        )
