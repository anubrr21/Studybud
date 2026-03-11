from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
import logging
import requests
import os

logger = logging.getLogger(__name__)

def send_email_brevo_api(subject, to_email, html_content, text_content=None, user=None):
    """
    Send email using Brevo API (not SMTP)
    """
    api_key = os.environ.get('BREVO_API_KEY')
    
    if not api_key:
        logger.error("BREVO_API_KEY not found in environment")
        return {'success': False, 'error': 'API key not configured'}
    
    # Get recipient name
    recipient_name = "StudyBud User"
    if user and hasattr(user, 'username'):
        recipient_name = f"@{user.username}"
    
    # Prepare the email data
    data = {
        "sender": {
            "name": "StudyBud",
            "email": "anubratabhattacharyya81@gmail.com"
        },
        "to": [
            {
                "email": to_email,
                "name": recipient_name
            }
        ],
        "subject": subject,
        "htmlContent": html_content,
    }
    
    if text_content:
        data["textContent"] = text_content
    
    headers = {
        "accept": "application/json",
        "api-key": api_key.strip(),
        "content-type": "application/json"
    }
    
    try:
        print(f"Sending email to: {to_email} with name: {recipient_name}")
        response = requests.post(
            "https://api.brevo.com/v3/smtp/email",
            json=data,
            headers=headers,
            timeout=30
        )
        
        if response.status_code == 201:
            logger.info(f"✅ Email sent successfully to {to_email}")
            return {'success': True}
        else:
            logger.error(f"❌ Brevo API error: {response.status_code} - {response.text}")
            return {'success': False, 'error': f"API error: {response.status_code}"}
            
    except Exception as e:
        logger.error(f"❌ Error: {e}")
        return {'success': False, 'error': str(e)}

def get_base_styles():
    """Return email-client-friendly CSS styles"""
    return """
        /* Base Styles - Email Safe */
        body {
            font-family: 'DM Sans', 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
            background-color: #1a1a2a;
            margin: 0;
            padding: 0;
        }
        
        .email-container {
            max-width: 600px;
            margin: 0 auto;
            background-color: #2d2d39;
            border-radius: 24px;
            overflow: hidden;
            border: 1px solid #51546e;
        }
        
        /* Header */
        .email-header {
            background-color: #71c6dd;
            padding: 40px 30px;
            text-align: center;
            border-bottom: 3px solid #ffffff;
        }
        
        .logo-container {
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 15px;
            margin-bottom: 15px;
        }
        
        .logo-icon {
            width: 60px;
            height: 60px;
            background-color: #2d2d39;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            border: 3px solid #ffffff;
        }
        
        .logo-icon svg {
            width: 35px;
            height: 35px;
            fill: #71c6dd;
        }
        
        .logo-text {
            font-size: 42px;
            font-weight: 800;
            color: #1a1a2a;
        }
        
        .header-tagline {
            color: #1a1a2a;
            font-size: 16px;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 2px;
            background-color: rgba(255,255,255,0.3);
            display: inline-block;
            padding: 8px 20px;
            border-radius: 50px;
        }
        
        /* Content */
        .email-content {
            padding: 40px 35px;
            background-color: #2d2d39;
        }
        
        .greeting {
            font-size: 28px;
            font-weight: 700;
            color: #ffffff;
            margin-bottom: 20px;
            display: flex;
            align-items: center;
            gap: 10px;
        }
        
        .greeting-emoji {
            font-size: 32px;
        }
        
        .message-text {
            color: #b2bdbd;
            font-size: 16px;
            line-height: 1.6;
            margin-bottom: 30px;
        }
        
        /* Verification Code Box */
        .code-container {
            background-color: #1a1a2a;
            border-radius: 20px;
            padding: 30px;
            margin: 30px 0;
            text-align: center;
            border: 2px solid #71c6dd;
        }
        
        .code-label {
            color: #ffffff;
            font-size: 14px;
            text-transform: uppercase;
            letter-spacing: 3px;
            margin-bottom: 15px;
        }
        
        .verification-code {
            font-size: 48px;
            font-weight: 800;
            color: #71c6dd;
            letter-spacing: 8px;
            margin: 10px 0;
            font-family: 'Courier New', monospace;
        }
        
        .code-expiry {
            color: #b2bdbd;
            font-size: 13px;
            margin-top: 10px;
        }
        
        /* Features Section */
        .features-section {
            display: flex;
            justify-content: space-between;
            gap: 15px;
            margin: 40px 0;
            padding: 25px 0;
            border-top: 2px solid #51546e;
            border-bottom: 2px solid #51546e;
        }
        
        .feature-item {
            text-align: center;
            flex: 1;
        }
        
        .feature-icon {
            font-size: 28px;
            margin-bottom: 8px;
        }
        
        .feature-text {
            color: #ffffff;
            font-size: 13px;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 1px;
        }
        
        /* Info Box */
        .info-box {
            background-color: #1a1a2a;
            border-radius: 20px;
            padding: 30px;
            margin: 30px 0;
            border: 1px solid #51546e;
        }
        
        .info-title {
            color: #71c6dd;
            font-size: 20px;
            font-weight: 700;
            margin-bottom: 20px;
            display: flex;
            align-items: center;
            gap: 10px;
        }
        
        .info-list {
            list-style: none;
            padding: 0;
            margin: 0;
        }
        
        .info-list li {
            color: #b2bdbd;
            font-size: 15px;
            margin-bottom: 15px;
            padding-left: 25px;
            position: relative;
        }
        
        .info-list li::before {
            content: '✓';
            color: #71c6dd;
            position: absolute;
            left: 0;
            font-weight: bold;
        }
        
        /* Quote */
        .quote-text {
            color: #71c6dd;
            font-size: 18px;
            font-style: italic;
            text-align: center;
            padding: 25px 0;
            border-top: 1px solid #51546e;
            margin-top: 30px;
        }
        
        /* Footer */
        .email-footer {
            background-color: #1a1a2a;
            padding: 40px 35px;
            text-align: center;
            border-top: 3px solid #71c6dd;
        }
        
        .footer-links {
            display: flex;
            justify-content: center;
            gap: 20px;
            margin-bottom: 30px;
            flex-wrap: wrap;
        }
        
        .footer-link {
            color: #b2bdbd;
            text-decoration: none;
            font-size: 14px;
        }
        
        .footer-link:hover {
            color: #71c6dd;
            text-decoration: underline;
        }
        
        .social-links {
            display: flex;
            justify-content: center;
            gap: 15px;
            margin: 25px 0;
        }
        
        .social-link {
            width: 40px;
            height: 40px;
            background-color: #2d2d39;
            border-radius: 50%;
            display: inline-flex;
            align-items: center;
            justify-content: center;
            border: 1px solid #71c6dd;
        }
        
        .social-link svg {
            width: 20px;
            height: 20px;
            fill: #71c6dd;
        }
        
        .copyright {
            color: #808080;
            font-size: 13px;
            margin-top: 25px;
            padding-top: 20px;
            border-top: 1px solid #51546e;
        }
        
        .copyright span {
            color: #71c6dd;
            font-weight: 600;
        }
        
        /* Reset Button */
        .reset-button {
            display: inline-block;
            padding: 15px 40px;
            background-color: #71c6dd;
            color: #1a1a2a;
            text-decoration: none;
            border-radius: 50px;
            font-weight: 700;
            font-size: 16px;
            border: 2px solid #ffffff;
        }
        
        /* Mobile Responsive */
        @media (max-width: 600px) {
            .email-header {
                padding: 30px 20px;
            }
            
            .logo-text {
                font-size: 32px;
            }
            
            .email-content {
                padding: 30px 20px;
            }
            
            .greeting {
                font-size: 24px;
            }
            
            .verification-code {
                font-size: 36px;
                letter-spacing: 5px;
            }
            
            .features-section {
                flex-direction: column;
                gap: 20px;
            }
            
            .footer-links {
                flex-direction: column;
                gap: 15px;
            }
        }
    """

def send_verification_email(user, verification_code, site_url=None):
    """Send email verification code with email-friendly design"""
    if site_url is None:
        site_url = "https://studybud-kxsv.onrender.com"
    
    subject = "✨ Welcome to StudyBud - Verify Your Account"
    
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            {get_base_styles()}
        </style>
    </head>
    <body>
        <div class="email-container">
            <!-- Header with Logo -->
            <div class="email-header">
                <div class="logo-container">
                    <div class="logo-icon">
                        <svg viewBox="0 0 24 24">
                            <path d="M20 2H4c-1.1 0-2 .9-2 2v18l4-4h14c1.1 0 2-.9 2-2V4c0-1.1-.9-2-2-2z"/>
                        </svg>
                    </div>
                    <div class="logo-text">StudyBud</div>
                </div>
                <div class="header-tagline">Your Learning Journey Starts Here</div>
            </div>
            
            <!-- Content -->
            <div class="email-content">
                <div class="greeting">
                    <span class="greeting-emoji">👋</span>
                    Welcome, @{user.username}!
                </div>
                
                <div class="message-text">
                    We're absolutely thrilled to have you join the StudyBud community! 
                    To unlock your account and start your learning journey, please verify 
                    your email address using the code below.
                </div>
                
                <!-- Verification Code Box -->
                <div class="code-container">
                    <div class="code-label">Verification Code</div>
                    <div class="verification-code">{verification_code}</div>
                    <div class="code-expiry">⏰ This code will expire in 24 hours</div>
                </div>
                
                <!-- Features Section -->
                <div class="features-section">
                    <div class="feature-item">
                        <div class="feature-icon">📚</div>
                        <div class="feature-text">Study Rooms</div>
                    </div>
                    <div class="feature-item">
                        <div class="feature-icon">💬</div>
                        <div class="feature-text">Live Chat</div>
                    </div>
                    <div class="feature-item">
                        <div class="feature-icon">🤝</div>
                        <div class="feature-text">Find Partners</div>
                    </div>
                </div>
                
                <!-- Info Box -->
                <div class="info-box">
                    <div class="info-title">
                        <span>✨</span>
                        Your Learning Journey Awaits
                    </div>
                    <ul class="info-list">
                        <li>Complete your profile with a photo and bio</li>
                        <li>Join study rooms that match your interests</li>
                        <li>Connect with study partners worldwide</li>
                        <li>Create your own study groups</li>
                    </ul>
                </div>
                
                <div class="quote-text">
                    "Alone we can do so little; together we can do so much."
                </div>
            </div>
            
            <!-- Footer -->
            <div class="email-footer">
                <div class="footer-links">
                    <a href="{site_url}/about-us/" class="footer-link">About Us</a>
                    <a href="{site_url}/privacy-policy/" class="footer-link">Privacy Policy</a>
                    <a href="{site_url}/terms-of-service/" class="footer-link">Terms of Service</a>
                    <a href="{site_url}/help-center/" class="footer-link">Help Center</a>
                </div>
                
                <div class="social-links">
                    <a href="#" class="social-link">
                        <svg viewBox="0 0 24 24">
                            <path d="M22 12c0-5.523-4.477-10-10-10S2 6.477 2 12c0 4.991 3.657 9.128 8.438 9.879v-6.99h-2.54V12h2.54V9.797c0-2.506 1.492-3.89 3.777-3.89 1.094 0 2.238.195 2.238.195v2.46h-1.26c-1.243 0-1.63.771-1.63 1.562V12h2.773l-.443 2.89h-2.33v6.99C18.343 21.128 22 16.991 22 12z"/>
                        </svg>
                    </a>
                    <a href="#" class="social-link">
                        <svg viewBox="0 0 24 24">
                            <path d="M22.46 6c-.77.35-1.6.58-2.46.69.88-.53 1.56-1.37 1.88-2.38-.83.5-1.75.85-2.72 1.05C18.37 4.5 17.26 4 16 4c-2.35 0-4.27 1.92-4.27 4.29 0 .34.04.67.11.98-3.56-.18-6.73-1.89-8.84-4.48-.37.63-.58 1.37-.58 2.15 0 1.49.75 2.81 1.91 3.56-.71 0-1.37-.2-1.95-.5v.03c0 2.08 1.48 3.82 3.44 4.21a4.22 4.22 0 0 1-1.93.07 4.28 4.28 0 0 0 4 2.98 8.52 8.52 0 0 1-5.33 1.84c-.34 0-.68-.02-1.02-.06C3.9 20.29 6.16 21 8.58 21c7.88 0 12.21-6.54 12.21-12.21 0-.19 0-.37-.01-.56.84-.6 1.56-1.36 2.14-2.23z"/>
                        </svg>
                    </a>
                    <a href="#" class="social-link">
                        <svg viewBox="0 0 24 24">
                            <path d="M12 2.163c3.204 0 3.584.012 4.85.07 3.252.148 4.771 1.691 4.919 4.919.058 1.265.069 1.645.069 4.849 0 3.205-.012 3.584-.069 4.849-.149 3.225-1.664 4.771-4.919 4.919-1.266.058-1.644.07-4.85.07-3.204 0-3.584-.012-4.849-.07-3.26-.149-4.771-1.699-4.919-4.92-.058-1.265-.07-1.644-.07-4.849 0-3.204.013-3.583.07-4.849.149-3.227 1.664-4.771 4.919-4.919 1.266-.057 1.645-.069 4.849-.069z"/>
                        </svg>
                    </a>
                </div>
                
                <div class="copyright">
                    <span>© {verification_code[:4]} StudyBud.</span> All rights reserved.
                    <br>
                    <span>✨ 300+ Study Rooms</span> • <span>👥 10K+ Active Users</span> • <span>⚡ 24/7 Support</span>
                </div>
            </div>
        </div>
    </body>
    </html>
    """
    
    text_content = f"""
WELCOME TO STUDYBUD!

Hello @{user.username},

Your verification code is: {verification_code}

Enter this code in the app to verify your email address.
This code will expire in 24 hours.

What's next?
- Complete your profile with a photo and bio
- Join study rooms that match your interests
- Connect with study partners worldwide
- Create your own study groups

Visit us at: {site_url}

© 2026 StudyBud. All rights reserved.
    """
    
    return send_email_brevo_api(
        subject=subject,
        to_email=user.email,
        html_content=html_content,
        text_content=text_content,
        user=user
    )

def send_password_reset_email(user, reset_link, site_url=None):
    """Send password reset email with email-friendly design"""
    if site_url is None:
        site_url = "https://studybud-kxsv.onrender.com"
    
    subject = "🔐 Reset Your StudyBud Password"
    
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            {get_base_styles()}
        </style>
    </head>
    <body>
        <div class="email-container">
            <!-- Header with Logo -->
            <div class="email-header">
                <div class="logo-container">
                    <div class="logo-icon">
                        <svg viewBox="0 0 24 24">
                            <path d="M20 2H4c-1.1 0-2 .9-2 2v18l4-4h14c1.1 0 2-.9 2-2V4c0-1.1-.9-2-2-2z"/>
                        </svg>
                    </div>
                    <div class="logo-text">StudyBud</div>
                </div>
                <div class="header-tagline">Your Learning Journey Starts Here</div>
            </div>
            
            <!-- Content -->
            <div class="email-content">
                <div class="greeting">
                    <span class="greeting-emoji">🔐</span>
                    Password Reset Request
                </div>
                
                <div class="message-text">
                    Hello @{user.username},
                    <br><br>
                    We received a request to reset your StudyBud password. 
                    Don't worry, it happens to the best of us! Click the button below 
                    to create a new password and get back to learning.
                </div>
                
                <!-- Reset Button -->
                <div style="text-align: center; margin: 40px 0;">
                    <a href="{reset_link}" class="reset-button">
                        Reset Password →
                    </a>
                </div>
                
                <!-- Security Info Box -->
                <div class="info-box">
                    <div class="info-title">
                        <span>🛡️</span>
                        Security Tips
                    </div>
                    <ul class="info-list">
                        <li>This link will expire in 24 hours</li>
                        <li>Never share this link with anyone</li>
                        <li>Create a strong password (8+ characters with mix of letters, numbers, and symbols)</li>
                        <li>Enable two-factor authentication for extra security</li>
                    </ul>
                </div>
                
                <!-- Warning Box -->
                <div style="background-color: rgba(252, 75, 11, 0.1); border-radius: 16px; padding: 20px; margin: 30px 0; border-left: 4px solid #fc4b0b;">
                    <div style="display: flex; align-items: center; gap: 15px;">
                        <span style="font-size: 24px;">⚠️</span>
                        <div>
                            <strong style="color: #fc4b0b; font-size: 15px;">Didn't request this?</strong>
                            <p style="color: #b2bdbd; font-size: 14px; margin-top: 5px;">
                                If you didn't request a password reset, please ignore this email 
                                or contact support if you're concerned about your account security.
                            </p>
                        </div>
                    </div>
                </div>
            </div>
            
            <!-- Footer -->
            <div class="email-footer">
                <div class="footer-links">
                    <a href="{site_url}/about-us/" class="footer-link">About Us</a>
                    <a href="{site_url}/privacy-policy/" class="footer-link">Privacy Policy</a>
                    <a href="{site_url}/terms-of-service/" class="footer-link">Terms of Service</a>
                    <a href="{site_url}/help-center/" class="footer-link">Help Center</a>
                </div>
                
                <div class="social-links">
                    <a href="#" class="social-link">
                        <svg viewBox="0 0 24 24">
                            <path d="M22 12c0-5.523-4.477-10-10-10S2 6.477 2 12c0 4.991 3.657 9.128 8.438 9.879v-6.99h-2.54V12h2.54V9.797c0-2.506 1.492-3.89 3.777-3.89 1.094 0 2.238.195 2.238.195v2.46h-1.26c-1.243 0-1.63.771-1.63 1.562V12h2.773l-.443 2.89h-2.33v6.99C18.343 21.128 22 16.991 22 12z"/>
                        </svg>
                    </a>
                    <a href="#" class="social-link">
                        <svg viewBox="0 0 24 24">
                            <path d="M22.46 6c-.77.35-1.6.58-2.46.69.88-.53 1.56-1.37 1.88-2.38-.83.5-1.75.85-2.72 1.05C18.37 4.5 17.26 4 16 4c-2.35 0-4.27 1.92-4.27 4.29 0 .34.04.67.11.98-3.56-.18-6.73-1.89-8.84-4.48-.37.63-.58 1.37-.58 2.15 0 1.49.75 2.81 1.91 3.56-.71 0-1.37-.2-1.95-.5v.03c0 2.08 1.48 3.82 3.44 4.21a4.22 4.22 0 0 1-1.93.07 4.28 4.28 0 0 0 4 2.98 8.52 8.52 0 0 1-5.33 1.84c-.34 0-.68-.02-1.02-.06C3.9 20.29 6.16 21 8.58 21c7.88 0 12.21-6.54 12.21-12.21 0-.19 0-.37-.01-.56.84-.6 1.56-1.36 2.14-2.23z"/>
                        </svg>
                    </a>
                    <a href="#" class="social-link">
                        <svg viewBox="0 0 24 24">
                            <path d="M12 2.163c3.204 0 3.584.012 4.85.07 3.252.148 4.771 1.691 4.919 4.919.058 1.265.069 1.645.069 4.849 0 3.205-.012 3.584-.069 4.849-.149 3.225-1.664 4.771-4.919 4.919-1.266.058-1.644.07-4.85.07-3.204 0-3.584-.012-4.849-.07-3.26-.149-4.771-1.699-4.919-4.92-.058-1.265-.07-1.644-.07-4.849 0-3.204.013-3.583.07-4.849.149-3.227 1.664-4.771 4.919-4.919 1.266-.057 1.645-.069 4.849-.069z"/>
                        </svg>
                    </a>
                </div>
                
                <div class="copyright">
                    <span>© 2026 StudyBud.</span> All rights reserved.
                    <br>
                    <span>🔐 Secure</span> • <span>⚡ Reliable</span> • <span>🌍 Community-Driven</span>
                </div>
            </div>
        </div>
    </body>
    </html>
    """
    
    text_content = f"""
PASSWORD RESET REQUEST - STUDY BUDDY

Hello @{user.username},

Click this link to reset your password:
{reset_link}

This link will expire in 24 hours.

SECURITY TIPS:
- Never share this link with anyone
- Create a strong password
- Enable two-factor authentication

If you didn't request this, please ignore this email.

Visit us at: {site_url}

© 2026 StudyBud. All rights reserved.
    """
    
    return send_email_brevo_api(
        subject=subject,
        to_email=user.email,
        html_content=html_content,
        text_content=text_content,
        user=user
    )