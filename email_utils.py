import os
import sys
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Email, To, Content
from flask import current_app, url_for, render_template

# Get the SendGrid API key from environment variables
sendgrid_key = os.environ.get('SENDGRID_API_KEY')

def send_email(
    to_email,
    from_email,
    subject,
    text_content=None,
    html_content=None
) -> bool:
    """
    Send an email using SendGrid
    
    Args:
        to_email (str): Recipient email address
        from_email (str): Sender email address
        subject (str): Email subject
        text_content (str, optional): Plain text content
        html_content (str, optional): HTML content
        
    Returns:
        bool: True if email was sent successfully, False otherwise
    """
    if not sendgrid_key:
        current_app.logger.error("SendGrid API key not found")
        return False
        
    sg = SendGridAPIClient(sendgrid_key)

    message = Mail(
        from_email=Email(from_email),
        to_emails=To(to_email),
        subject=subject
    )

    if html_content:
        message.content = Content("text/html", html_content)
    elif text_content:
        message.content = Content("text/plain", text_content)
    else:
        current_app.logger.error("Email content not provided")
        return False

    try:
        sg.send(message)
        current_app.logger.info(f"Email sent to {to_email}")
        return True
    except Exception as e:
        current_app.logger.error(f"SendGrid error: {e}")
        return False

def send_share_notification(share, recipient_email, sender_name):
    """
    Send a notification email when a file is shared
    
    Args:
        share: Share object
        recipient_email: Email address of the recipient
        sender_name: Name of the person sharing the file
        
    Returns:
        bool: True if email was sent successfully, False otherwise
    """
    from_email = current_app.config.get('MAIL_DEFAULT_SENDER', 'noreply@securefiles.com')
    subject = f"{sender_name} shared a file with you"
    
    # Generate the share access URL
    share_url = url_for('shares.access_shared_file', token=share.token, _external=True)
    
    # Get file information
    filename = share.file.original_filename
    expires_at = share.expires_at.strftime("%Y-%m-%d %H:%M UTC") if share.expires_at else "Never"
    is_password_protected = share.password_hash is not None
    
    # Create email content
    text_content = f"""
    {sender_name} has shared a file with you: {filename}
    
    Click the link below to access the file:
    {share_url}
    
    Expires: {expires_at}
    Password Protected: {"Yes" if is_password_protected else "No"}
    
    This is an automated message, please do not reply.
    """
    
    html_content = f"""
    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #e0e0e0; border-radius: 5px;">
        <h2 style="color: #333;">File Shared With You</h2>
        <p><strong>{sender_name}</strong> has shared a file with you:</p>
        <div style="background-color: #f5f5f5; padding: 15px; border-radius: 5px; margin: 15px 0;">
            <p style="margin: 0;"><strong>{filename}</strong></p>
        </div>
        <p><a href="{share_url}" style="display: inline-block; background-color: #4CAF50; color: white; padding: 10px 20px; text-decoration: none; border-radius: 4px;">Access File</a></p>
        <div style="margin-top: 20px; padding-top: 15px; border-top: 1px solid #e0e0e0;">
            <p><strong>Expires:</strong> {expires_at}</p>
            <p><strong>Password Protected:</strong> {"Yes" if is_password_protected else "No"}</p>
        </div>
        <p style="font-size: 12px; color: #777; margin-top: 30px;">This is an automated message, please do not reply.</p>
    </div>
    """
    
    return send_email(
        to_email=recipient_email,
        from_email=from_email,
        subject=subject,
        text_content=text_content,
        html_content=html_content
    )

def send_password_reset(user, reset_token):
    """
    Send a password reset email
    
    Args:
        user: User object
        reset_token: Password reset token
        
    Returns:
        bool: True if email was sent successfully, False otherwise
    """
    from_email = current_app.config.get('MAIL_DEFAULT_SENDER', 'noreply@securefiles.com')
    subject = "Password Reset Request"
    
    # Generate the reset URL
    reset_url = url_for('auth.reset_password', token=reset_token, _external=True)
    
    # Create email content
    text_content = f"""
    Hello {user.username},
    
    We received a request to reset your password. Click the link below to reset it:
    {reset_url}
    
    If you didn't request a password reset, please ignore this email or contact support if you have concerns.
    
    This link will expire in 1 hour.
    """
    
    html_content = f"""
    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #e0e0e0; border-radius: 5px;">
        <h2 style="color: #333;">Password Reset Request</h2>
        <p>Hello <strong>{user.username}</strong>,</p>
        <p>We received a request to reset your password. Click the button below to reset it:</p>
        <p><a href="{reset_url}" style="display: inline-block; background-color: #4CAF50; color: white; padding: 10px 20px; text-decoration: none; border-radius: 4px;">Reset Password</a></p>
        <p>If the button doesn't work, copy and paste this link into your browser:</p>
        <p style="word-break: break-all; background-color: #f5f5f5; padding: 10px; border-radius: 4px;">{reset_url}</p>
        <p>If you didn't request a password reset, please ignore this email or contact support if you have concerns.</p>
        <p><strong>This link will expire in 1 hour.</strong></p>
        <p style="font-size: 12px; color: #777; margin-top: 30px;">This is an automated message, please do not reply.</p>
    </div>
    """
    
    return send_email(
        to_email=user.email,
        from_email=from_email,
        subject=subject,
        text_content=text_content,
        html_content=html_content
    )

def send_account_activity_alert(user, activity_type, ip_address, user_agent, timestamp):
    """
    Send an alert for suspicious account activity
    
    Args:
        user: User object
        activity_type: Type of activity (login, password change, etc.)
        ip_address: IP address from which the activity was performed
        user_agent: User agent string
        timestamp: Time of the activity
        
    Returns:
        bool: True if email was sent successfully, False otherwise
    """
    from_email = current_app.config.get('MAIL_DEFAULT_SENDER', 'noreply@securefiles.com')
    subject = f"Security Alert: {activity_type}"
    
    # Format timestamp
    timestamp_str = timestamp.strftime("%Y-%m-%d %H:%M:%S UTC")
    
    # Create email content
    text_content = f"""
    Hello {user.username},
    
    We detected a {activity_type} on your account at {timestamp_str}.
    
    IP Address: {ip_address}
    Browser/Device: {user_agent}
    
    If this was you, you can ignore this message. If you didn't perform this action, please change your password immediately and contact support.
    """
    
    html_content = f"""
    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #e0e0e0; border-radius: 5px;">
        <h2 style="color: #333;">Security Alert</h2>
        <p>Hello <strong>{user.username}</strong>,</p>
        <p>We detected a <strong>{activity_type}</strong> on your account at <strong>{timestamp_str}</strong>.</p>
        <div style="background-color: #f5f5f5; padding: 15px; border-radius: 5px; margin: 15px 0;">
            <p><strong>IP Address:</strong> {ip_address}</p>
            <p style="margin-bottom: 0;"><strong>Browser/Device:</strong> {user_agent}</p>
        </div>
        <p>If this was you, you can ignore this message. If you didn't perform this action, please change your password immediately and contact support.</p>
        <p style="font-size: 12px; color: #777; margin-top: 30px;">This is an automated message, please do not reply.</p>
    </div>
    """
    
    return send_email(
        to_email=user.email,
        from_email=from_email,
        subject=subject,
        text_content=text_content,
        html_content=html_content
    )
    
def send_welcome_email(user):
    """
    Send a welcome email to new users
    
    Args:
        user: User object
        
    Returns:
        bool: True if email was sent successfully, False otherwise
    """
    from_email = current_app.config.get('MAIL_DEFAULT_SENDER', 'noreply@securefiles.com')
    subject = "Welcome to Secure File Sharing!"
    
    # Generate login URL
    login_url = url_for('auth.login', _external=True)
    
    # Render the HTML template
    try:
        html_content = render_template('email/welcome.html', user=user, login_url=login_url)
    except Exception as e:
        current_app.logger.error(f"Error rendering welcome email template: {e}")
        # Fallback to a simple HTML content if template rendering fails
        html_content = f"""
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #e0e0e0; border-radius: 5px;">
            <h2 style="color: #333;">Welcome to Secure File Sharing!</h2>
            <p>Hello <strong>{user.username}</strong>,</p>
            <p>Thank you for registering! Your account has been created successfully.</p>
            <p>You can now <a href="{login_url}">log in to your account</a> and start using our secure file sharing platform.</p>
            <p>Best regards,<br>The Secure File Sharing Team</p>
        </div>
        """
    
    # Create plain text version
    text_content = f"""
    Welcome to Secure File Sharing!
    
    Hello {user.username},
    
    Thank you for registering! Your account has been created successfully.
    You can now log in to your account and start using our secure file sharing platform.
    
    {login_url}
    
    Best regards,
    The Secure File Sharing Team
    """
    
    return send_email(
        to_email=user.email,
        from_email=from_email,
        subject=subject,
        text_content=text_content,
        html_content=html_content
    )