🚀 Live Demo
Experience StudyBuddy live: https://studybud-kxsv.onrender.com

📋 Table of Contents
Overview

✨ Features

🛠️ Tech Stack

📸 Screenshots

🚀 Getting Started

📁 Project Structure

💬 Core Features

📱 Mobile Responsiveness

🔧 Configuration

🚢 Deployment

🤝 Contributing

📄 License

📞 Contact

📖 Overview
StudyBuddy is a modern, real-time communication platform designed specifically for students and learners. It combines the functionality of study groups with instant messaging, creating a seamless environment for collaborative learning. Whether you're looking for a study partner, want to discuss complex topics, or need a dedicated space for group projects, StudyBuddy has you covered.

✨ Features
🏠 Core Platform
🔐 Secure Authentication - Email-based signup/login with email verification

👤 User Profiles - Customizable profiles with avatars and bios

🔍 Advanced Search - Search rooms by topic, name, or description

📊 Activity Feed - Real-time feed of all platform activities

💬 Room Features (Group Chats)
📝 Create Study Rooms - Create topic-specific rooms for group discussions

📌 Pin Messages - Pin important messages (max 3 per room)

↩️ Reply to Messages - Threaded conversations with reply indicators

✏️ Edit/Delete Messages - Full message management

❤️ Like Rooms - Show appreciation for useful rooms

👥 Participant Tracking - See who's in each room

🔔 Room Notifications - Get notified of comments and likes

💌 Personal Messaging
💬 One-on-One Chats - Private messaging between users

🔌 Real-time Communication - Instant message delivery via WebSockets

🖼️ File Sharing - Share images and documents (up to 10MB)

👍 Message Reactions - React to messages with emojis

📌 Pin Messages - Pin important conversations

↩️ Reply to Messages - Contextual replies

🗑️ Delete Options - "Delete for me" or "Delete for everyone"

✍️ Typing Indicators - See when someone is typing

🟢 Online Status - Real-time online/offline status

🎨 Custom Themes - 30+ beautiful chat themes

📱 Mobile Actions - Long press on mobile for message actions

🔔 Notifications System
📨 Real-time Notifications - Instant alerts for follows, likes, and comments

🔍 Advanced Filters - Filter by type, date, or search content

📅 Date Filter - View notifications from specific dates

✅ Read/Unread Status - Track which notifications you've seen

🔗 Clickable Links - Direct navigation to relevant content

👥 Social Features
🔄 Follow System - Follow other users

🤝 Mutual Followers - See friends in common

📊 Follower/Following Counts - Track your network

💡 Suggested Users - Discover new study partners

🎨 UI/UX
🌙 Dark Theme - Easy on the eyes for late-night study sessions

📱 Fully Responsive - Perfect on desktop, tablet, and mobile

🍞 Toast Notifications - Elegant pop-up messages

⚡ Smooth Animations - Fluid transitions and hover effects

🔍 Live Search - Instant filtering across all pages

📅 Calendar Filters - Date-based content filtering

🛠️ Tech Stack
Backend
Django (v5.0) - High-level Python web framework

Django Channels - WebSocket support for real-time features

Redis - Channel layer for WebSocket communication

PostgreSQL - Production database

SQLite - Development database

Frontend
HTML5/CSS3 - Semantic markup and modern styling

JavaScript - Dynamic interactions and real-time updates

CSS Variables - Theming and consistent design language

WebSockets - Real-time bidirectional communication

Authentication & Email
Django Auth - Built-in authentication system

Email Verification - 6-digit code verification

Password Reset - Secure password recovery

Resend - Modern email delivery service

Deployment
Render - Cloud platform for hosting

Gunicorn/Daphne - ASGI server for WebSocket support

WhiteNoise - Static file serving

Additional Libraries
Pillow - Image processing

python-decouple - Environment variable management

django-cors-headers - CORS handling

djangorestframework - API endpoints

channels-redis - Redis channel layer

📸 Screenshots
Home Page	Chat Interface	Profile Page
https://screenshots/home.png	https://screenshots/chat.png	https://screenshots/profile.png
Notifications	Room View	Mobile View
https://screenshots/notifications.png	https://screenshots/room.png	https://screenshots/mobile.png
🚀 Getting Started
Prerequisites
Python 3.11+

Redis (for WebSocket support)

Git

Installation
Clone the repository

bash
git clone https://github.com/anubrr21/Studybud.git
cd Studybud
Create and activate virtual environment

bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
Install dependencies

bash
pip install -r requirements.txt
Set up environment variables
Create a .env file in the root directory:

env
SECRET_KEY=your-secret-key
DEBUG=True
DATABASE_URL=sqlite:///db.sqlite3
REDIS_URL=redis://localhost:6379

# Email (Resend)
RESEND_API_KEY=your-resend-api-key

# Cloudinary (Optional)
CLOUDINARY_CLOUD_NAME=your-cloud-name
CLOUDINARY_API_KEY=your-api-key
CLOUDINARY_API_SECRET=your-api-secret
Run migrations

bash
python manage.py makemigrations
python manage.py migrate
Create superuser (optional)

bash
python manage.py createsuperuser
Run development server

bash
python manage.py runserver
Access the application

Main site: http://localhost:8000

Admin panel: http://localhost:8000/admin

📁 Project Structure
text
Studybud/
├── base/                      # Main application
│   ├── management/             # Custom management commands
│   ├── migrations/             # Database migrations
│   ├── templates/base/         # HTML templates
│   │   ├── home.html
│   │   ├── room.html
│   │   ├── profile.html
│   │   ├── chats.html
│   │   ├── chat_detail.html
│   │   ├── notifications.html
│   │   └── ...
│   ├── static/                 # CSS, JS, images
│   ├── consumers.py            # WebSocket consumers
│   ├── models.py               # Database models
│   ├── views.py                # View functions
│   ├── urls.py                 # URL routing
│   ├── forms.py                # Form classes
│   └── tokens.py               # Token generation
├── studybud/                   # Project configuration
│   ├── settings.py             # Django settings
│   ├── urls.py                 # Main URL config
│   ├── asgi.py                 # ASGI config
│   └── wsgi.py                 # WSGI config
├── templates/                  # Global templates
│   ├── main.html               # Base template
│   └── navbar.html             # Navigation bar
├── static/                     # Static files
├── media/                       # User uploads
├── requirements.txt            # Python dependencies
├── manage.py                   # Django management script
├── README.md                   # This file
└── .env                        # Environment variables
💬 Core Features
Room System
python
# Example: Creating a room
room = Room.objects.create(
    host=request.user,
    topic=topic,
    name="Advanced Django",
    description="Let's master Django together!"
)
Real-time Chat
javascript
// WebSocket connection
const socket = new WebSocket(
    'ws://' + window.location.host + '/ws/chat/' + chatId + '/'
);

// Send message
socket.send(JSON.stringify({
    'type': 'message',
    'content': message
}));
Email Verification
python
# Generate 6-digit code
verification_code = generate_verification_code()
user.email_verification_token = verification_code
user.save()

# Send via Resend
send_verification_email(user, verification_code)
📱 Mobile Responsiveness
StudyBuddy is fully responsive and works seamlessly across all devices:

Desktop: 3-column layout with sidebar

Tablet: 2-column layout with collapsible sidebar

Mobile: Single column with bottom navigation

Touch Support: Swipe gestures, long press for actions

Optimized: Fast loading on all devices

🔧 Configuration
Email Settings (Resend)
python
# settings.py
RESEND_API_KEY = os.environ.get('RESEND_API_KEY')
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.resend.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'resend'
EMAIL_HOST_PASSWORD = RESEND_API_KEY
WebSocket Configuration
python
# settings.py
CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [os.environ.get("REDIS_URL")],
        },
    },
}
🚢 Deployment
Deploy on Render
Push code to GitHub

bash
git add .
git commit -m "Ready for deployment"
git push
Create a new Web Service on Render

Connect your GitHub repository

Select "Python" environment

Set build command: pip install -r requirements.txt

Set start command: daphne studybud.asgi:application -b 0.0.0.0 -p $PORT

Add environment variables in Render dashboard:

SECRET_KEY

DATABASE_URL

REDIS_URL

RESEND_API_KEY

Deploy! 🚀

🤝 Contributing
Contributions are welcome! Here's how you can help:

Fork the repository

Create a feature branch

bash
git checkout -b feature/amazing-feature
Commit your changes

bash
git commit -m 'Add amazing feature'
Push to the branch

bash
git push origin feature/amazing-feature
Open a Pull Request

Development Guidelines
Follow PEP 8 style guide

Write meaningful commit messages

Add tests for new features

Update documentation as needed

📄 License
This project is licensed under the MIT License - see the LICENSE file for details.

📞 Contact
Anubrata Bhattacharyya

GitHub: @anubrr21

Project Link: https://github.com/anubrr21/Studybud

Live Demo: https://studybud-kxsv.onrender.com

🙏 Acknowledgments
Django Documentation

Django Channels Documentation

Render Deployment Guides

All contributors and testers

Made with ❤️ for the study community

⭐ If you found this project helpful, please give it a star on GitHub!
