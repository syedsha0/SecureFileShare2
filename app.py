import os
import logging

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from werkzeug.middleware.proxy_fix import ProxyFix
from flask_login import LoginManager

logging.basicConfig(level=logging.DEBUG)

# Create the app
app = Flask(__name__)
app.config.from_object('config.Config')
app.secret_key = os.environ.get("SESSION_SECRET", "dev_secret_key")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)  # needed for url_for to generate with https

# Configure the database
# Use SQLite database for now due to PostgreSQL connection issues
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///secure_files.db"
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Define base class for SQLAlchemy models
class Base(DeclarativeBase):
    pass

# Initialize SQLAlchemy
db = SQLAlchemy(model_class=Base)
db.init_app(app)

# Configure login manager
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.login_message_category = 'info'
login_manager.init_app(app)

# Register blueprints - Import routes here to avoid circular imports
with app.app_context():
    # Import routes after app and extensions are initialized
    from routes import auth, files, shares
    
    # Register blueprints
    app.register_blueprint(auth.auth_bp)
    app.register_blueprint(files.files_bp)
    app.register_blueprint(shares.shares_bp)

with app.app_context():
    # Import models to ensure tables are created
    import models
    
    # Create all tables
    db.create_all()
    
    # Create upload directory if it doesn't exist
    uploads_dir = os.path.join(app.instance_path, app.config['UPLOAD_FOLDER'])
    if not os.path.exists(uploads_dir):
        os.makedirs(uploads_dir, exist_ok=True)
    
    # Create temp directory for chunks if it doesn't exist
    temp_dir = os.path.join(app.instance_path, app.config['TEMP_FOLDER'])
    if not os.path.exists(temp_dir):
        os.makedirs(temp_dir, exist_ok=True)

@login_manager.user_loader
def load_user(user_id):
    from models import User
    return User.query.get(int(user_id))
