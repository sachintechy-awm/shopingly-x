"""
Django settings for the ShopinglyX project.
"""
from pathlib import Path
from decouple import config

BASE_DIR = Path(__file__).resolve().parent.parent

# -----------------------------------------------------------------
# SECURITY
# -----------------------------------------------------------------
SECRET_KEY = config('SECRET_KEY', default='django-insecure-change-this-key-for-production-use-only')
DEBUG = config('DEBUG', default=True, cast=bool)
ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='127.0.0.1,localhost').split(',')

# -----------------------------------------------------------------
# APPLICATIONS
# -----------------------------------------------------------------
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # ShopinglyX
    'store',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'shopinglyx.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'store.context_processors.cart',
                'store.context_processors.categories',
            ],
        },
    },
]

WSGI_APPLICATION = 'shopinglyx.wsgi.application'

# -----------------------------------------------------------------
# DATABASE (SQLite - zero setup, perfect for running locally)
# -----------------------------------------------------------------
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# -----------------------------------------------------------------
# PASSWORD VALIDATION
# -----------------------------------------------------------------
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# -----------------------------------------------------------------
# INTERNATIONALIZATION
# -----------------------------------------------------------------
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Asia/Kolkata'
USE_I18N = True
USE_TZ = True

# -----------------------------------------------------------------
# STATIC & MEDIA FILES
# -----------------------------------------------------------------
STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

MEDIA_URL = 'media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# -----------------------------------------------------------------
# AUTH REDIRECTS
# -----------------------------------------------------------------
LOGIN_URL = 'store:login'
LOGIN_REDIRECT_URL = 'store:home'
LOGOUT_REDIRECT_URL = 'store:home'

# -----------------------------------------------------------------
# AI SHOPPING ASSISTANT (Gemini API)
# -----------------------------------------------------------------
# Powers the "Ask AI" search assistant in the header: a customer describes
# what they need in plain language and gets a friendly pointer to the right
# category plus matching product picks.
#
# 1. Get a free API key from https://aistudio.google.com/apikey
# 2. Put it in your .env file as GEMINI_API_KEY=your_key_here
# 3. `pip install google-genai` (already in requirements.txt)
#
# If left blank, the assistant still works — it falls back to keyword
# matching against the product catalog instead of calling the API, so the
# project runs and demos fine with zero external setup.
GEMINI_API_KEY = config('GEMINI_API_KEY', default='')
AI_MODEL = config('AI_MODEL', default='gemini-flash-latest')
