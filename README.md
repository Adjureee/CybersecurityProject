# Secure Registration and Login System

This project implements the cybersecurity final project requirements:

- Registration module with username, password, and confirm password
- Login module with username and password
- Password strength meter with Weak, Medium, and Strong results
- Lowercase, uppercase, digit, symbol, and minimum 12-character validation
- Random per-user salt generation
- Pepper added during hashing but not stored in the database
- SHA-256 hashing of `password + salt + pepper`
- SQLite storage of username, password hash, and salt only

## Files

- `HashingSaltPepper.py` - main application source code
- `app.py` - Flask web version for online hosting
- `templates/index.html` - web registration and login page
- `templates/dashboard.html` - page shown after successful login
- `static/style.css` - web page styling
- `static/auth.js` - web page interactions
- `static/auth-hero.png` - web page hero image
- `users.db` - SQLite database
- `requirements.txt` - dependency list for the hosted Flask version
- `PYTHONANYWHERE_SETUP.md` - step-by-step hosting guide
- `DEMO_SCRIPT_15_MINUTES.md` - presentation and demonstration script

## How to Run

Run the application:

```bash
python HashingSaltPepper.py
```

Run the web version locally after installing Flask:

```bash
pip install -r requirements.txt
python app.py
```

## Password Rules

A Strong password must include:

- At least one lowercase letter
- At least one uppercase letter
- At least one number
- At least one special character
- At least 12 characters

Example Strong password: `Cyber@2026Secure`

## Database Fields

The `users` table stores:

- `username`
- `hashed_password`
- `salt`

The pepper is intentionally kept in the source code and is not stored in the database.

## Submission Reminder

The assignment also requires screenshots, short documentation, and a public hosted URL. Use the Flask web version for online hosting.
