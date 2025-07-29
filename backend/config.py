import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'your-secret-key')
    MONGODB_URI = os.environ.get('MONGODB_URI', 'mongodb+srv://haseebsiddique825:Apex%2389@mycluster.ujqwmto.mongodb.net/Apex_db')
    
    # SMTP configuration for email verification
    SMTP_SERVER = os.environ.get('SMTP_SERVER', 'smtp.gmail.com')
    SMTP_PORT = int(os.environ.get('SMTP_PORT', 587))
    SMTP_USERNAME = os.environ.get('SMTP_USERNAME', '')
    SMTP_PASSWORD = os.environ.get('SMTP_PASSWORD', '')
    EMAIL_FROM = os.environ.get('EMAIL_FROM', '')
    EMAIL_FROM_NAME = os.environ.get('EMAIL_FROM_NAME', 'Apex App') 