# PythonAnywhere Setup Guide

Use this guide to host the Flask web version of the project.

## 1. Files to Upload

Upload these project files and folders to a folder named `mysite` on PythonAnywhere:

- `app.py`
- `requirements.txt`
- `users.db` if you want to upload your existing local test users
- `templates/index.html`
- `templates/dashboard.html`
- `static/auth-hero.png`
- `static/auth.js`
- `static/style.css`

Do not upload:

- `__pycache__`
- `users.db-shm`
- `users.db-wal`

## 2. Create the Folder

1. Log in to PythonAnywhere.
2. Open the `Files` tab.
3. Create this folder:

```text
/home/YOURUSERNAME/mysite
```

Replace `YOURUSERNAME` with your PythonAnywhere username.

## 3. Upload the Files

Inside `/home/YOURUSERNAME/mysite`, upload:

```text
app.py
requirements.txt
users.db
```

Create these folders:

```text
templates
static
```

Upload `index.html` and `dashboard.html` inside `templates`.

Upload `auth-hero.png`, `auth.js`, and `style.css` inside `static`.

## 4. Install Flask

Open the `Consoles` tab and start a `Bash` console.

Run:

```bash
cd ~/mysite
mkvirtualenv --python=/usr/bin/python3.13 cyberenv
pip install -r requirements.txt
```

If Python 3.13 is not available on your account, choose the newest Python 3 version shown in the PythonAnywhere Web tab and use that same version for both the virtualenv and the web app.

## 5. Create the Web App

1. Open the `Web` tab.
2. Click `Add a new web app`.
3. Choose `Manual configuration`.
4. Choose the same Python version used for the virtualenv.
5. In the `Virtualenv` section, enter:

```text
/home/YOURUSERNAME/.virtualenvs/cyberenv
```

Click the check mark or confirm button beside the virtualenv field.

## 6. Configure the WSGI File

In the `Web` tab, click the WSGI configuration file link.

Delete the sample Flask code and paste:

```python
import sys

path = '/home/YOURUSERNAME/mysite'
if path not in sys.path:
    sys.path.insert(0, path)

from app import app as application
```

Replace `YOURUSERNAME` with your PythonAnywhere username.

Save the file.

## 7. Configure Static Files

In the `Web` tab, find `Static files`.

Add this mapping:

```text
URL: /static/
Directory: /home/YOURUSERNAME/mysite/static
```

Click `Reload` after saving the static file mapping.

## 8. Test the Website

Open:

```text
https://YOURUSERNAME.pythonanywhere.com
```

Test these actions:

- Register with a strong password such as `Cyber@2026Secure`
- Log in with the same account
- Try a failed login attempt
- Open the Register tab and confirm the password meter updates

## 9. If Something Looks Old

Open the site and press:

```text
Ctrl + F5
```

You can also test whether static files load by opening:

```text
https://YOURUSERNAME.pythonanywhere.com/static/style.css?v=4
https://YOURUSERNAME.pythonanywhere.com/static/auth.js?v=4
```

## 10. If the Website Shows an Error

Check these common issues:

- The WSGI file still has `YOURUSERNAME` instead of your real username.
- The virtualenv path is wrong.
- Flask was not installed in the virtualenv.
- The `templates` folder is missing `index.html`.
- The `static` folder is missing `style.css`, `auth.js`, or `auth-hero.png`.
- The Web tab was not reloaded after changes.

## Official References

- PythonAnywhere Flask setup: https://help.pythonanywhere.com/pages/Flask
- PythonAnywhere file upload: https://help.pythonanywhere.com/pages/UploadingAndDownloadingFiles/
- PythonAnywhere static files: https://help.pythonanywhere.com/pages/StaticFiles/
- PythonAnywhere virtualenvs: https://help.pythonanywhere.com/pages/VirtualEnvForWebsites/
