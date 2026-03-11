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
    """Return enhanced base CSS styles with advanced animations"""
    return """
        /* Import Google Fonts */
        @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;700;800&display=swap');
        
        /* Base Styles */
        body {
            font-family: 'DM Sans', 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
            background: linear-gradient(135deg, #1a1a2a 0%, #2d2d39 100%);
            margin: 0;
            padding: 20px;
            -webkit-font-smoothing: antialiased;
            -moz-osx-font-smoothing: grayscale;
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        
        /* Main Container with 3D Effect */
        .email-container {
            max-width: 600px;
            margin: 20px auto;
            background: linear-gradient(145deg, #2d2d39 0%, #23232f 100%);
            border-radius: 40px;
            overflow: hidden;
            box-shadow: 
                0 30px 60px rgba(0, 0, 0, 0.6),
                0 0 0 2px #51546e inset,
                0 0 20px rgba(113, 198, 221, 0.3);
            border: 1px solid rgba(113, 198, 221, 0.2);
            transform: perspective(1000px) rotateX(1deg);
            transition: all 0.5s ease;
            animation: float 6s ease-in-out infinite;
        }
        
        @keyframes float {
            0%, 100% { transform: perspective(1000px) rotateX(1deg) translateY(0); }
            50% { transform: perspective(1000px) rotateX(0.5deg) translateY(-10px); }
        }
        
        /* Header with Advanced Gradient and 3D Effect */
        .email-header {
            background: linear-gradient(135deg, #71c6dd 0%, #4fa3b8 50%, #2d7a8c 100%);
            padding: 50px 30px;
            text-align: center;
            position: relative;
            overflow: hidden;
            box-shadow: 0 10px 30px rgba(113, 198, 221, 0.4);
            border-bottom: 3px solid #ffffff20;
        }
        
        .email-header::before {
            content: '';
            position: absolute;
            top: -50%;
            left: -50%;
            width: 200%;
            height: 200%;
            background: radial-gradient(circle, rgba(255,255,255,0.3) 0%, transparent 60%);
            animation: shimmer 10s ease-in-out infinite;
            transform: rotate(30deg);
        }
        
        .email-header::after {
            content: '';
            position: absolute;
            bottom: -50%;
            right: -50%;
            width: 200%;
            height: 200%;
            background: radial-gradient(circle, rgba(113,198,221,0.3) 0%, transparent 60%);
            animation: shimmerReverse 12s ease-in-out infinite;
            transform: rotate(-20deg);
        }
        
        @keyframes shimmer {
            0%, 100% { transform: rotate(30deg) translate(-10%, -10%); }
            50% { transform: rotate(30deg) translate(10%, 10%); }
        }
        
        @keyframes shimmerReverse {
            0%, 100% { transform: rotate(-20deg) translate(10%, 10%); }
            50% { transform: rotate(-20deg) translate(-10%, -10%); }
        }
        
        /* Logo Container with 3D Flip Effect */
        .logo-container {
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 15px;
            margin-bottom: 15px;
            position: relative;
            z-index: 10;
            animation: logoGlow 3s ease-in-out infinite;
        }
        
        @keyframes logoGlow {
            0%, 100% { filter: drop-shadow(0 0 10px rgba(255,255,255,0.5)); }
            50% { filter: drop-shadow(0 0 20px rgba(113,198,221,0.8)); }
        }
        
        .logo-icon {
            width: 70px;
            height: 70px;
            background: linear-gradient(135deg, #2d2d39 0%, #1a1a2a 100%);
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            box-shadow: 
                0 10px 20px rgba(0, 0, 0, 0.4),
                0 0 0 3px #71c6dd,
                0 0 0 6px rgba(113, 198, 221, 0.3);
            border: 2px solid #ffffff;
            transform: rotateY(0deg);
            transition: transform 0.5s ease;
            animation: rotate3D 8s ease-in-out infinite;
        }
        
        @keyframes rotate3D {
            0%, 100% { transform: rotateY(0deg) scale(1); }
            25% { transform: rotateY(10deg) scale(1.05); }
            75% { transform: rotateY(-10deg) scale(1.05); }
        }
        
        .logo-icon svg {
            width: 40px;
            height: 40px;
            fill: #71c6dd;
            filter: drop-shadow(0 0 10px rgba(113,198,221,0.8));
            animation: pulse 2s ease-in-out infinite;
        }
        
        @keyframes pulse {
            0%, 100% { transform: scale(1); }
            50% { transform: scale(1.1); }
        }
        
        .logo-text {
            font-size: 48px;
            font-weight: 800;
            background: linear-gradient(135deg, #ffffff 0%, #2d2d39 80%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            text-shadow: 
                2px 2px 4px rgba(0, 0, 0, 0.3),
                0 0 20px rgba(255,255,255,0.5);
            letter-spacing: -1px;
            position: relative;
            animation: textFloat 4s ease-in-out infinite;
        }
        
        @keyframes textFloat {
            0%, 100% { transform: translateY(0); }
            50% { transform: translateY(-5px); }
        }
        
        .header-tagline {
            color: rgba(255,255,255,0.95);
            font-size: 16px;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 4px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
            background: rgba(45,45,57,0.3);
            display: inline-block;
            padding: 8px 20px;
            border-radius: 50px;
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255,255,255,0.2);
            animation: taglinePulse 3s ease-in-out infinite;
        }
        
        @keyframes taglinePulse {
            0%, 100% { opacity: 0.9; transform: scale(1); }
            50% { opacity: 1; transform: scale(1.05); }
        }
        
        /* Content Area with Glass Morphism */
        .email-content {
            padding: 50px 40px;
            background: rgba(45, 45, 57, 0.8);
            backdrop-filter: blur(10px);
            position: relative;
        }
        
        .email-content::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: radial-gradient(circle at 20% 30%, rgba(113,198,221,0.1) 0%, transparent 50%);
            pointer-events: none;
        }
        
        .greeting {
            font-size: 32px;
            font-weight: 700;
            color: #ffffff;
            margin-bottom: 20px;
            display: flex;
            align-items: center;
            gap: 15px;
            animation: slideInLeft 0.8s ease-out;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }
        
        @keyframes slideInLeft {
            from {
                opacity: 0;
                transform: translateX(-30px);
            }
            to {
                opacity: 1;
                transform: translateX(0);
            }
        }
        
        .greeting-emoji {
            font-size: 40px;
            filter: drop-shadow(0 0 15px rgba(113,198,221,0.8));
            animation: bounce 2s ease-in-out infinite;
        }
        
        @keyframes bounce {
            0%, 100% { transform: translateY(0); }
            50% { transform: translateY(-10px); }
        }
        
        .message-text {
            color: #e0e0e0;
            font-size: 18px;
            line-height: 1.8;
            margin-bottom: 35px;
            animation: slideInRight 0.8s ease-out 0.2s both;
            text-shadow: 1px 1px 2px rgba(0,0,0,0.2);
        }
        
        @keyframes slideInRight {
            from {
                opacity: 0;
                transform: translateX(30px);
            }
            to {
                opacity: 1;
                transform: translateX(0);
            }
        }
        
        /* Enhanced Verification Code Box */
        .code-container {
            background: linear-gradient(145deg, #2d2d39 0%, #1a1a2a 100%);
            border-radius: 60px;
            padding: 40px;
            margin: 40px 0;
            text-align: center;
            border: 3px solid #71c6dd;
            box-shadow: 
                0 20px 40px rgba(113, 198, 221, 0.4),
                0 0 0 5px rgba(113,198,221,0.2),
                inset 0 0 30px rgba(113,198,221,0.3);
            position: relative;
            overflow: hidden;
            animation: codePulse 3s ease-in-out infinite;
        }
        
        @keyframes codePulse {
            0%, 100% { box-shadow: 0 20px 40px rgba(113,198,221,0.4), 0 0 0 5px rgba(113,198,221,0.2); }
            50% { box-shadow: 0 25px 50px rgba(113,198,221,0.6), 0 0 0 8px rgba(113,198,221,0.3); }
        }
        
        .code-container::before {
            content: '';
            position: absolute;
            top: -50%;
            left: -50%;
            width: 200%;
            height: 200%;
            background: radial-gradient(circle, rgba(113,198,221,0.2) 0%, transparent 70%);
            animation: rotate3D 15s linear infinite;
        }
        
        .code-label {
            color: #ffffff;
            font-size: 16px;
            text-transform: uppercase;
            letter-spacing: 6px;
            margin-bottom: 20px;
            position: relative;
            z-index: 2;
            font-weight: 600;
            text-shadow: 0 0 10px rgba(113,198,221,0.5);
        }
        
        .verification-code {
            font-size: 72px;
            font-weight: 800;
            background: linear-gradient(135deg, #71c6dd 0%, #ffffff 80%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            text-shadow: 
                0 0 30px rgba(113,198,221,0.8),
                0 0 60px rgba(113,198,221,0.4);
            letter-spacing: 12px;
            margin: 15px 0;
            position: relative;
            z-index: 2;
            font-family: 'Courier New', monospace;
            animation: glowPulse 2s ease-in-out infinite;
        }
        
        @keyframes glowPulse {
            0%, 100% { filter: drop-shadow(0 0 20px rgba(113,198,221,0.8)); }
            50% { filter: drop-shadow(0 0 40px rgba(113,198,221,1)); }
        }
        
        .code-expiry {
            color: #b0b0b0;
            font-size: 14px;
            margin-top: 15px;
            position: relative;
            z-index: 2;
            font-weight: 500;
            letter-spacing: 1px;
        }
        
        /* Features Section with 3D Cards */
        .features-section {
            display: flex;
            justify-content: space-between;
            gap: 20px;
            margin: 50px 0;
            padding: 30px 0;
            border-top: 2px solid rgba(81, 84, 110, 0.5);
            border-bottom: 2px solid rgba(81, 84, 110, 0.5);
            animation: fadeInUp 1s ease-out 0.4s both;
        }
        
        @keyframes fadeInUp {
            from {
                opacity: 0;
                transform: translateY(20px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }
        
        .feature-item {
            text-align: center;
            flex: 1;
            padding: 20px 10px;
            background: linear-gradient(145deg, rgba(45,45,57,0.8) 0%, rgba(26,26,42,0.8) 100%);
            border-radius: 20px;
            border: 1px solid rgba(113,198,221,0.3);
            backdrop-filter: blur(5px);
            transition: all 0.3s ease;
            animation: cardFloat 4s ease-in-out infinite;
            animation-delay: calc(var(--i) * 0.2s);
        }
        
        .feature-item:hover {
            transform: translateY(-10px) scale(1.05);
            border-color: #71c6dd;
            box-shadow: 0 20px 30px rgba(113,198,221,0.3);
        }
        
        .feature-item:nth-child(1) { --i: 1; }
        .feature-item:nth-child(2) { --i: 2; }
        .feature-item:nth-child(3) { --i: 3; }
        
        @keyframes cardFloat {
            0%, 100% { transform: translateY(0); }
            50% { transform: translateY(-5px); }
        }
        
        .feature-icon {
            font-size: 36px;
            margin-bottom: 15px;
            display: inline-block;
            animation: iconSpin 10s linear infinite;
        }
        
        @keyframes iconSpin {
            from { transform: rotate(0deg); }
            to { transform: rotate(360deg); }
        }
        
        .feature-text {
            color: #e0e0e0;
            font-size: 14px;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 1.5px;
            text-shadow: 1px 1px 2px rgba(0,0,0,0.3);
        }
        
        /* Info Box with Glass Effect */
        .info-box {
            background: rgba(81, 84, 110, 0.2);
            backdrop-filter: blur(10px);
            border-radius: 30px;
            padding: 35px;
            margin: 40px 0;
            border: 1px solid rgba(113,198,221,0.3);
            box-shadow: 
                0 10px 30px rgba(0,0,0,0.3),
                inset 0 0 30px rgba(113,198,221,0.1);
            animation: fadeIn 1s ease-out 0.6s both;
        }
        
        @keyframes fadeIn {
            from { opacity: 0; }
            to { opacity: 1; }
        }
        
        .info-title {
            color: #71c6dd;
            font-size: 24px;
            font-weight: 700;
            margin-bottom: 25px;
            display: flex;
            align-items: center;
            gap: 15px;
            text-shadow: 0 0 15px rgba(113,198,221,0.5);
            animation: slideInLeft 0.8s ease-out;
        }
        
        .info-list {
            list-style: none;
            padding: 0;
            margin: 0;
        }
        
        .info-list li {
            color: #e0e0e0;
            font-size: 16px;
            margin-bottom: 20px;
            padding-left: 35px;
            position: relative;
            animation: slideInRight 0.8s ease-out;
            animation-fill-mode: both;
            transition: all 0.3s ease;
        }
        
        .info-list li:hover {
            transform: translateX(10px);
            color: #71c6dd;
        }
        
        .info-list li::before {
            content: '✨';
            color: #71c6dd;
            position: absolute;
            left: 0;
            font-weight: bold;
            font-size: 20px;
            animation: starTwinkle 1.5s ease-in-out infinite;
        }
        
        @keyframes starTwinkle {
            0%, 100% { opacity: 1; transform: scale(1); }
            50% { opacity: 0.7; transform: scale(1.2); }
        }
        
        .info-list li:nth-child(1) { animation-delay: 0.1s; }
        .info-list li:nth-child(2) { animation-delay: 0.2s; }
        .info-list li:nth-child(3) { animation-delay: 0.3s; }
        .info-list li:nth-child(4) { animation-delay: 0.4s; }
        
        /* Quote Styling */
        .message-text:last-of-type {
            font-size: 20px;
            color: #71c6dd;
            font-style: italic;
            text-align: center;
            padding: 30px 0;
            border-top: 1px solid rgba(113,198,221,0.3);
            margin-top: 40px;
            animation: fadeIn 1s ease-out 0.8s both;
            text-shadow: 0 0 15px rgba(113,198,221,0.5);
        }
        
        /* Enhanced Footer */
        .email-footer {
            background: linear-gradient(135deg, #1a1a2a 0%, #2d2d39 100%);
            padding: 50px 40px;
            text-align: center;
            border-top: 3px solid #71c6dd;
            position: relative;
            overflow: hidden;
            animation: fadeIn 1s ease-out 1s both;
        }
        
        .email-footer::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: radial-gradient(circle at 50% 0%, rgba(113,198,221,0.2) 0%, transparent 70%);
            pointer-events: none;
        }
        
        .footer-links {
            display: flex;
            justify-content: center;
            gap: 25px;
            margin-bottom: 35px;
            flex-wrap: wrap;
            position: relative;
            z-index: 2;
        }
        
        .footer-link {
            color: #b0b0b0;
            text-decoration: none;
            font-size: 15px;
            font-weight: 500;
            padding: 8px 16px;
            border-radius: 50px;
            background: rgba(45,45,57,0.5);
            backdrop-filter: blur(5px);
            border: 1px solid rgba(113,198,221,0.2);
            transition: all 0.3s ease;
            letter-spacing: 0.5px;
        }
        
        .footer-link:hover {
            color: #71c6dd;
            background: rgba(113,198,221,0.1);
            border-color: #71c6dd;
            transform: translateY(-3px);
            box-shadow: 0 10px 20px rgba(113,198,221,0.2);
        }
        
        /* Social Links with 3D Effect */
        .social-links {
            display: flex;
            justify-content: center;
            gap: 20px;
            margin: 35px 0;
            position: relative;
            z-index: 2;
        }
        
        .social-link {
            width: 55px;
            height: 55px;
            background: linear-gradient(145deg, #2d2d39 0%, #1a1a2a 100%);
            border-radius: 50%;
            display: inline-flex;
            align-items: center;
            justify-content: center;
            transition: all 0.4s ease;
            border: 2px solid rgba(113,198,221,0.3);
            box-shadow: 0 5px 15px rgba(0,0,0,0.3);
            transform: rotateY(0deg);
            animation: socialFloat 3s ease-in-out infinite;
        }
        
        .social-link:nth-child(1) { animation-delay: 0s; }
        .social-link:nth-child(2) { animation-delay: 0.2s; }
        .social-link:nth-child(3) { animation-delay: 0.4s; }
        
        @keyframes socialFloat {
            0%, 100% { transform: translateY(0) rotateY(0deg); }
            50% { transform: translateY(-5px) rotateY(10deg); }
        }
        
        .social-link:hover {
            background: linear-gradient(145deg, #71c6dd 0%, #4fa3b8 100%);
            border-color: #ffffff;
            transform: translateY(-8px) scale(1.1);
            box-shadow: 0 15px 30px rgba(113,198,221,0.5);
        }
        
        .social-link svg {
            width: 28px;
            height: 28px;
            fill: #e0e0e0;
            transition: all 0.3s ease;
        }
        
        .social-link:hover svg {
            fill: #1a1a2a;
            transform: scale(1.1);
        }
        
        /* Enhanced Copyright */
        .copyright {
            color: #808080;
            font-size: 14px;
            margin-top: 35px;
            position: relative;
            z-index: 2;
            padding: 20px 0;
            border-top: 1px solid rgba(113,198,221,0.2);
            line-height: 1.8;
            letter-spacing: 0.5px;
        }
        
        .copyright br {
            display: none;
        }
        
        .copyright span {
            display: inline-block;
            margin: 0 5px;
            color: #71c6dd;
            font-weight: 600;
        }
        
        /* Mobile Responsive Enhancements */
        @media (max-width: 600px) {
            body {
                padding: 10px;
            }
            
            .email-container {
                margin: 10px;
                border-radius: 30px;
            }
            
            .email-header {
                padding: 30px 20px;
            }
            
            .logo-text {
                font-size: 36px;
            }
            
            .logo-icon {
                width: 55px;
                height: 55px;
            }
            
            .logo-icon svg {
                width: 30px;
                height: 30px;
            }
            
            .email-content {
                padding: 30px 20px;
            }
            
            .greeting {
                font-size: 24px;
                gap: 10px;
            }
            
            .greeting-emoji {
                font-size: 32px;
            }
            
            .message-text {
                font-size: 16px;
                line-height: 1.6;
            }
            
            .verification-code {
                font-size: 48px;
                letter-spacing: 8px;
            }
            
            .features-section {
                flex-direction: column;
                gap: 15px;
                padding: 20px 0;
            }
            
            .feature-item {
                padding: 15px;
                width: 100%;
            }
            
            .feature-icon {
                font-size: 32px;
            }
            
            .info-box {
                padding: 25px;
            }
            
            .info-title {
                font-size: 20px;
            }
            
            .info-list li {
                font-size: 14px;
                margin-bottom: 15px;
            }
            
            .footer-links {
                flex-direction: column;
                gap: 12px;
                align-items: center;
            }
            
            .footer-link {
                width: 80%;
                text-align: center;
                padding: 10px;
            }
            
            .social-links {
                gap: 15px;
            }
            
            .social-link {
                width: 45px;
                height: 45px;
            }
            
            .social-link svg {
                width: 22px;
                height: 22px;
            }
            
            .copyright {
                font-size: 12px;
                padding: 15px 0;
            }
            
            .copyright br {
                display: block;
                margin: 5px 0;
            }
        }
    """

def send_verification_email(user, verification_code, site_url=None):
    """Send email verification code with stunning design"""
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
                            <circle cx="12" cy="12" r="3" fill="#71c6dd"/>
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
                
                <div class="message-text" style="text-align: center; font-style: italic;">
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
                            <path d="M12 2.163c3.204 0 3.584.012 4.85.07 3.252.148 4.771 1.691 4.919 4.919.058 1.265.069 1.645.069 4.849 0 3.205-.012 3.584-.069 4.849-.149 3.225-1.664 4.771-4.919 4.919-1.266.058-1.644.07-4.85.07-3.204 0-3.584-.012-4.849-.07-3.26-.149-4.771-1.699-4.919-4.92-.058-1.265-.07-1.644-.07-4.849 0-3.204.013-3.583.07-4.849.149-3.227 1.664-4.771 4.919-4.919 1.266-.057 1.645-.069 4.849-.069zm0-2.163c-3.259 0-3.667.014-4.947.072-4.358.2-6.78 2.618-6.98 6.98-.059 1.281-.073 1.689-.073 4.948 0 3.259.014 3.668.072 4.948.2 4.358 2.618 6.78 6.98 6.98 1.281.058 1.689.072 4.948.072 3.259 0 3.668-.014 4.948-.072 4.354-.2 6.782-2.618 6.979-6.98.059-1.28.073-1.689.073-4.948 0-3.259-.014-3.667-.072-4.947-.196-4.354-2.617-6.78-6.979-6.98-1.281-.059-1.69-.073-4.949-.073zM5.838 12a6.162 6.162 0 1 1 12.324 0 6.162 6.162 0 0 1-12.324 0zM12 16a4 4 0 1 1 0-8 4 4 0 0 1 0 8z"/>
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
                            <circle cx="12" cy="12" r="3" fill="#71c6dd"/>
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
                <div style="text-align: center; margin: 45px 0;">
                    <a href="{reset_link}" style="
                        display: inline-block;
                        padding: 18px 45px;
                        background: linear-gradient(135deg, #71c6dd 0%, #4fa3b8 100%);
                        color: #1a1a2a;
                        text-decoration: none;
                        border-radius: 60px;
                        font-weight: 800;
                        font-size: 18px;
                        letter-spacing: 2px;
                        box-shadow: 0 15px 30px rgba(113,198,221,0.5);
                        border: 2px solid #ffffff;
                        transition: all 0.3s ease;
                        text-transform: uppercase;
                    ">
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
                <div style="
                    background: rgba(252, 75, 11, 0.1);
                    border-radius: 20px;
                    padding: 25px;
                    margin: 30px 0;
                    border-left: 5px solid #fc4b0b;
                    backdrop-filter: blur(5px);
                    animation: fadeIn 1s ease-out;
                ">
                    <div style="display: flex; align-items: center; gap: 15px;">
                        <span style="font-size: 28px;">⚠️</span>
                        <div>
                            <strong style="color: #fc4b0b; font-size: 16px;">Didn't request this?</strong>
                            <p style="color: #b0b0b0; font-size: 14px; margin-top: 5px; line-height: 1.6;">
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