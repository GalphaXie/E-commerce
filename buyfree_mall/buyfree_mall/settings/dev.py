"""
Django settings for buyfree_mall project.

Generated by 'django-admin startproject' using Django 1.11.11.

For more information on this file, see
https://docs.djangoproject.com/en/1.11/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.11/ref/settings/
"""
import datetime
import os

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# 在BASE_DIR下面
import sys

sys.path.insert(0, os.path.join(BASE_DIR, "apps"))
# print(sys.path)

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.11/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '!@6$2#+es%24#kbbq^!_=54s@7b2o@g3wfyy(rx@=mcvf8)%gs'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['api.meiduo.site', '127.0.0.1', 'localhost', 'www.meiduo.site']

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'corsheaders',  # 1. heads 用于处理跨域资源共享的相关http头
    'ckeditor',  # 富文本编辑器
    'ckeditor_uploader',  # 富文本编辑器上传图片模块
    'django_crontab',  # 定时任务
    'haystack',  # 对接搜索引擎
    'users.apps.UsersConfig',
    'verifications.apps.VerificationsConfig',
    'oauth.apps.OauthConfig',
    'areas.apps.AreasConfig',
    'goods.apps.GoodsConfig',
    'contents.apps.ContentsConfig',
    'carts.apps.CartsConfig',
    'orders.apps.OrderConfig',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',  # 2. 关注顺序(一定要添加到最前面)  # 解决跨域请求
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'buyfree_mall.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],  # 配置模板文件的目录
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

WSGI_APPLICATION = 'buyfree_mall.wsgi.application'

# Database
# https://docs.djangoproject.com/en/1.11/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'HOST': '127.0.0.1',  # 数据库主机
        'PORT': 3306,  # 数据库端口
        'USER': 'buyfree',  # 数据库用户名
        'PASSWORD': 'buyfree',  # 数据库用户密码
        'NAME': 'buyfree_mall'  # 数据库名字
    }
}

CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://127.0.0.1:6379/0",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        }
    },
    "session": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://127.0.0.1:6379/1",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        }
    },
    "verify_codes": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://127.0.0.1:6379/2",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        }
    },
    "history": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://127.0.0.1:6379/3",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        }
    },
    "cart": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://127.0.0.1:6379/4",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        }
    }
}
# 给admin站点使用的session
SESSION_ENGINE = "django.contrib.sessions.backends.cache"
SESSION_CACHE_ALIAS = "session"

# Password validation
# https://docs.djangoproject.com/en/1.11/ref/settings/#auth-password-validators

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

# Internationalization
# https://docs.djangoproject.com/en/1.11/topics/i18n/

# LANGUAGE_CODE = 'en-us'
#
# TIME_ZONE = 'UTC'
# 大小写均可，大写可能会出现‘繁体’信息
LANGUAGE_CODE = 'zh-hans'
TIME_ZONE = 'Asia/Shanghai'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.11/howto/static-files/

STATIC_URL = '/static/'

LOGGING = {
    'version': 1,  # 这一行是固定的
    'disable_existing_loggers': False,  # 是否禁止已存在的日志器
    'formatters': {  # 格式化信息
        'verbose': {  # 冗长的
            'format': '%(levelname)s %(asctime)s %(module)s %(lineno)d %(message)s'
        },
        'simple': {  # 简单的
            'format': '%(levelname)s %(module)s %(lineno)d %(message)s'
        },
    },
    'filters': {  # 过滤器，这里不做任何过滤
        'require_debug_true': {
            '()': 'django.utils.log.RequireDebugTrue',
        },
    },
    'handlers': {  # 控制
        'console': {  # 往终端写
            'level': 'DEBUG',
            'filters': ['require_debug_true'],
            'class': 'logging.StreamHandler',
            'formatter': 'simple'
        },
        'file': {  # 往文件写
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(os.path.dirname(BASE_DIR), "logs/buyfree.log"),  # 往哪里写，文件名
            'maxBytes': 300 * 1024 * 1024,  # 文件大小
            'backupCount': 10,  # 最多保留多少个
            'formatter': 'verbose'
        },
    },
    'loggers': {  # 创建loggers日志器对象
        'django': {  # 定义一个名为 django 的日志器
            'handlers': ['console', 'file'],
            'propagate': True,  # 传播传送繁殖 -- 是否‘往上一级传递，冒泡’
        },
    }
}

REST_FRAMEWORK = {
    # 异常处理
    'EXCEPTION_HANDLER': 'buyfree_mall.utils.exceptions.exception_handler',
    # 这个配置要等后面做购物车的时候才有用
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_jwt.authentication.JSONWebTokenAuthentication',
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.BasicAuthentication',
    ),
    # 分页
    'DEFAULT_PAGINATION_CLASS': 'buyfree_mall.utils.pagination.StandardResultsSetPagination',
}

JWT_AUTH = {
    # 注册
    'JWT_EXPIRATION_DELTA': datetime.timedelta(days=1),  # token过期时间
    'JWT_RESPONSE_PAYLOAD_HANDLER': 'users.utils.jwt_response_payload_handler',
}

# 配置,让django使用我们定义的模型
AUTH_USER_MODEL = 'users.User'

# 认证方法
AUTHENTICATION_BACKENDS = [
    'users.utils.UsernameMobileAuthBackend',
]

# CORS  3.1 白名单
# 对比 ALLOWED_HOSTS , 为何上面不用端口,这里要加上port
CORS_ORIGIN_WHITELIST = (
    '127.0.0.1:8080',
    'localhost:8080',
    'www.meiduo.site:8080',
    'api.meiduo.site:8000'
)
CORS_ALLOW_CREDENTIALS = True  # 3.2 允许携带cookie

# QQ登录参数
QQ_CLIENT_ID = '101474184'
QQ_CLIENT_SECRET = 'c6ce949e04e12ecc909ae6a8b09b637c'
QQ_REDIRECT_URI = 'http://www.meiduo.site:8080/oauth_callback.html'
QQ_STATE = '/'  # 或 '/index.html'

# 配置发送邮件的邮箱信息
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.163.com'
EMAIL_PORT = 25
# 发送邮件的邮箱
EMAIL_HOST_USER = 'defaulttest@163.com'
# 在邮箱中设置的客户端授权密码
EMAIL_HOST_PASSWORD = 'xiexie39'
# 收件人看到的发件人
EMAIL_FROM = '帅哭你有限责任公司<defaulttest@163.com>'

# DRF扩展
REST_FRAMEWORK_EXTENSIONS = {
    # 缓存时间
    'DEFAULT_CACHE_RESPONSE_TIMEOUT': 60 * 60,
    # 缓存存储
    'DEFAULT_USE_CACHE': 'default',
}

# django文件存储
DEFAULT_FILE_STORAGE = 'buyfree_mall.utils.fastdfs.fdfs_storage.FastDFSStorage'

# FastDFS
FDFS_URL = 'http://image.meiduo.site:8888/'
FDFS_CLIENT_CONF = os.path.join(BASE_DIR, 'utils/fastdfs/client.conf')

# 富文本编辑器ckeditor配置
CKEDITOR_CONFIGS = {
    'default': {
        'toolbar': 'full',  # 工具条功能
        'height': 300,  # 编辑器高度
        # 'width': 300,  # 编辑器宽
    },
}
CKEDITOR_UPLOAD_PATH = ''  # 上传图片保存路径，使用了FastDFS，所以此处设为''

# 页面静态化保存的文件目录
GENERATED_STATIC_HTML_FILES_DIR = os.path.join(os.path.dirname(os.path.dirname(BASE_DIR)), 'front_end_pc')

# 定时任务
CRONJOBS = [
    # 每个可以被5整除的分钟(如0,10,15,20,...执行一次)执行一次生成主页静态文件
    # ('*/5 * * * *', 'contents.crons.generate_static_index_html', '>> /Users/delron/Desktop/meiduo_mall/logs/crontab.log')
    # 三个参数,第一个是固定的设置'时间间隔或者指定时间刷新', 定时任务函数(不要加小括号;且不能传递参数), 系统执行记录打印输出的位置
    ('*/5 * * * *', 'contents.crons.generate_static_index_html',
     '>> ' + os.path.join(os.path.dirname(BASE_DIR), 'logs/crontab.log'))
]

# 解决crontab中文问题
CRONTAB_COMMAND_PREFIX = 'LANG_ALL=zh_cn.UTF-8'

# Haystack
HAYSTACK_CONNECTIONS = {
    'default': {
        'ENGINE': 'haystack.backends.elasticsearch_backend.ElasticsearchSearchEngine',
        'URL': 'http://192.168.129.169/',  # 此处为elasticsearch运行的服务器ip地址，端口号固定为9200
        'INDEX_NAME': 'buyfree',  # 指定elasticsearch建立的索引库的名称
    },
}

# 当添加、修改、删除数据时，自动生成索引
HAYSTACK_SIGNAL_PROCESSOR = 'haystack.signals.RealtimeSignalProcessor'  # 实时
