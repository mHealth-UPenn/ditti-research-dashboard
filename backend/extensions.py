# from flask_apscheduler import APScheduler
from authlib.integrations.flask_client import OAuth
from flask_caching import Cache
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

from shared.tokens_manager import TokensManager

cors = CORS()
db = SQLAlchemy()
jwt = JWTManager()
migrate = Migrate()
cache = Cache(config={"CACHE_TYPE": "SimpleCache", "CACHE_DEFAULT_TIMEOUT": 7200})

tm = TokensManager()
oauth = OAuth()
