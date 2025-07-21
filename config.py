import os
import tempfile

class Config:
    SECRET_KEY = os.environ.get('SESSION_SECRET', 'dev_secret_key')
    MAX_CONTENT_LENGTH = 100 * 1024 * 1024  # 100 MB max upload size
    UPLOAD_FOLDER = 'uploads'
    TEMP_FOLDER = 'temp'
    CHUNK_SIZE = 1024 * 1024  # 1MB chunks
    
    # Encryption settings
    ENCRYPTION_KEY_LENGTH = 32  # 256 bits
    
    # Link sharing settings
    SHARE_LINK_EXPIRY = 7  # days
    
    # Session settings
    PERMANENT_SESSION_LIFETIME = 86400  # 24 hours
    SESSION_TYPE = 'filesystem'
    SESSION_PERMANENT = True
    SESSION_USE_SIGNER = True
