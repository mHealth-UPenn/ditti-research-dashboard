from flask_apscheduler import APScheduler
from flask_bcrypt import Bcrypt
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from shared.tokens_manager import TokensManager


bcrypt = Bcrypt()
cors = CORS()
db = SQLAlchemy()
jwt = JWTManager()
migrate = Migrate()
scheduler = APScheduler()

tm = TokensManager()
