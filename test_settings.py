DEBUG = True

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'testdb.sqlite',
    }
}

INSTALLED_APPS = ["lti_store"]
