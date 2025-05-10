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

## Screenshot

![Image](https://github.com/user-attachments/assets/6f8d5777-e08b-42df-a86f-08a18b95248d)
![Image](https://github.com/user-attachments/assets/49c414a4-4d0e-4c70-82cd-4bc1c9562774)
![Image](https://github.com/user-attachments/assets/1e1b7f16-8718-4157-8c68-9a98b3631b84)
![Image](https://github.com/user-attachments/assets/43a0fd74-b2ac-45d4-89a8-065bec55a197)
![Image](https://github.com/user-attachments/assets/4b2e018b-0eb2-4f2e-8f03-b8b272f576cc)

## API Endpoints

SocialConnect provides a comprehensive RESTful API. All API endpoints are available at `/api/`.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
