"""
Run this once to create your login.

Usage:
    python create_user.py
"""
import getpass

from app.core.database import SessionLocal
from app.crud.user import create_user, get_user_by_username

db = SessionLocal()

username = input("Choose a username: ").strip()

if get_user_by_username(db, username):
    print(f"User '{username}' already exists.")
else:
    password = getpass.getpass("Choose a password: ")
    confirm = getpass.getpass("Confirm password: ")
    if password != confirm:
        print("Passwords didn't match. Run the script again.")
    else:
        create_user(db, username, password)
        print(f"User '{username}' created successfully.")

db.close()