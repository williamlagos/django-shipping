DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }
}
INSTALLED_APPS = [
    "django.contrib.contenttypes",
    "django.contrib.auth",
    "django.contrib.sessions",
    "shipping",
]
MIDDLEWARE = [
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
]
DEFAULT_AUTO_FIELD = "django.db.models.AutoField"
ROOT_URLCONF = "shipping.urls"
SECRET_KEY = "test-secret-key-not-for-production"
SESSION_ENGINE = "django.contrib.sessions.backends.db"
