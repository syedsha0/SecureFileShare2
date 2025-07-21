import os
import uuid
from datetime import datetime, timedelta

from app import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime, nullable=True)
    storage_quota = db.Column(db.BigInteger, default=10 * 1024 * 1024 * 1024)  # 10GB default
    storage_used = db.Column(db.BigInteger, default=0)
    password_reset_token = db.Column(db.String(100), nullable=True)
    password_reset_expiry = db.Column(db.DateTime, nullable=True)
    email_notifications = db.Column(db.Boolean, default=True)
    two_factor_enabled = db.Column(db.Boolean, default=False)
    two_factor_secret = db.Column(db.String(32), nullable=True)
    
    # Relationships
    files = db.relationship('File', backref='owner', lazy='dynamic', cascade='all, delete-orphan', 
                           foreign_keys='File.user_id')
    shares = db.relationship('Share', backref='created_by', lazy='dynamic', cascade='all, delete-orphan')
    folders = db.relationship('Folder', backref='owner', lazy='dynamic', cascade='all, delete-orphan')
    activities = db.relationship('Activity', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def generate_password_reset_token(self):
        """Generate a token for password reset"""
        self.password_reset_token = uuid.uuid4().hex
        # Set expiry to 1 hour from now
        self.password_reset_expiry = datetime.utcnow() + timedelta(hours=1)
        return self.password_reset_token
    
    def verify_password_reset_token(self, token):
        """Verify a password reset token"""
        if (self.password_reset_token == token and 
            self.password_reset_expiry and 
            self.password_reset_expiry > datetime.utcnow()):
            return True
        return False
    
    def clear_password_reset_token(self):
        """Clear the password reset token after it's been used"""
        self.password_reset_token = None
        self.password_reset_expiry = None
        
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class File(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    original_filename = db.Column(db.String(255), nullable=False)
    file_size = db.Column(db.Integer, nullable=False)
    mime_type = db.Column(db.String(127), nullable=True)
    encryption_key = db.Column(db.LargeBinary, nullable=False)
    encryption_nonce = db.Column(db.LargeBinary, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)
    parent_id = db.Column(db.Integer, db.ForeignKey('file.id'), nullable=True)
    version = db.Column(db.Integer, default=1)
    is_current = db.Column(db.Boolean, default=True)
    folder_id = db.Column(db.Integer, db.ForeignKey('folder.id'), nullable=True)
    description = db.Column(db.Text, nullable=True)
    
    # Relationships
    shares = db.relationship('Share', backref='file', lazy='dynamic', cascade='all, delete-orphan')
    previous_versions = db.relationship(
        'File',
        backref=db.backref('parent', remote_side=[id]),
        cascade='all, delete-orphan'
    )
    
    @property
    def file_path(self):
        from app import app
        return os.path.join(app.instance_path, app.config['UPLOAD_FOLDER'], self.filename)
        
    def get_preview_url(self):
        """Get URL for file preview if supported type"""
        if self.mime_type and (
            self.mime_type.startswith('image/') or 
            self.mime_type == 'application/pdf' or 
            self.mime_type.startswith('text/')
        ):
            from flask import url_for
            return url_for('files.preview_file', file_id=self.id)
        return None


class Folder(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    parent_id = db.Column(db.Integer, db.ForeignKey('folder.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    parent = db.relationship('Folder', remote_side=[id], backref='subfolders')
    files = db.relationship('File', backref='folder', lazy='dynamic')
    
    def get_path(self):
        """Get the full path of the folder"""
        path = [self.name]
        current = self.parent
        
        while current:
            path.insert(0, current.name)
            current = current.parent
            
        return '/' + '/'.join(path)


class Share(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    token = db.Column(db.String(64), unique=True, nullable=False, default=lambda: uuid.uuid4().hex)
    file_id = db.Column(db.Integer, db.ForeignKey('file.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime, nullable=True)
    max_downloads = db.Column(db.Integer, nullable=True)
    download_count = db.Column(db.Integer, default=0)
    password_hash = db.Column(db.String(256), nullable=True)
    
    def set_password(self, password):
        if password:
            self.password_hash = generate_password_hash(password)
        else:
            self.password_hash = None
        
    def check_password(self, password):
        if not self.password_hash:
            return True
        return check_password_hash(self.password_hash, password)
        
    def is_valid(self):
        if self.expires_at and self.expires_at < datetime.utcnow():
            return False
        if self.max_downloads and self.download_count >= self.max_downloads:
            return False
        return True
    
    def increment_download_count(self):
        self.download_count += 1
        db.session.commit()


class Activity(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    action = db.Column(db.String(32), nullable=False)
    target_type = db.Column(db.String(16), nullable=False)
    target_id = db.Column(db.Integer, nullable=False)
    ip_address = db.Column(db.String(64), nullable=True)
    user_agent = db.Column(db.String(255), nullable=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    details = db.Column(db.JSON, nullable=True)
    
    ACTIONS = {
        'CREATE': 'created',
        'UPDATE': 'updated',
        'DELETE': 'deleted',
        'UPLOAD': 'uploaded',
        'DOWNLOAD': 'downloaded',
        'SHARE': 'shared',
        'REVOKE': 'revoked share for',
        'LOGIN': 'logged in',
        'LOGOUT': 'logged out',
        'REGISTER': 'registered',
        'PREVIEW': 'previewed'
    }
    
    TARGET_TYPES = ['FILE', 'FOLDER', 'SHARE', 'USER', 'SYSTEM']
    
    @staticmethod
    def log(user_id, action, target_type, target_id, request=None, details=None):
        """Log a user activity"""
        if action not in Activity.ACTIONS:
            raise ValueError(f"Invalid action: {action}")
        
        if target_type not in Activity.TARGET_TYPES:
            raise ValueError(f"Invalid target type: {target_type}")
        
        ip_address = None
        user_agent = None
        
        if request:
            ip_address = request.remote_addr
            user_agent = request.user_agent.string if request.user_agent else None
        
        activity = Activity(
            user_id=user_id,
            action=action,
            target_type=target_type,
            target_id=target_id,
            ip_address=ip_address,
            user_agent=user_agent,
            details=details
        )
        
        db.session.add(activity)
        db.session.commit()
        
        return activity
