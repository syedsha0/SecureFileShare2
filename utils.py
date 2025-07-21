import os
import base64
import hashlib
import secrets
import tempfile
from io import BytesIO
from pathlib import Path
from datetime import datetime, timedelta

from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from werkzeug.utils import secure_filename
from flask import current_app, send_file


def get_random_bytes(length):
    """Generate secure random bytes of specified length"""
    return secrets.token_bytes(length)


def encrypt_file(input_file, output_file_path, key=None):
    """
    Encrypt a file using AES-GCM
    
    Args:
        input_file: File object or bytes
        output_file_path: Path to save the encrypted file
        key: Optional encryption key (will generate if not provided)
        
    Returns:
        tuple: (key, nonce) used for encryption
    """
    # Generate key and nonce if not provided
    if key is None:
        key = get_random_bytes(current_app.config['ENCRYPTION_KEY_LENGTH'])
    nonce = get_random_bytes(12)  # 96 bits is recommended for AES-GCM
    
    # Create AESGCM cipher with our key
    aesgcm = AESGCM(key)
    
    # Read the file content
    if hasattr(input_file, 'read'):
        plaintext = input_file.read()
    else:
        plaintext = input_file
    
    # Encrypt the file
    ciphertext = aesgcm.encrypt(nonce, plaintext, None)
    
    # Write the encrypted data
    with open(output_file_path, 'wb') as f:
        f.write(ciphertext)
    
    return key, nonce


def decrypt_file(file_path, key, nonce):
    """
    Decrypt a file using AES-GCM
    
    Args:
        file_path: Path to the encrypted file
        key: Encryption key
        nonce: Nonce used during encryption
        
    Returns:
        BytesIO: Decrypted file content as a BytesIO object
    """
    # Create AESGCM cipher with our key
    aesgcm = AESGCM(key)
    
    # Read the encrypted file
    with open(file_path, 'rb') as f:
        ciphertext = f.read()
    
    # Decrypt the file
    plaintext = aesgcm.decrypt(nonce, ciphertext, None)
    
    # Return a BytesIO object with the decrypted content
    return BytesIO(plaintext)


def generate_unique_filename(original_filename):
    """Generate a unique filename to prevent overwriting and information leakage"""
    timestamp = datetime.utcnow().strftime('%Y%m%d%H%M%S')
    random_str = secrets.token_hex(8)
    ext = Path(original_filename).suffix
    
    # Create a filename that doesn't reveal the original name
    return f"{timestamp}_{random_str}{ext}"


def get_file_mimetype(filename):
    """Try to determine the MIME type based on file extension"""
    ext = Path(filename).suffix.lower()
    mime_types = {
        '.txt': 'text/plain',
        '.pdf': 'application/pdf',
        '.doc': 'application/msword',
        '.docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        '.xls': 'application/vnd.ms-excel',
        '.xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        '.ppt': 'application/vnd.ms-powerpoint',
        '.pptx': 'application/vnd.openxmlformats-officedocument.presentationml.presentation',
        '.jpg': 'image/jpeg',
        '.jpeg': 'image/jpeg',
        '.png': 'image/png',
        '.gif': 'image/gif',
        '.mp3': 'audio/mpeg',
        '.mp4': 'video/mp4',
        '.zip': 'application/zip',
        '.csv': 'text/csv',
    }
    return mime_types.get(ext, 'application/octet-stream')


def save_file_chunks(chunks_dir, filename):
    """
    Combine chunks into a complete file
    
    Args:
        chunks_dir: Directory containing the chunks
        filename: Name of the output file
    
    Returns:
        str: Path to the combined file
    """
    # Sort chunks numerically
    chunk_files = sorted(
        [f for f in os.listdir(chunks_dir) if f.startswith('chunk_')],
        key=lambda x: int(x.split('_')[1])
    )
    
    # Create a temporary file to store the combined content
    temp_file = tempfile.NamedTemporaryFile(delete=False)
    temp_path = temp_file.name
    
    try:
        # Combine chunks
        with open(temp_path, 'wb') as outfile:
            for chunk_file in chunk_files:
                chunk_path = os.path.join(chunks_dir, chunk_file)
                with open(chunk_path, 'rb') as infile:
                    outfile.write(infile.read())
                # Remove the chunk after it's been processed
                os.unlink(chunk_path)
        
        return temp_path
    except Exception as e:
        # Clean up in case of failure
        if os.path.exists(temp_path):
            os.unlink(temp_path)
        raise e


def create_download_response(file_path, original_filename, mimetype=None):
    """
    Create a proper file download response
    
    Args:
        file_path: Path to the file to download
        original_filename: Original filename to use in Content-Disposition
        mimetype: Optional mimetype
        
    Returns:
        Flask Response object for file download
    """
    if mimetype is None:
        mimetype = get_file_mimetype(original_filename)
    
    # Create a response with the file
    return send_file(
        file_path,
        mimetype=mimetype,
        as_attachment=True,
        download_name=original_filename
    )


def file_size_format(num_bytes):
    """Format file size in a human-readable form"""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if num_bytes < 1024.0:
            return f"{num_bytes:.1f} {unit}"
        num_bytes /= 1024.0
    return f"{num_bytes:.1f} PB"
