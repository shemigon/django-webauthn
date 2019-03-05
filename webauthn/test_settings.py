import os

TEST_DIR = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'tests')

SECRET_KEY = '8q$p@8b$mbn$#7y)q2_dst^r-0l3d_ela!o413hka+#be$kc62'

INSTALLED_APPS = [
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'webauthn',
]

MIDDLEWARE = [
    'django.contrib.sessions.middleware.SessionMiddleware',
]
SESSION_SERIALIZER = 'django.contrib.sessions.serializers.PickleSerializer'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(TEST_DIR, 'db.sqlite3'),
    }
}

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True
