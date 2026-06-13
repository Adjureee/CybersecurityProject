# Secure Registration and Login System

## Cover Page

Project Title: Secure Registration and Login System

Subject: Cybersecurity Final Project

Group Members:

- [Name 1]
- [Name 2]
- [Name 3]

Hosted Website Link:

[Paste PythonAnywhere link here]

## 1. Hashing Algorithm Used

This project uses the SHA-256 hashing algorithm through Python's `hashlib.sha256()` function. During registration, the system does not store the plain text password. Instead, it combines the password with a unique salt and a private pepper, then hashes the combined value.

The hashing process is:

`password + salt + pepper -> SHA-256 -> password hash`

The generated password hash is stored in the SQLite database. During login, the system recomputes the hash using the input password, stored salt, and same pepper. If the recomputed hash matches the stored hash, the login is successful.

## 2. How Salt Works

A salt is a unique random value generated for every registered user. In this project, the salt is created using `os.urandom(16)` and converted into hexadecimal format before being saved in the database.

Salt improves password security because even if two users choose the same password, their stored password hashes will still be different. This helps defend against precomputed hash attacks such as rainbow table attacks.

The database stores the salt because it is needed during login to recompute the password hash.

## 3. How Pepper Works

A pepper is a secret value added to the password before hashing. Unlike the salt, the pepper is not stored in the database. In this project, the pepper is defined in the source code and combined with the password and salt before SHA-256 hashing.

The process is:

`input_password + stored_salt + pepper`

The pepper adds another layer of protection. If someone accesses only the database, they will see usernames, password hashes, and salts, but they will not see the pepper.

## 4. How the Password Meter Validates Password Strength

The password meter checks five rules:

1. At least one lowercase letter
2. At least one uppercase letter
3. At least one number
4. At least one special character
5. At least 12 characters

The system displays password strength as Weak, Medium, or Strong. A password is accepted for registration only when it satisfies all required rules and becomes Strong.

Example strong password:

`Cyber@2026Secure`

## 5. Why Strong Passwords Are Important in Cybersecurity

Strong passwords are important because weak passwords can be guessed, brute-forced, or cracked more easily. A strong password has enough length and complexity to make attacks harder.

In authentication systems, password security is very important because passwords protect user accounts and sensitive information. By requiring strong passwords and storing only hashed passwords with salt and pepper, this project follows better cybersecurity practices.

## 6. Screenshots of the System

Insert screenshots here:

- Registration form
- Password meter
- Successful registration
- Successful login dashboard
- Failed login attempt
- Database table showing username, hashed password, and salt
- Hosted online system

## 7. Public URL or Hosted Link

Hosted website link:

[Paste PythonAnywhere link here]

## Conclusion

This project demonstrates a secure registration and login system. It includes password strength validation, hashing, salt, pepper, and secure login verification. The system does not store plain text passwords, and the pepper does not appear in the database.
