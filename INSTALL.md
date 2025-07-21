# Installation Guide for Secure File Sharing Platform

This guide will walk you through the steps to set up and run the Secure File Sharing Platform on your local machine or server.

## Prerequisites

- Python 3.9+ installed
- pip (Python package manager)
- Git (optional, for cloning the repository)
- SendGrid account (for email notifications) - optional

## Step 1: Clone the Repository

```bash
git clone https://github.com/syedsha0/secure-file-sharing.git
cd secure-file-sharing
```

Or download and extract the zip file from the repository.

## Step 2: Set Up a Virtual Environment (Recommended)

```bash
# Create a virtual environment
python -m venv venv

# Activate the virtual environment
# On Windows
venv\Scripts\activate
# On macOS/Linux
source venv/bin/activate
```

## Step 3: Install Dependencies

Using pip with the pyproject.toml file:

```bash
pip install .
```

Or install dependencies individually:

```bash
pip install flask flask-login flask-sqlalchemy flask-wtf email-validator cryptography psycopg2-binary gunicorn sendgrid python-dotenv
```

## Step 4: Configure Environment Variables

Create a `.env` file in the root directory with the following variables:

```
# Flask Secret Key - Change this to a random secure string
SESSION_SECRET=your_secret_key_here

# Database Configuration
# For SQLite (default for development)
# No additional configuration needed

# For PostgreSQL (recommended for production)
DATABASE_URL=postgresql://username:password@localhost:5432/databasename

# SendGrid Configuration (for email notifications)
SENDGRID_API_KEY=your_sendgrid_api_key
MAIL_DEFAULT_SENDER=no-reply@yourdomain.com
```

## Step 5: Initialize the Database

```bash
python scripts/init_db.py
```

## Step 6: Create Required Directories

The application will create these automatically on startup, but you can create them manually:

```bash
mkdir -p instance/uploads
mkdir -p instance/temp
mkdir -p uploads
mkdir -p temp
```

## Step 7: Run the Application

### Development Mode

```bash
python main.py
```

### Production Mode

For production deployment, we recommend using Gunicorn:

```bash
gunicorn --bind 0.0.0.0:5000 --workers 4 main:app
```

The application will be available at `http://localhost:5000`

## Step 8: Configure Email Notifications (Optional)

Email notifications require a SendGrid account:

1. Sign up for a SendGrid account at https://sendgrid.com/
2. Create an API key with mail send permissions
3. Add the API key to your environment variables as `SENDGRID_API_KEY`
4. Set the default sender email in your environment variables as `MAIL_DEFAULT_SENDER`

## Additional Configuration

### Storage Quotas

You can adjust user storage quotas in the `models.py` file. By default, users get 10GB of storage.

### Maximum Upload Size

The maximum file upload size is set to 100MB by default. You can change this in `config.py`.

### Session Duration

The session lifetime is set to 24 hours by default. You can modify this in `config.py`.

## Troubleshooting

### Database Connection Issues

If you're using PostgreSQL and experiencing connection issues:

1. Verify your PostgreSQL server is running
2. Check that your DATABASE_URL is correct
3. Ensure your PostgreSQL user has the necessary permissions

### Email Sending Issues

If emails are not being sent:

1. Verify your SendGrid API key is correct
2. Check that your sender email is verified with SendGrid
3. Look for any error messages in the application logs

### File Upload Problems

If file uploads fail:

1. Check that the upload directories have proper write permissions
2. Verify that the maximum upload size in `config.py` is appropriate
3. Check the server logs for any specific error messages

## Security Notes

- Always change the default `SESSION_SECRET` to a secure random string
- In production, use HTTPS to ensure secure data transmission
- Regularly back up your database
- Keep your dependencies updated for security patches
