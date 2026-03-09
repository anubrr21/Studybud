import resend
from django.conf import settings

def send_email_resend(subject, to_email, html_content, text_content=None):
    """
    Send email using Resend API directly (more reliable than SMTP)
    """
    params = {
        "from": settings.DEFAULT_FROM_EMAIL,
        "to": [to_email],
        "subject": subject,
        "html": html_content,
    }
    
    if text_content:
        params["text"] = text_content
    
    try:
        email = resend.Emails.send(params)
        return {'success': True, 'id': email['id']}
    except Exception as e:
        print(f"Resend email error: {e}")
        return {'success': False, 'error': str(e)}

def send_verification_email(user, verification_code):
    """Send email verification code"""
    subject = "Verify your StudyBud account"
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{
                font-family: 'Arial', sans-serif;
                background-color: #f4f4f4;
                margin: 0;
                padding: 0;
            }}
            .container {{
                max-width: 600px;
                margin: 20px auto;
                background: linear-gradient(135deg, #2d2d39 0%, #3f4156 100%);
                border-radius: 15px;
                padding: 30px;
                box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            }}
            .header {{
                text-align: center;
                margin-bottom: 30px;
            }}
            .logo {{
                font-size: 32px;
                font-weight: bold;
                color: #71c6dd;
            }}
            .code {{
                background: #71c6dd;
                color: #2d2d39;
                font-size: 48px;
                font-weight: bold;
                padding: 20px;
                text-align: center;
                border-radius: 10px;
                letter-spacing: 5px;
                margin: 30px 0;
            }}
            .footer {{
                text-align: center;
                color: #b2bdbd;
                font-size: 14px;
                margin-top: 30px;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <div class="logo">StudyBuddy</div>
                <p style="color: #e5e5e5;">Welcome to the community!</p>
            </div>
            <p style="color: #e5e5e5;">Hello @{user.username},</p>
            <p style="color: #e5e5e5;">Your verification code is:</p>
            <div class="code">{verification_code}</div>
            <p style="color: #e5e5e5;">Enter this code in the app to verify your email address.</p>
            <p style="color: #e5e5e5;">This code will expire in 24 hours.</p>
            <div class="footer">
                <p>If you didn't request this, please ignore this email.</p>
                <p>&copy; 2024 StudyBuddy. All rights reserved.</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    return send_email_resend(
        subject=subject,
        to_email=user.email,
        html_content=html_content,
        text_content=f"Your verification code is: {verification_code}"
    )

def send_password_reset_email(user, reset_link):
    """Send password reset email"""
    subject = "Reset your StudyBud password"
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{
                font-family: 'Arial', sans-serif;
                background-color: #f4f4f4;
                margin: 0;
                padding: 0;
            }}
            .container {{
                max-width: 600px;
                margin: 20px auto;
                background: linear-gradient(135deg, #2d2d39 0%, #3f4156 100%);
                border-radius: 15px;
                padding: 30px;
                box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            }}
            .header {{
                text-align: center;
                margin-bottom: 30px;
            }}
            .logo {{
                font-size: 32px;
                font-weight: bold;
                color: #71c6dd;
            }}
            .button {{
                display: inline-block;
                padding: 15px 30px;
                background: #71c6dd;
                color: #2d2d39;
                text-decoration: none;
                border-radius: 30px;
                font-weight: bold;
                margin: 30px 0;
            }}
            .footer {{
                text-align: center;
                color: #b2bdbd;
                font-size: 14px;
                margin-top: 30px;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <div class="logo">StudyBuddy</div>
                <p style="color: #e5e5e5;">Password Reset Request</p>
            </div>
            <p style="color: #e5e5e5;">Hello @{user.username},</p>
            <p style="color: #e5e5e5;">We received a request to reset your password. Click the button below to create a new password:</p>
            <div style="text-align: center;">
                <a href="{reset_link}" class="button">Reset Password</a>
            </div>
            <p style="color: #e5e5e5;">If you didn't request this, please ignore this email.</p>
            <p style="color: #e5e5e5;">This link will expire in 24 hours.</p>
            <div class="footer">
                <p>&copy; 2024 StudyBuddy. All rights reserved.</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    return send_email_resend(
        subject=subject,
        to_email=user.email,
        html_content=html_content,
        text_content=f"Reset your password here: {reset_link}"
    )