# ==============================
# youface.py
# ==============================

# --- Standard Imports ---
import os
import time

# --- Installed Imports ---
import flask
import timeago
from tinydb import TinyDB, Query  # ✅ import TinyDB and Query properly

# --- Handlers ---
from handlers import friends, login, posts
from db import helpers, users

# --- Project Root ---
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))

# --- Flask App Setup ---
app = flask.Flask(
    __name__,
    template_folder=os.path.join(PROJECT_ROOT, 'templates')
)

# --- Secret & Config ---
app.secret_key = 'mygroup'
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0


# --- Database Setup ---
# ✅ Initialize your TinyDB database and User query object
db_path = os.path.join(PROJECT_ROOT, 'db.json')
db = TinyDB(db_path)
User = Query()


# --- NEW: Database Migration Function ---
def run_db_migration(db):
    """
    Checks all users in the DB and adds missing fields to ensure
    compatibility with the new friend request AND follow system.
    """
    print("Checking database schema...")
    users_table = db.table('users')
    User = Query()
    
    # --- UPDATED: Added new 'following' and 'followers' fields ---
    default_schema = {
        'friends': [],
        'pending_requests_received': [],
        'pending_requests_sent': [],
        'following': [],
        'followers': []
    }
    
    # --- UPDATED: The query now checks for all 5 keys ---
    query = (
        (~ User.friends.exists()) |
        (~ User.pending_requests_received.exists()) |
        (~ User.pending_requests_sent.exists()) |
        (~ User.following.exists()) |
        (~ User.followers.exists())
    )
    users_to_migrate = users_table.search(query)

    if not users_to_migrate:
        print("Database schema is up-to-date. No migration needed.")
        return

    print(f"Found {len(users_to_migrate)} user(s) needing migration...")
    
    for user_doc in users_to_migrate:
        update_data = {}
        
        # Check for each key individually to be safe
        for key, default_value in default_schema.items():
            if key not in user_doc:
                update_data[key] = default_value
        
        if update_data:
            print(f"  -> Migrating user: {user_doc['username']}")
            users_table.update(update_data, User.username == user_doc['username'])
            
    print("Database migration complete.")


# ==============================
# ROUTES
# ==============================

@app.route('/settings')
def settings():
    return "Settings page coming soon!"

@app.route('/logout')
def logout():
    """Logs the user out by clearing cookies."""
    resp = flask.make_response(flask.redirect(flask.url_for('login.loginscreen')))
    resp.set_cookie('username', '', expires=0)
    resp.set_cookie('password', '', expires=0)
    return resp


@app.route('/profile')
def profile():
    # --- Get cookies ---
    username = flask.request.cookies.get('username')
    password = flask.request.cookies.get('password')

    # --- Require login ---
    if not username or not password:
        return flask.redirect(flask.url_for('login.loginscreen'))

    # --- Load DB and verify user ---
    # Use the global 'db' variable
    user = users.get_user(db, username, password)
    if not user:
        return flask.redirect(flask.url_for('login.loginscreen'))

    # --- Render profile ---
    return flask.render_template('profile.html', user=user)


# ==============================
# TEMPLATE FILTERS
# ==============================

@app.template_filter('convert_time')
def convert_time(ts):
    """A Jinja template helper to convert timestamps to timeago format."""
    return timeago.format(ts, time.time())


# ==============================
# BLUEPRINT REGISTRATION
# ==============================

app.register_blueprint(friends.blueprint)
app.register_blueprint(login.blueprint)
app.register_blueprint(posts.blueprint)


# ==============================
# MAIN APP ENTRY
# ==============================

if __name__ == "__main__":
    # --- Run the migration check *before* starting the server ---
    run_db_migration(db)
    
    # --- Start the app ---
    app.run(debug=True, host='0.0.0.0', port=5005)