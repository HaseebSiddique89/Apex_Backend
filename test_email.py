#!/usr/bin/env python3
"""
Test email functionality
"""
import asyncio
from backend.utils.email_utils import generate_verification_token, send_verification_email

async def test_email_functionality():
    """Test the email verification functionality"""
    print("Testing email verification functionality...")
    
    # Test token generation
    token = generate_verification_token()
    print(f"Generated verification token: {token}")
    print(f"Token length: {len(token)}")
    
    # Test email sending to a different email
    print("\nTesting email sending...")
    test_email = "haseebsiddique807@gmail.com"  # Send to the user's email
    success = await send_verification_email(test_email, "TestUser", token)
    
    if success:
        print("✅ Email sent successfully!")
        print(f"Check {test_email} inbox for the verification email.")
    else:
        print("❌ Failed to send email. Check your SMTP configuration.")
    
    print("\nEmail verification system is ready!")

if __name__ == "__main__":
    asyncio.run(test_email_functionality()) 