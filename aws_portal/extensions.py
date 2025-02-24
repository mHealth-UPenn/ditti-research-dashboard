# from flask_apscheduler import APScheduler
from flask_bcrypt import Bcrypt
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_caching import Cache
from html_sanitizer import Sanitizer
from authlib.integrations.flask_client import OAuth

from shared.tokens_manager import TokensManager


bcrypt = Bcrypt()
cors = CORS()
db = SQLAlchemy()
jwt = JWTManager()
migrate = Migrate()
# scheduler = APScheduler()
cache = Cache(config={
    "CACHE_TYPE": "SimpleCache",
    "CACHE_DEFAULT_TIMEOUT": 7200
})

tm = TokensManager()
oauth = OAuth()

sanitizer = Sanitizer({
    "attributes": {
        "li": ("class", "data-list")
    }
})
