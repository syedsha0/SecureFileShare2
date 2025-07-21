from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms import StringField, PasswordField, BooleanField, SubmitField, IntegerField, DateField, TextAreaField, SelectField
from wtforms.validators import DataRequired, Email, EqualTo, Length, Optional, ValidationError
from datetime import datetime, timedelta
from config import Config


class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=64)])
    email = StringField('Email', validators=[DataRequired(), Email(), Length(max=120)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=8)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Log In')


class UploadForm(FlaskForm):
    file = FileField('File', validators=[FileRequired()])
    submit = SubmitField('Upload')


class ShareForm(FlaskForm):
    recipient_email = StringField('Recipient Email (Optional)', validators=[Optional(), Email()])
    password = PasswordField('Password Protection (Optional)', validators=[Optional(), Length(min=4)])
    confirm_password = PasswordField('Confirm Password', 
                                     validators=[Optional(), EqualTo('password')])
    expiry_days = IntegerField('Expiry Days', default=Config.SHARE_LINK_EXPIRY,
                              validators=[Optional()])
    max_downloads = IntegerField('Maximum Downloads', validators=[Optional()])
    send_notification = BooleanField('Send notification email to recipient', default=True)
    submit = SubmitField('Create Share Link')

    def validate_expiry_days(self, field):
        if field.data is not None and field.data < 0:
            raise ValidationError('Expiry days must be a positive number')


class SharePasswordForm(FlaskForm):
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Access File')


class DeleteFileForm(FlaskForm):
    confirm = BooleanField('I confirm I want to delete this file', validators=[DataRequired()])
    submit = SubmitField('Delete File')


class RevokeShareForm(FlaskForm):
    submit = SubmitField('Revoke Share')


class FileVersionForm(FlaskForm):
    file = FileField('File', validators=[FileRequired()])
    description = TextAreaField('Version Notes', validators=[Optional(), Length(max=500)])
    submit = SubmitField('Upload New Version')


class FolderForm(FlaskForm):
    name = StringField('Folder Name', validators=[DataRequired(), Length(min=1, max=255)])
    description = TextAreaField('Description', validators=[Optional(), Length(max=500)])
    submit = SubmitField('Create Folder')


class MoveFolderForm(FlaskForm):
    target_folder = SelectField('Move To', coerce=int, validators=[Optional()])
    submit = SubmitField('Move')


class FileSearchForm(FlaskForm):
    query = StringField('Search', validators=[DataRequired(), Length(min=2, max=100)])
    search_type = SelectField('Search In', choices=[
        ('filename', 'Filename'),
        ('content', 'File Content'),
        ('both', 'Both')
    ], default='filename')
    submit = SubmitField('Search')


class UserSettingsForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=64)])
    email = StringField('Email', validators=[DataRequired(), Email(), Length(max=120)])
    current_password = PasswordField('Current Password', validators=[Optional(), Length(min=8)])
    new_password = PasswordField('New Password', validators=[Optional(), Length(min=8)])
    confirm_password = PasswordField('Confirm New Password', validators=[
        EqualTo('new_password', message='Passwords must match')
    ])
    submit = SubmitField('Update Settings')
    

class TwoFactorSetupForm(FlaskForm):
    verification_code = StringField('Verification Code', validators=[
        DataRequired(), 
        Length(min=6, max=6, message='Verification code must be 6 digits')
    ])
    submit = SubmitField('Verify and Enable 2FA')
    
    
class FileTagForm(FlaskForm):
    tags = StringField('Tags (comma separated)', validators=[Optional(), Length(max=200)])
    submit = SubmitField('Update Tags')


class RequestPasswordResetForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Request Password Reset')
    
    
class ResetPasswordForm(FlaskForm):
    password = PasswordField('New Password', validators=[DataRequired(), Length(min=8)])
    confirm_password = PasswordField('Confirm New Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Reset Password')
