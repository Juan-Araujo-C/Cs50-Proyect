import os
import sqlite3
from flask import Flask, flash, redirect, render_template, request, session, jsonify
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
import re

from nasa_api import get_api_data_for_hist, format_date, get_api_data_for_map
from helpers import apology, login_required

app = Flask(__name__)

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure SQLite database
DB_FILE = "clients.db"

# Register the filter in the application
app.jinja_env.filters['format_date'] = format_date

@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

@app.route("/history")
@login_required
def history():
    start_index = int(request.args.get('start_index', 1))
    data = get_api_data_for_hist(start_index)
    events = data.get('events', [])
    total_count = data.get('total_count', 0)
    indexed_events = list(enumerate(events, start=start_index))

    return render_template('history.html', events=indexed_events, total_count=total_count)

@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""
    if request.method == "POST":
        # Ensure username (email) was submitted
        if not request.form.get("username"):
            return apology("Email is required")

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("Password is required")

        # Validate email format
        email = request.form.get("username")
        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            return apology("Invalid email format", 400)

        # Query database for username (email)
        with sqlite3.connect(DB_FILE) as conn:
            cursor = conn.cursor()
            user = cursor.execute(
                "SELECT * FROM users WHERE username = ?", (email,)
            ).fetchone()

        # Check if email exists and password is correct
        if user and check_password_hash(user[2], request.form.get("password")):
            # Remember which user has logged in
            session["user_id"] = user[0]

            # Redirect user to home page
            return redirect("/")
        else:
            flash("Invalid email and/or password", "error")
            return render_template("login.html")

    else:
        return render_template("login.html")

@app.route("/logout")
def logout():
    """Log user out"""
    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")

@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    if request.method == "POST":
        # Ensure username (email) was submitted
        if not request.form.get("username"):
            return apology("Email is required")

        # Ensure password was submitted
        elif not request.form.get("password") or not request.form.get("confirmation"):
            return apology("Password is required")

        # Ensure password match
        elif request.form.get("password") != request.form.get("confirmation"):
            return apology("Passwords do not match")

        # Hash the password
        password = request.form.get("password")

        # Check password requirements
        if not re.search(r"[A-Z]", password):
            return apology("Password must contain at least one uppercase letter", 400)

        if not re.search(r"\d", password):
            return apology("Password must contain at least one digit", 400)

        if len(password) < 8:
            return apology("Password must be at least eight characters long", 400)

        # Validate email format
        email = request.form.get("username")
        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            return apology("Invalid email format", 400)

        hashed_password = generate_password_hash(password)

        # Check if the username (email) already exists
        with sqlite3.connect(DB_FILE) as conn:
            cursor = conn.cursor()
            existing_user = cursor.execute(
                "SELECT * FROM users WHERE username = ?", (email,)
            ).fetchone()

        if existing_user:
            return apology("Email already exists")

        # Insert the username (email) into the database
        with sqlite3.connect(DB_FILE) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO users (username, hash) VALUES (?, ?)",
                (email, hashed_password),
            )
            conn.commit()

        # Redirect user to the home page
        return redirect("/")

    else:
        return render_template("register.html")
    
@app.route("/")
@login_required
def map():
    data = get_api_data_for_map()
    catastrophes = data.get('events', [])

    # Organize events by category
    events_by_category = {}
    for catastrophe in catastrophes:
        category = catastrophe.get('categories', [{}])[0].get('title', 'Other')
        events_by_category.setdefault(category, []).append(catastrophe)

    return render_template('index.html', events_by_category=events_by_category)

@app.route('/get_catastrophes', methods=['GET'])
@login_required
def get_catastrophes():
    # Logic to retrieve data on natural disasters
    start_index = int(request.args.get('start_index', 1))
    data = get_api_data_for_hist(start_index)
    return jsonify(data)

@app.route('/change_password', methods=['GET', 'POST'])
@login_required
def change_password():
    if request.method == 'POST':
        # Get the form information
        current_password = request.form.get('current_password')
        new_password = request.form.get('new_password')
        confirmation = request.form.get('confirmation')

        # Validate that the fields are not empty
        if not current_password or not new_password or not confirmation:
            return apology('All fields are required', 400)

        # Validate that the new password and confirmation match
        if new_password != confirmation:
            return apology('The new password and confirmation do not match', 400)

        # Get information about the current user
        user_id = session.get('user_id')
        with sqlite3.connect(DB_FILE) as conn:
            cursor = conn.cursor()
            user = cursor.execute(
                "SELECT * FROM users WHERE id = ?", (user_id,)
            ).fetchone()

        # Verify the current password
        if not user or not check_password_hash(user[2], current_password):
            return apology('Incorrect current password', 403)

        # Check if the new password is the same as the current one
        if check_password_hash(user[2], new_password):
            return apology('New password must be different from the current one', 400)

        # Check password requirements
        if not re.search(r"[A-Z]", new_password):
            return apology("New password must contain at least one uppercase letter", 400)

        if not re.search(r"\d", new_password):
            return apology("New password must contain at least one digit", 400)

        if len(new_password) < 8:
            return apology("New password must be at least eight characters long", 400)

        # Generate the hash of the new password
        hashed_password = generate_password_hash(new_password)

        # Update the password in the database
        with sqlite3.connect(DB_FILE) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE users SET hash = ? WHERE id = ?",
                (hashed_password, user_id)
            )
            conn.commit()

        return redirect('/')

    else:
        return render_template("change_password.html")
