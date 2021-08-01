import os
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SECRET_KEY = '7&cb7ybp)-z@f5ow8jryz=0*b!@4ma%e#bl2$z!+_g!i3*8=k_'
DEBUG = True
TESTING = sys.argv[1] == 'test'
ALLOWED_HOSTS = []

INSTALLED_APPS = [
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'openwisp_utils.admin_theme',
    # all-auth
    'django.contrib.sites',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    # Other dependencies
    'reversion',
    # openwisp2 modules
    'openwisp_users',
    'openwisp_ipam',
    # admin
    'django.contrib.admin',
    # rest framework
    'rest_framework',
    'rest_framework.authtoken',
    # Only for developement
    'django_extensions',
    'drf_yasg',
]

SITE_ID = 1
ROOT_URLCONF = 'openwisp2.urls'
AUTH_USER_MODEL = 'openwisp_users.User'

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

STATICFILES_FINDERS = [
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    'openwisp_utils.staticfiles.DependencyFinder',
]

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'OPTIONS': {
            'loaders': [
                'django.template.loaders.filesystem.Loader',
                'openwisp_utils.loaders.DependencyLoader',
                'django.template.loaders.app_directories.Loader',
            ],
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'openwisp_utils.admin_theme.context_processor.menu_groups',
            ],
        },
    },
]

DATABASES = {'default': {'ENGINE': 'django.db.backends.sqlite3', 'NAME': 'db.sqlite3'}}

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_L10N = True
USE_TZ = True
STATIC_URL = '/static/'
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
OPENWISP_USERS_AUTH_API = True

if TESTING:
    OPENWISP_ORGANIZATION_USER_ADMIN = True
    OPENWISP_ORGANIZATION_OWNER_ADMIN = True

if os.environ.get('SAMPLE_APP', False):
    ipam_index = INSTALLED_APPS.index('openwisp_ipam')
    INSTALLED_APPS.remove('openwisp_ipam')
    INSTALLED_APPS.insert(ipam_index, 'openwisp2.sample_ipam')
    # Replace Openwisp_Users
    users_index = INSTALLED_APPS.index('openwisp_users')
    INSTALLED_APPS.remove('openwisp_users')
    INSTALLED_APPS.insert(users_index, 'openwisp2.sample_users')
    EXTENDED_APPS = ['openwisp_ipam', 'openwisp_users']
    OPENWISP_IPAM_IPADDRESS_MODEL = 'sample_ipam.IpAddress'
    OPENWISP_IPAM_SUBNET_MODEL = 'sample_ipam.Subnet'
    # Swapper
    AUTH_USER_MODEL = 'sample_users.User'
    OPENWISP_USERS_GROUP_MODEL = 'sample_users.Group'
    OPENWISP_USERS_ORGANIZATION_MODEL = 'sample_users.Organization'
    OPENWISP_USERS_ORGANIZATIONUSER_MODEL = 'sample_users.OrganizationUser'
    OPENWISP_USERS_ORGANIZATIONOWNER_MODEL = 'sample_users.OrganizationOwner'

# local settings must be imported before test runner otherwise they'll be ignored
try:
    from openwisp2.local_settings import *
except ImportError:
    pass
