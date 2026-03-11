from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
import logging
import requests
import os

logger = logging.getLogger(__name__)

def send_email_brevo_api(subject, to_email, html_content, text_content=None, user=None):
    """
    Send email using Brevo API (not SMTP) - This WILL work!
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
            "email": "noreply@studybud.com"
        },
        "to": [
            {
                "email": to_email,
                "name": recipient_name  # <-- Now with a name!
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
    """Return base CSS styles for all emails"""
    return """
        /* Base Styles */
        body {
            font-family: 'DM Sans', 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
            background-color: #2d2d39;
            margin: 0;
            padding: 0;
            -webkit-font-smoothing: antialiased;
            -moz-osx-font-smoothing: grayscale;
        }
        
        .email-container {
            max-width: 600px;
            margin: 30px auto;
            background: linear-gradient(145deg, #3f4156 0%, #2d2d39 100%);
            border-radius: 24px;
            overflow: hidden;
            box-shadow: 0 20px 40px rgba(0, 0, 0, 0.4), 0 8px 16px rgba(0, 0, 0, 0.3);
            border: 1px solid #51546e;
        }
        
        /* Header with Gradient */
        .email-header {
            background: linear-gradient(135deg, #71c6dd 0%, #4fa3b8 100%);
            padding: 40px 30px;
            text-align: center;
            position: relative;
            overflow: hidden;
        }
        
        .email-header::before {
            content: '';
            position: absolute;
            top: -50%;
            right: -50%;
            width: 200%;
            height: 200%;
            background: radial-gradient(circle, rgba(255,255,255,0.15) 0%, transparent 70%);
            animation: shimmer 8s infinite;
        }
        
        @keyframes shimmer {
            0% { transform: translate(0, 0) rotate(0deg); }
            100% { transform: translate(-10%, -10%) rotate(5deg); }
        }
        
        .logo-container {
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 15px;
            margin-bottom: 10px;
        }
        
        .logo-icon {
            width: 50px;
            height: 50px;
            background: #2d2d39;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            box-shadow: 0 8px 16px rgba(0, 0, 0, 0.3);
            border: 3px solid #e5e5e5;
        }
        
        .logo-icon svg {
            width: 30px;
            height: 30px;
            fill: #71c6dd;
        }
        
        .logo-text {
            font-size: 36px;
            font-weight: 700;
            color: #2d2d39;
            text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.2);
            letter-spacing: -0.5px;
        }
        
        .header-tagline {
            color: #2d2d39;
            font-size: 16px;
            font-weight: 500;
            opacity: 0.9;
            text-transform: uppercase;
            letter-spacing: 2px;
            margin-top: 5px;
        }
        
        /* Content Area */
        .email-content {
            padding: 40px 35px;
            background: rgba(255, 255, 255, 0.02);
        }
        
        .greeting {
            font-size: 24px;
            font-weight: 600;
            color: #e5e5e5;
            margin-bottom: 15px;
            display: flex;
            align-items: center;
            gap: 10px;
        }
        
        .greeting-emoji {
            font-size: 28px;
            filter: drop-shadow(0 4px 4px rgba(0,0,0,0.3));
        }
        
        .message-text {
            color: #b2bdbd;
            font-size: 16px;
            line-height: 1.6;
            margin-bottom: 25px;
        }
        
        /* Verification Code Box */
        .code-container {
            background: linear-gradient(145deg, #51546e 0%, #3f4156 100%);
            border-radius: 50px;
            padding: 25px;
            margin: 30px 0;
            text-align: center;
            border: 2px solid #71c6dd;
            box-shadow: 0 15px 25px rgba(113, 198, 221, 0.2);
            position: relative;
            overflow: hidden;
        }
        
        .code-container::before {
            content: '';
            position: absolute;
            top: -50%;
            left: -50%;
            width: 200%;
            height: 200%;
            background: radial-gradient(circle, rgba(113,198,221,0.1) 0%, transparent 70%);
            animation: rotate 10s linear infinite;
        }
        
        @keyframes rotate {
            from { transform: rotate(0deg); }
            to { transform: rotate(360deg); }
        }
        
        .code-label {
            color: #e5e5e5;
            font-size: 14px;
            text-transform: uppercase;
            letter-spacing: 3px;
            margin-bottom: 15px;
            position: relative;
            z-index: 1;
        }
        
        .verification-code {
            font-size: 54px;
            font-weight: 800;
            color: #71c6dd;
            text-shadow: 0 0 20px rgba(113, 198, 221, 0.5);
            letter-spacing: 8px;
            margin: 10px 0;
            position: relative;
            z-index: 1;
            font-family: 'Courier New', monospace;
        }
        
        .code-expiry {
            color: #b2bdbd;
            font-size: 13px;
            margin-top: 15px;
            position: relative;
            z-index: 1;
        }
        
        /* Password Reset Button */
        .button-container {
            text-align: center;
            margin: 40px 0;
        }
        
        .reset-button {
            display: inline-block;
            padding: 18px 45px;
            background: linear-gradient(135deg, #71c6dd 0%, #4fa3b8 100%);
            color: #2d2d39;
            text-decoration: none;
            border-radius: 50px;
            font-weight: 700;
            font-size: 18px;
            letter-spacing: 1px;
            box-shadow: 0 10px 20px rgba(113, 198, 221, 0.4);
            border: 2px solid #e5e5e5;
            transition: all 0.3s ease;
            position: relative;
            overflow: hidden;
        }
        
        .reset-button:hover {
            transform: translateY(-3px);
            box-shadow: 0 15px 30px rgba(113, 198, 221, 0.6);
        }
        
        .reset-button::after {
            content: '→';
            margin-left: 10px;
            font-size: 20px;
            transition: transform 0.3s ease;
            display: inline-block;
        }
        
        .reset-button:hover::after {
            transform: translateX(5px);
        }
        
        /* Features Section */
        .features-section {
            display: flex;
            justify-content: space-between;
            margin: 40px 0;
            padding: 20px 0;
            border-top: 2px solid #51546e;
            border-bottom: 2px solid #51546e;
        }
        
        .feature-item {
            text-align: center;
            flex: 1;
        }
        
        .feature-icon {
            font-size: 24px;
            margin-bottom: 10px;
            filter: drop-shadow(0 4px 4px rgba(0,0,0,0.3));
        }
        
        .feature-text {
            color: #b2bdbd;
            font-size: 12px;
            font-weight: 500;
            text-transform: uppercase;
            letter-spacing: 1px;
        }
        
        /* Info Box */
        .info-box {
            background: rgba(81, 84, 110, 0.3);
            border-radius: 16px;
            padding: 25px;
            margin: 30px 0;
            border: 1px solid #51546e;
        }
        
        .info-title {
            color: #71c6dd;
            font-size: 18px;
            font-weight: 600;
            margin-bottom: 15px;
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
            font-size: 14px;
            margin-bottom: 12px;
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
        
        /* Footer */
        .email-footer {
            background: #2d2d39;
            padding: 30px 35px;
            text-align: center;
            border-top: 2px solid #51546e;
        }
        
        .footer-links {
            display: flex;
            justify-content: center;
            gap: 30px;
            margin-bottom: 20px;
        }
        
        .footer-link {
            color: #b2bdbd;
            text-decoration: none;
            font-size: 14px;
            transition: color 0.3s ease;
        }
        
        .footer-link:hover {
            color: #71c6dd;
        }
        
        .social-links {
            display: flex;
            justify-content: center;
            gap: 20px;
            margin: 25px 0;
        }
        
        .social-link {
            width: 40px;
            height: 40px;
            background: #3f4156;
            border-radius: 50%;
            display: inline-flex;
            align-items: center;
            justify-content: center;
            transition: all 0.3s ease;
            border: 2px solid transparent;
        }
        
        .social-link:hover {
            background: #71c6dd;
            border-color: #e5e5e5;
            transform: translateY(-3px);
        }
        
        .social-link svg {
            width: 20px;
            height: 20px;
            fill: #e5e5e5;
        }
        
        .social-link:hover svg {
            fill: #2d2d39;
        }
        
        .copyright {
            color: #696d97;
            font-size: 13px;
            margin-top: 25px;
        }
        
        /* Responsive */
        @media (max-width: 600px) {
            .email-container {
                margin: 15px;
                border-radius: 16px;
            }
            
            .email-header {
                padding: 30px 20px;
            }
            
            .logo-text {
                font-size: 28px;
            }
            
            .verification-code {
                font-size: 40px;
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

def send_verification_email(user, verification_code):
    """Send email verification code with stunning design"""
    if site_url is None:
        site_url = "https://studybud-kxsv.onrender.com"  # Your default URL
    subject = "✨ Verify Your StudyBud Account"
    
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
                    We're thrilled to have you join the StudyBud community! 
                    To get started, please verify your email address using the code below.
                </div>
                
                <!-- Verification Code Box -->
                <div class="code-container">
                    <div class="code-label">Verification Code</div>
                    <div class="verification-code">{verification_code}</div>
                    <div class="code-expiry">⏰ Expires in 24 hours</div>
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
                        What's Next?
                    </div>
                    <ul class="info-list">
                        <li>Complete your profile with a photo and bio</li>
                        <li>Join study rooms that match your interests</li>
                        <li>Connect with study partners worldwide</li>
                        <li>Create your own study groups</li>
                    </ul>
                </div>
                
                <div class="message-text" style="text-align: center; font-style: italic;">
                    "Alone we can do so little; together we can do so much."
                </div>
            </div>
            
            <!-- Footer -->
            <div class="email-footer">
                <div class="footer-links">
    <a href="{{ site_url }}/about-us/" class="footer-link">About Us</a>
    <a href="{{ site_url }}/privacy-policy/" class="footer-link">Privacy Policy</a>
    <a href="{{ site_url }}/terms-of-service/" class="footer-link">Terms of Service</a>
    <a href="{{ site_url }}/help-center/" class="footer-link">Help Center</a>
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
                            <path d="M12 2.163c3.204 0 3.584.012 4.85.07 3.252.148 4.771 1.691 4.919 4.919.058 1.265.069 1.645.069 4.849 0 3.205-.012 3.584-.069 4.849-.149 3.225-1.664 4.771-4.919 4.919-1.266.058-1.644.07-4.85.07-3.204 0-3.584-.012-4.849-.07-3.26-.149-4.771-1.699-4.919-4.92-.058-1.265-.07-1.644-.07-4.849 0-3.204.013-3.583.07-4.849.149-3.227 1.664-4.771 4.919-4.919 1.266-.057 1.645-.069 4.849-.069zm0-2.163c-3.259 0-3.667.014-4.947.072-4.358.2-6.78 2.618-6.98 6.98-.059 1.281-.073 1.689-.073 4.948 0 3.259.014 3.668.072 4.948.2 4.358 2.618 6.78 6.98 6.98 1.281.058 1.689.072 4.948.072 3.259 0 3.668-.014 4.948-.072 4.354-.2 6.782-2.618 6.979-6.98.059-1.28.073-1.689.073-4.948 0-3.259-.014-3.667-.072-4.947-.196-4.354-2.617-6.78-6.979-6.98-1.281-.059-1.69-.073-4.949-.073zM5.838 12a6.162 6.162 0 1 1 12.324 0 6.162 6.162 0 0 1-12.324 0zM12 16a4 4 0 1 1 0-8 4 4 0 0 1 0 8zm4.965-10.405a1.44 1.44 0 1 1 2.881.001 1.44 1.44 0 0 1-2.881-.001z"/>
                        </svg>
                    </a>
                </div>
                
                <div class="copyright">
                    © {verification_code[:4]} StudyBud. All rights reserved.
                    <br>
                     Study Rooms • Active Users • Support
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
- Complete your profile
- Join study rooms
- Connect with study partners
- Create your own groups

© 2026 StudyBud. All rights reserved.
    """
    
    return send_email_brevo_api(
        subject=subject,
        to_email=user.email,
        html_content=html_content,
        text_content=text_content,
        user=user
    )


def send_password_reset_email(user, reset_link):
    """Send password reset email with stunning design"""
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
                    to create a new password.
                </div>
                
                <!-- Reset Button -->
                <div class="button-container">
                    <a href="{reset_link}" class="reset-button">
                        Reset Password
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
                <div style="background: rgba(252, 75, 11, 0.1); border-radius: 12px; padding: 20px; margin: 30px 0; border-left: 4px solid #fc4b0b;">
                    <div style="display: flex; align-items: center; gap: 15px;">
                        <span style="font-size: 24px;">⚠️</span>
                        <div>
                            <strong style="color: #fc4b0b; font-size: 16px;">Didn't request this?</strong>
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
    <a href="{{ site_url }}/about-us/" class="footer-link">About Us</a>
    <a href="{{ site_url }}/privacy-policy/" class="footer-link">Privacy Policy</a>
    <a href="{{ site_url }}/terms-of-service/" class="footer-link">Terms of Service</a>
    <a href="{{ site_url }}/help-center/" class="footer-link">Help Center</a>
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
                            <path d="M12 2.163c3.204 0 3.584.012 4.85.07 3.252.148 4.771 1.691 4.919 4.919.058 1.265.069 1.645.069 4.849 0 3.205-.012 3.584-.069 4.849-.149 3.225-1.664 4.771-4.919 4.919-1.266.058-1.644.07-4.85.07-3.204 0-3.584-.012-4.849-.07-3.26-.149-4.771-1.699-4.919-4.92-.058-1.265-.07-1.644-.07-4.849 0-3.204.013-3.583.07-4.849.149-3.227 1.664-4.771 4.919-4.919 1.266-.057 1.645-.069 4.849-.069zm0-2.163c-3.259 0-3.667.014-4.947.072-4.358.2-6.78 2.618-6.98 6.98-.059 1.281-.073 1.689-.073 4.948 0 3.259.014 3.668.072 4.948.2 4.358 2.618 6.78 6.98 6.98 1.281.058 1.689.072 4.948.072 3.259 0 3.668-.014 4.948-.072 4.354-.2 6.782-2.618 6.979-6.98.059-1.28.073-1.689.073-4.948 0-3.259-.014-3.667-.072-4.947-.196-4.354-2.617-6.78-6.979-6.98-1.281-.059-1.69-.073-4.949-.073zM5.838 12a6.162 6.162 0 1 1 12.324 0 6.162 6.162 0 0 1-12.324 0zM12 16a4 4 0 1 1 0-8 4 4 0 0 1 0 8zm4.965-10.405a1.44 1.44 0 1 1 2.881.001 1.44 1.44 0 0 1-2.881-.001z"/>
                        </svg>
                    </a>
                </div>
                
                <div class="copyright">
                    © 2026 StudyBud. All rights reserved.
                    <br>
                    Secure • Reliable • Community-Driven
                </div>
            </div>
        </div>
    </body>
    </html>
    """
    
    text_content = f"""
PASSWORD RESET REQUEST - STUDY BUDDY

Hello @{user.username},

We received a request to reset your password.

Click this link to reset your password:
{reset_link}

This link will expire in 24 hours.

SECURITY TIPS:
- Never share this link with anyone
- Create a strong password
- Enable two-factor authentication

If you didn't request this, please ignore this email.

© 2026 StudyBud. All rights reserved.
    """
    
    return send_email_brevo_api(
        subject=subject,
        to_email=user.email,
        html_content=html_content,
        text_content=text_content
    )