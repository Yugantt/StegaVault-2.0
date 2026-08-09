from flask_babel import Babel
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import CSRFProtect

db = SQLAlchemy()
babel = Babel()
csrf = CSRFProtect()
