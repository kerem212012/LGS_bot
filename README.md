# LGS Bot

A Django-based Learning Management System (LMS) with bot integration for quiz management and automated responses.

## Overview

LGS Bot is a comprehensive platform designed to manage quizzes and learning materials. It integrates with a bot service to provide automated responses and quiz management capabilities.

## Project Structure

```
LGS_bot/
├── lgs/                      # Main Django app
│   ├── models.py            # Database models
│   ├── views.py             # View handlers
│   ├── admin.py             # Django admin configuration
│   ├── migrations/          # Database migrations
│   └── tests.py             # Application tests
├── lgs_bot/                 # Django project settings
│   ├── settings.py          # Project settings
│   ├── urls.py              # URL routing
│   ├── asgi.py              # ASGI configuration
│   └── wsgi.py              # WSGI configuration
├── bot/                     # Bot service
│   └── bot.py               # Bot implementation
├── media/                   # User-uploaded files
├── docker-compose.yml       # Docker compose configuration
├── Dockerfile               # Main application Dockerfile
├── manage.py                # Django management script
├── requirements.txt         # Python dependencies
└── db.sqlite3              # SQLite database
```

## Requirements

- Python 3.x
- Django
- SQLite3
- Docker (optional, for containerized deployment)

## Installation

### Local Setup

1. **Clone the repository**
   ```bash
   cd LGS_bot
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run migrations**
   ```bash
   python manage.py migrate
   ```

5. **Start the development server**
   ```bash
   python manage.py runserver
   ```

### Docker Setup

Build and run using Docker Compose:

```bash
docker-compose up --build
```

## Features

- **Quiz Management**: Create, edit, and manage quizzes
- **Subject Organization**: Organize quizzes by subject
- **Bot Integration**: Automated bot responses and interactions
- **Media Support**: Upload and manage quiz images
- **Admin Panel**: Django admin interface for content management

## Usage

1. Access the Django admin panel at `http://localhost:8000/admin/`
2. Create subjects and quizzes through the admin interface
3. Upload quiz images as needed
4. The bot service will handle automated interactions based on configured rules

## Database Schema

The application uses SQLite with the following main models:
- **Subject**: Quiz subject categories
- **Quiz**: Quiz questions and content
- **Quiz Images**: Associated media for quizzes

## Configuration

Edit `lgs_bot/settings.py` to configure:
- Database settings
- Installed apps
- Static files paths
- Bot settings

## Troubleshooting

- **Database migration errors**: Run `python manage.py makemigrations` then `python manage.py migrate`
- **Missing dependencies**: Run `pip install -r requirements.txt` again
- **Port already in use**: Change the port with `python manage.py runserver 8001`

## Contributing

Follow Django best practices and ensure all tests pass before submitting changes.

## Support

For issues or questions, please open an issue in the repository.
