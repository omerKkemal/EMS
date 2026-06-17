# EMS — Employee Management System

A lightweight Flask-based Employee Management System (EMS) for managing employees, profiles, and reports.

## Features
- User authentication (login)
- Employee listing and detail view
- Profile picture upload and static assets
- Simple reporting page

## Requirements
- Python 3.8+
- See `requirements.txt` for exact packages

## Quick Setup
1. Create and activate a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Initialize or migrate the database (if applicable):

```bash
python manage_db.py init
# or follow the scripts in manage_db.py / db.py for creating tables
```

4. Run the app:

```bash
python app.py
```

Open `http://127.0.0.1:5000` in your browser.

## Project Structure
- `app.py` — Flask app entrypoint
- `models.py`, `db.py`, `manage_db.py` — database models and helpers
- `templates/` — HTML templates
- `static/` — static assets (JS, fonts, profile_pics)

## Notes
- Profile pictures are stored in `static/profile_pics/`.
- Adjust configuration and secret keys in `app.py` or environment variables before production.

## License
This project has no license specified. Add a `LICENSE` file if needed.

---
Generated README for the EMS workspace.
