# 15-Minute Explanation and Demonstration Script

Project: Secure Registration and Login System

Use this as your speaking guide during the final project demonstration. Replace bracketed text such as `[Your Name]` and `[Hosted Link]` before presenting.

## 0:00-0:45 - Opening

Good day everyone. I am `[Your Name]`, and today I will present our cybersecurity final project titled **Secure Registration and Login System**.

The goal of this project is to demonstrate a secure user authentication system with three main parts: a registration module, a login module, and a password strength meter. The project also applies important cybersecurity techniques such as password hashing, salt, pepper, and password strength validation.

For this demonstration, I will show the system interface, explain how the security features work, and demonstrate both successful and failed login attempts.

## 0:45-2:00 - Project Overview

This project was created to avoid one of the most dangerous mistakes in authentication systems, which is storing passwords in plain text.

Instead of saving the actual password, the system saves only:

- the username
- the password hash
- the unique salt

The pepper is not stored in the database. It stays only in the source code as a secret value added during hashing.

The web version of this project uses Flask for the online interface and SQLite for the database. The interface includes a modern login and registration page, floating labels, password visibility toggles, real-time validation, and a password strength meter.

## 2:00-3:30 - Interface Walkthrough

Demo action: Open the website or local app.

If local:

```text
http://127.0.0.1:5000
```

If hosted:

```text
[Hosted Link]
```

This is the main authentication page. On the left side, there is a cybersecurity-themed visual area, and on the right side, there is the authentication form.

The page has two views: **Login** and **Register**. When I switch between them, the page uses a smooth transition animation instead of reloading the whole page. This improves the user experience because the interaction feels faster and more modern.

The design uses a dark mode layout, glass-style card, blue accent color, and clear focus states for accessibility.

## 3:30-5:00 - Registration Form

Demo action: Click **Register**.

Now I will demonstrate the registration module.

The registration form includes:

- username
- password
- confirm password

These fields match the project requirements. The password and confirm password must match before the system allows registration.

The password field also includes a password visibility toggle. This allows the user to check what they typed, which reduces typing mistakes while still keeping the password hidden by default.

## 5:00-7:00 - Password Strength Meter

Demo action: Type weak passwords first.

First, I will type a weak password, for example:

```text
password123
```

The system detects that this password is weak because it does not satisfy all required password rules.

The password strength meter checks for:

- at least one lowercase letter
- at least one uppercase letter
- at least one number
- at least one symbol
- at least 12 characters

Now I will type the example strong password:

```text
Cyber@2026Secure
```

The meter now shows **Strong**, because the password includes uppercase letters, lowercase letters, numbers, a symbol, and it has at least 12 characters.

This feature is important because weak passwords are easier to guess, brute force, or crack. A strong password increases account protection.

## 7:00-8:30 - Successful Registration

Demo action: Register a new sample account.

For this demonstration, I will register a sample user.

Example:

```text
Username: demo_user
Password: Cyber@2026Secure
Confirm Password: Cyber@2026Secure
```

When I submit the form, the system first validates the password strength and checks that the password and confirm password match.

After validation, the system generates a unique random salt for this user. Then it combines:

```text
password + salt + pepper
```

After combining those values, the system applies SHA-256 hashing. The final password hash and the salt are stored in the database, but the original password is not stored.

Demo action: Show successful registration message.

The system displays **Registration Successful**, which means the account was created securely.

## 8:30-10:00 - Database Demonstration

Demo action: Show the database table using DB Browser for SQLite, SQLite command line, or a screenshot.

Now I will show the database table.

The database table contains three fields:

- username
- hashed_password
- salt

Notice that there is no plain text password column. The password shown here is a long hash value, not the actual password typed by the user.

Also, the pepper is not shown in the database. This is intentional. The pepper must stay secret and must not be stored together with the user records.

This protects users because even if someone sees the database, they cannot directly read the real passwords.

## 10:00-11:30 - Login Process

Demo action: Return to the Login tab.

Now I will demonstrate the login module.

The login form accepts:

- username
- password

When the user logs in, the system retrieves the stored salt from the database. Then it recomputes the hash using:

```text
input_password + stored_salt + pepper
```

If the newly generated hash matches the stored hash, the login is successful. If it does not match, the system rejects the login.

Demo action: Log in using the correct username and password.

Now I will enter the correct credentials for the account I registered.

The system displays **Login Successful**, which means the entered password generated the same hash as the one stored in the database.

## 11:30-12:45 - Failed Login Attempt

Demo action: Try the same username with a wrong password.

Next, I will demonstrate a failed login attempt.

I will use the same username, but I will enter a wrong password.

The system now displays **Invalid Username or Password**.

This message is intentionally general. It does not say whether the username or password is wrong. This is a good security practice because it avoids giving attackers extra information.

## 12:45-13:45 - Code and Security Explanation

Demo action: Briefly show `app.py`.

The main web application code is in `app.py`.

Important functions include:

- `evaluate_password_strength`, which checks the password rules
- `hash_password`, which combines password, salt, and pepper before hashing
- `register_user`, which validates and securely stores new users
- `login_user`, which recomputes and compares the hash during login

The system also uses parameterized SQL queries. This helps protect database operations from SQL injection attacks.

For hash comparison, the project uses `hmac.compare_digest`, which is safer than a normal string comparison because it helps reduce timing-based information leaks.

## 13:45-14:30 - Online Hosting Explanation

This project is prepared for online hosting using PythonAnywhere.

PythonAnywhere is a good free hosting choice for this project because it supports Python Flask applications and can use SQLite for a small school project.

The hosted version uses these files:

- `app.py`
- `templates/index.html`
- `static/style.css`
- `static/auth.js`
- `static/auth-hero.png`
- `requirements.txt`

After deployment, the public URL will be:

```text
[Hosted Link]
```

## 14:30-15:00 - Closing

To summarize, this project demonstrates a secure authentication system with registration, login, and password strength validation.

It does not store plain text passwords. Instead, it uses hashing, unique salt, and pepper to protect user credentials.

The system also includes a modern and user-friendly interface, real-time password feedback, and proper login error handling.

That concludes my demonstration. Thank you.

## Quick Demo Checklist

Before presenting, prepare these:

- Start the local server or open the hosted link.
- Prepare one weak password example: `password123`
- Prepare one strong password example: `Cyber@2026Secure`
- Prepare one sample username: `demo_user`
- Show registration form.
- Show password meter changing from Weak to Strong.
- Show successful registration.
- Show database fields: username, hashed_password, salt.
- Show successful login.
- Show failed login.
- Show the public hosted URL if already deployed.

## Backup Lines If Something Goes Wrong

If the website is slow:

The page may take a few seconds to load because it is running on a free hosting service, but the authentication logic remains the same.

If the username already exists:

The system prevents duplicate usernames, so I will use a new sample username for this demonstration.

If the local server is used instead of hosted link:

For this demonstration, I am using the local version. The same Flask project is prepared for deployment on PythonAnywhere for the public URL requirement.
