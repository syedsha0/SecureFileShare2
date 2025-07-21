# Secure File Sharing Platform

A robust, secure file sharing platform that provides end-to-end encryption, comprehensive activity tracking, and user-centric sharing capabilities.

## Features

### Core Functionality
- **Secure File Upload & Storage**: All files are encrypted using AES-GCM encryption
- **File Management**: Organize files with folders, search, and manage versions
- **File Versioning**: Track changes by uploading new versions of existing files
- **File Preview**: Preview supported file types directly in the browser
- **File Sharing**: Share files securely with password protection and expiration dates

### Security Features
- **End-to-End Encryption**: All files are encrypted before storage
- **Password Protection**: Protect shared files with passwords
- **Expiring Links**: Set expiration dates for shared files
- **Download Limits**: Set maximum number of downloads for shared files
- **Activity Logging**: Comprehensive logging of all user activities
- **Suspicious Login Detection**: Get alerts when someone logs in from a new device/location
- **Password Reset**: Secure password reset functionality with tokens
- **Storage Quotas**: Set and enforce storage limits for users

### User Experience
- **Email Notifications**: Get notified about file shares and security events
- **Activity Dashboard**: View all recent activities on your account
- **Mobile Responsive**: Access from any device with a responsive interface

## Tech Stack

- **Backend**: Python with Flask framework
- **Database**: SQLite (local development) / PostgreSQL (production)
- **Authentication**: Flask-Login with secure password hashing
- **Email Service**: SendGrid API integration
- **Encryption**: AES-GCM via Python's cryptography library
- **Frontend**: Bootstrap 5 for responsive UI

## Security Measures

### File Security
- **End-to-End Encryption**: All files are encrypted using AES-GCM before storage
- **Unique Keys**: Each file has its own encryption key and nonce
- **Secure Storage**: Encryption keys are never stored in plaintext

### Account Security
- **Secure Password Hashing**: Using Werkzeug's security functions
- **Password Reset Tokens**: Time-limited tokens for password recovery
- **Suspicious Login Detection**: Alerts for unusual login activity
- **Activity Logging**: Comprehensive tracking of all account actions
- **Login History**: Track all logins with IP addresses and user agents

### Web Security
- **CSRF Protection**: On all forms to prevent cross-site request forgery
- **Secure Headers**: Proper security headers for browser protection
- **Error Handling**: Secure error pages that don't leak information
- **Input Validation**: Strict validation on all user inputs

### Sharing Security
- **Password Protection**: Optional password protection for shared files
- **Expiration Dates**: Set automatic expiration for shared links
- **Download Limits**: Restrict the number of times a file can be downloaded
- **Access Tracking**: Log all access to shared files

### Notification System
- **Security Alerts**: Email notifications for suspicious activities
- **Share Notifications**: Email notifications when files are shared
- **Password Reset Emails**: Secure email-based password recovery
- **Welcome Emails**: Onboarding emails for new users

## Preview

![Dashboard](screenshots/dashboard.png)

## Getting Started

### Quick Setup

```bash
# Clone the repository
git clone https://github.com/syedsha0/secure-file-sharing.git
cd secure-file-sharing

# Set up virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install .

# Initialize the database
python scripts/init_db.py

# Run the application
python main.py
```

The application will be available at `http://localhost:5000`

See [INSTALL.md](INSTALL.md) for detailed installation and setup instructions, including:
- PostgreSQL configuration
- Email notification setup 
- Production deployment
- Troubleshooting

## License

This project is licensed under the MIT License - see the LICENSE file for details.
