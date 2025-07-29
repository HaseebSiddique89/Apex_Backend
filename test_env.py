#!/usr/bin/env python3
"""
Test environment variables loading
"""
from backend.config import Config

def test_environment_variables():
    """Test if environment variables are loaded correctly"""
    print("Testing environment variables...")
    print(f"SMTP_SERVER: {Config.SMTP_SERVER}")
    print(f"SMTP_PORT: {Config.SMTP_PORT}")
    print(f"SMTP_USERNAME: {Config.SMTP_USERNAME}")
    print(f"SMTP_PASSWORD: {'*' * len(Config.SMTP_PASSWORD) if Config.SMTP_PASSWORD else 'NOT SET'}")
    print(f"EMAIL_FROM: {Config.EMAIL_FROM}")
    print(f"EMAIL_FROM_NAME: {Config.EMAIL_FROM_NAME}")
    
    # Check if all required variables are set
    required_vars = [
        'SMTP_USERNAME',
        'SMTP_PASSWORD', 
        'EMAIL_FROM'
    ]
    
    missing_vars = []
    for var in required_vars:
        value = getattr(Config, var)
        if not value:
            missing_vars.append(var)
    
    if missing_vars:
        print(f"\n❌ Missing environment variables: {missing_vars}")
        print("Make sure your .env file is in the project root and contains:")
        print("SMTP_USERNAME=your_email@gmail.com")
        print("SMTP_PASSWORD=your_app_password")
        print("EMAIL_FROM=your_email@gmail.com")
    else:
        print("\n✅ All environment variables are set correctly!")

if __name__ == "__main__":
    test_environment_variables() 