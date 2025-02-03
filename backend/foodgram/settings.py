from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = 'django-insecure-6a+c_r2r==$n*j)642((7ppa5(exm376-32b=4dte8w2oer04j'

DEBUG = True

ALLOWED_HOSTS = ['localhost', '127.0.0.1', 'testserver']

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'djoser',
    'rest_framework',
    'rest_framework.authtoken',
    'corsheaders',
    'recipes.apps.RecipesConfig',]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',

    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',]

ROOT_URLCONF = 'foodgram.urls'

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
            ],
        },
    },
]

WSGI_APPLICATION = 'foodgram.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True

STATIC_URL = '/static/'
STATIC_ROOT = '/app/collected_static/'
# STATIC_ROOT = os.path.join(BASE_DIR, 'collected_static')

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

LOGIN_URL = 'users:login'
LOGIN_REDIRECT_URL = 'recipes:index'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        # 'rest_framework.permissions.IsAuthenticated',
        'rest_framework.permissions.AllowAny',
    ],
    'DEFAULT_RENDERER_CLASSES': (
        'rest_framework.renderers.JSONRenderer',  # Только JSON
    ),

    'DEFAULT_PARSER_CLASSES': [
        'rest_framework.parsers.JSONParser',
        'rest_framework.parsers.MultiPartParser',
    ],

    'DEFAULT_PAGINATION_CLASS': None,  # Отключаем пагинацию по умолчанию
    'PAGE_SIZE': 6,

    # 'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    # 'PAGE_SIZE': 6,

    'DEFAULT_FILTER_BACKENDS': ['django_filters.rest_framework.DjangoFilterBackend'],

}

DJOSER = {
    # 'LOGIN_FIELD': 'username',
    'LOGIN_FIELD': 'email',
    # 'USER_CREATE_PASSWORD_RETYPE': True,
    'USER_CREATE_PASSWORD_RETYPE': False,  # Отключить повторный ввод пароля
    'SEND_ACTIVATION_EMAIL': False,  # Отключить активацию по email
    'TOKEN_MODEL': 'rest_framework.authtoken.models.Token',
    'SERIALIZERS': {
        'user_create': 'recipes.serializers.UserCreateSerializer',
        'user': 'recipes.serializers.UserSerializer',
        'current_user': 'recipes.serializers.UserSerializer',
        'user_login': 'recipes.serializers.UserLoginSerializer',
    },
}

# DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

CORS_URLS_REGEX = r'^/api/.*$'
CORS_ALLOWED_ORIGINS = [
    'http://localhost:3000',
    'http://127.0.0.1:8000', 
]

# AUTHENTICATION_BACKENDS = (
#     'django.contrib.auth.backends.ModelBackend',  # Стандартный бэкэнд
# )
AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',  # Стандартный бэкэнд
    'recipes.backends.EmailAuthBackend',  # Кастомный бэкэнд для email
)

AUTH_USER_MODEL = 'recipes.User'

CORS_ALLOW_ALL_ORIGINS = True


# DJOSER = {
#     # 'LOGIN_FIELD': 'email',
#     'LOGIN_FIELD': 'username',
#     'USER_CREATE_PASSWORD_RETYPE': True,
#     # 'USERNAME_CHANGED_EMAIL_CONFIRMATION': False,
#     # 'PASSWORD_CHANGED_EMAIL_CONFIRMATION': False,
#     # 'SEND_CONFIRMATION_EMAIL': False,
#     # 'SET_PASSWORD_RETYPE': True,
#     # 'PASSWORD_RESET_CONFIRM_RETYPE': True,
#     'TOKEN_MODEL': 'rest_framework.authtoken.models.Token',
#     'SERIALIZERS': {
#         'user_create': 'recipes.serializers.UserCreateSerializer',
#         # 'token_create': 'djoser.serializers.TokenCreateSerializer',
#         'user': 'recipes.serializers.UserSerializer',
#         'current_user': 'recipes.serializers.UserSerializer',
#         # 'user_login': 'recipes.serializers.UserLoginSerializer',
#     },
# }

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'foodgram': {  # Название вашего проекта
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': True,
        },
    },
}