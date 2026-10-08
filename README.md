# Secure Login System

A secure Flask-based login web application developed for the Thiranex internship Task 4.

## Features

- User registration
- Password hashing with bcrypt
- Secure login/logout
- Session management
- Input validation
- Parameterized SQL queries to reduce SQL injection risk
- SQLite database
- Optional two-factor authentication (TOTP)
- Simple responsive interface

## Technologies

- Python
- Flask
- SQLite
- bcrypt
- PyOTP
- HTML/CSS

## Project Structure

```text
secure_login_system/
├── app.py
├── requirements.txt
├── README.md
├── .gitignore
├── templates/
│   ├── base.html
│   ├── login.html
│   ├── register.html
│   ├── dashboard.html
│   └── setup_2fa.html
└── static/
    └── style.css
```

## How to Run

### 1. Create a virtual environment

Windows:

```bash
python -m venv venv
venv\Scripts\activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Start the application

```bash
python app.py
```

### 4. Open in a browser

```text
http://127.0.0.1:5000
```

## Security Measures

1. Passwords are never stored as plain text. bcrypt creates a salted password hash.
2. SQL queries use placeholders instead of string concatenation.
3. Login state is maintained with Flask sessions.
4. User input is validated before registration.
5. Logout clears the session.
6. Optional TOTP-based 2FA is included.

## Expected Outcome

The application provides a secure login system with hashed passwords, input validation, session management, and optional 2FA, reducing common risks such as password exposure, SQL injection, and unauthorized access.

## Internship Submission

For the Thiranex submission, upload this project to GitHub and submit the repository URL through the internship portal.
