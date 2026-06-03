import json
import os

AUTH_FILE = "user_data/users_auth.json"

def init_auth():
    if not os.path.exists("user_data"):
        os.makedirs("user_data")
    if not os.path.exists(AUTH_FILE):
        with open(AUTH_FILE, "w") as f:
            json.dump({}, f)

def signup_user(name, email, phone, username, password, salary, currency):
    init_auth()
    with open(AUTH_FILE, "r") as f:
        users = json.load(f)
    
    if username in users:
        return False, "Username already exists."
    
    users[username] = {
        "name": name,
        "email": email,
        "phone": phone,
        "password": password,
        "salary": float(salary),
        "currency": currency
    }
    
    with open(AUTH_FILE, "w") as f:
        json.dump(users, f, indent=4)
    return True, "Account created successfully!"

def login_user(username, password):
    init_auth()
    with open(AUTH_FILE, "r") as f:
        users = json.load(f)
    
    if username in users and users[username]["password"] == password:
        return True, users[username]
    return False, None
