import os
import requests
import sys

print("="*60)
print("🔍 BREVO API STANDALONE TEST")
print("="*60)

# Try to get API key from environment
api_key = os.environ.get('BREVO_SMTP_KEY')

if not api_key:
    print("❌ BREVO_SMTP_KEY not found in environment!")
    print("\nPlease set it manually for testing:")
    api_key = input("Paste your Brevo API key: ").strip()

if not api_key:
    print("❌ No API key provided. Exiting.")
    sys.exit(1)

print(f"\n✅ API Key found!")
print(f"   Length: {len(api_key)} characters")
print(f"   Starts with: {api_key[:20]}...")
print(f"   Ends with: ...{api_key[-10:]}")
print(f"   Format check: {'✅ Starts with xsmtpsib' if api_key.startswith('xsmtpsib') else '❌ Does NOT start with xsmtpsib'}")

# Test 1: Get account info
print("\n📡 Test 1: Getting account information...")
headers = {
    "api-key": api_key.strip(),
    "accept": "application/json"
}

try:
    response = requests.get(
        "https://api.brevo.com/v3/account",
        headers=headers,
        timeout=10
    )
    
    if response.status_code == 200:
        print("✅ SUCCESS! API key is valid!")
        account = response.json()
        print(f"   Account email: {account.get('email', 'N/A')}")
        print(f"   Company name: {account.get('companyName', 'N/A')}")
    else:
        print(f"❌ FAILED! Status code: {response.status_code}")
        print(f"   Response: {response.text}")
        
        # Try to diagnose the issue
        if response.status_code == 401:
            print("\n🔍 DIAGNOSIS: 401 Unauthorized")
            print("   Possible reasons:")
            print("   - API key is incorrect or expired")
            print("   - API key has spaces or extra characters")
            print("   - API key doesn't have the right permissions")
            
except requests.exceptions.ConnectionError:
    print("❌ Connection error - cannot reach Brevo API")
except Exception as e:
    print(f"❌ Unexpected error: {e}")

# Test 2: Try to send a test email (optional)
print("\n📡 Test 2: Would you like to send a test email? (y/n)")
choice = input().strip().lower()

if choice == 'y':
    test_email = input("Enter email address to send test to: ").strip()
    
    if test_email:
        print(f"Sending test email to {test_email}...")
        
        email_data = {
            "sender": {
                "name": "StudyBud Test",
                "email": "noreply@studybud.com"
            },
            "to": [
                {
                    "email": test_email,
                    "name": "Test User"
                }
            ],
            "subject": "Test Email from StudyBud",
            "htmlContent": "<h1>Test Email</h1><p>If you receive this, Brevo is working!</p>",
        }
        
        headers = {
            "accept": "application/json",
            "api-key": api_key.strip(),
            "content-type": "application/json"
        }
        
        try:
            response = requests.post(
                "https://api.brevo.com/v3/smtp/email",
                json=email_data,
                headers=headers,
                timeout=30
            )
            
            if response.status_code == 201:
                print("✅ Test email sent successfully!")
            else:
                print(f"❌ Failed to send test email: {response.status_code}")
                print(f"   Response: {response.text}")
        except Exception as e:
            print(f"❌ Error sending test email: {e}")

print("\n" + "="*60)