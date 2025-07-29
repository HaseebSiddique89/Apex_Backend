import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from backend.config import Config
import secrets
import string

def generate_verification_token(length=32):
    """Generate a random verification token"""
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(length))

async def send_verification_email(email, username, verification_token):
    """Send verification email to user"""
    try:
        # Create message
        msg = MIMEMultipart()
        msg['From'] = f"{Config.EMAIL_FROM_NAME} <{Config.EMAIL_FROM}>"
        msg['To'] = email
        msg['Subject'] = "Verify Your Email - Apex App"
        
        # Create verification link (you'll need to set your frontend URL)
        verification_url = f"http://localhost:3000/verify-email?token={verification_token}"
        
        # Email body
        body = f"""
        Hello {username},
        
        Thank you for signing up with Apex App! Please verify your email address by clicking the link below:
        
        {verification_url}
        
        If you didn't create an account, you can safely ignore this email.
        
        Best regards,
        The Apex App Team
        """
        
        msg.attach(MIMEText(body, 'plain'))
        
        # Create SMTP session
        context = ssl.create_default_context()
        
        with smtplib.SMTP(Config.SMTP_SERVER, Config.SMTP_PORT) as server:
            server.starttls(context=context)
            server.login(Config.SMTP_USERNAME, Config.SMTP_PASSWORD)
            text = msg.as_string()
            # Send to the user's email address, not the sender's
            server.sendmail(Config.EMAIL_FROM, [email], text)
            
        return True
    except Exception as e:
        print(f"Error sending email: {e}")
        return False 