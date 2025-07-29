#!/usr/bin/env python3
"""
Test script for email verification functionality
"""
import asyncio
import os
from backend.utils.email_utils import generate_verification_token, send_verification_email

async def test_email_functionality():
    """Test the email verification functionality"""
    print("Testing email verification functionality...")
    
    # Test token generation
    token = generate_verification_token()
    print(f"Generated verification token: {token}")
    print(f"Token length: {len(token)}")
    
    # Test email sending (you'll need to set up your SMTP credentials first)
    print("\nTesting email sending...")
    print("Note: Make sure you've set up your SMTP credentials in environment variables:")
    print("- SMTP_SERVER (e.g., smtp.gmail.com)")
    print("- SMTP_PORT (e.g., 587)")
    print("- SMTP_USERNAME (your email)")
    print("- SMTP_PASSWORD (your app password)")
    print("- EMAIL_FROM (sender email)")
    print("- EMAIL_FROM_NAME (sender name)")
    
    # You can uncomment the following lines to test actual email sending
    # test_email = "your-test-email@example.com"
    # success = await send_verification_email(test_email, "TestUser", token)
    # if success:
    #     print("✅ Email sent successfully!")
    # else:
    #     print("❌ Failed to send email. Check your SMTP configuration.")
    
    print("\nEmail verification system is ready!")
    print("To test with real emails, update the SMTP credentials and uncomment the test code.")

if __name__ == "__main__":
    asyncio.run(test_email_functionality()) 