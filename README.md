# SocialConnect

SocialConnect is a full-featured social media web application built with Django and Django REST Framework. It allows users to create profiles, share posts, connect with friends, and interact through likes and comments.

## Features

- User authentication and profile management
- Post creation with text and image support
- Like and unlike posts
- Connection system (follow/unfollow)
- Feed of posts from connected users
- User recommendations
- RESTful API for all features

## Setup Instructions

### Prerequisites

- Python 3.9+
- pip (Python package manager)
- Git

### Installation

1. Clone the repository:
   ```
   git clone https://github.com/Titanpimpale/Social-Media-App.git
   cd Social-Media-App
   ```

2. Create and activate a virtual environment:
   ```
   python -m venv env
   
   # On Windows
   env\Scripts\activate
   
   # On macOS/Linux
   source env/bin/activate
   ```

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Set up the database:
   ```
   cd socialmedia
   python manage.py migrate
   ```

5. Create a superuser (admin):
   ```
   python manage.py createsuperuser
   ```

6. Run the development server:
   ```
   python manage.py runserver
   ```

7. Access the application at http://127.0.0.1:8000/

## API Endpoints

SocialConnect provides a comprehensive RESTful API. All API endpoints are available at `/api/`.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
