# ==============================
# youface.py
# ==============================

# --- Standard Imports ---
import os
import time

# --- Installed Imports ---
import flask
import timeago
from tinydb import TinyDB, Query
from tinydb.operations import delete # ✅ Import 'delete' operation

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
db_path = os.path.join(PROJECT_ROOT, 'db.json')
db = TinyDB(db_path)
User = Query()


# --- UPDATED: Database Migration Function ---
def run_db_migration(db):
    """
    Checks all users in the DB and migrates to the new follow-only system.
    1. Adds 'following' and 'followers' if they don't exist.
    2. Deletes old 'friends', 'pending_requests_received', 'pending_requests_sent'.
    """
    print("Checking database schema...")
    users_table = db.table('users')
    User = Query()
    
    # --- 1. Add new fields ---
    print("Step 1: Adding 'following' and 'followers' fields...")
    default_schema = {
        'following': [],
        'followers': []
    }
    query_add = (
        (~ User.following.exists()) |
        (~ User.followers.exists())
    )
    users_to_add = users_table.search(query_add)

    if not users_to_add:
        print(" -> 'following' and 'followers' fields are up-to-date.")
    else:
        print(f" -> Found {len(users_to_add)} user(s) needing new fields...")
        for user_doc in users_to_add:
            update_data = {}
            for key, default_value in default_schema.items():
                if key not in user_doc:
                    update_data[key] = default_value
            
            if update_data:
                print(f"    -> Migrating user: {user_doc['username']}")
                users_table.update(update_data, User.username == user_doc['username'])
    
    # --- 2. Remove old, deprecated fields ---
    print("\nStep 2: Removing deprecated 'friends' and 'pending_requests' fields...")
    
    # Check and remove 'friends'
    if users_table.search(User.friends.exists()):
        print(" -> Removing 'friends' field from users...")
        users_table.update(delete('friends'), User.friends.exists())
    else:
        print(" -> 'friends' field already removed.")
        
    # Check and remove 'pending_requests_received'
    if users_table.search(User.pending_requests_received.exists()):
        print(" -> Removing 'pending_requests_received' field from users...")
        users_table.update(delete('pending_requests_received'), User.pending_requests_received.exists())
    else:
        print(" -> 'pending_requests_received' field already removed.")

    # Check and remove 'pending_requests_sent'
    if users_table.search(User.pending_requests_sent.exists()):
        print(" -> Removing 'pending_requests_sent' field from users...")
        users_table.update(delete('pending_requests_sent'), User.pending_requests_sent.exists())
    else:
        print(" -> 'pending_requests_sent' field already removed.")
        
    print("\nDatabase migration complete.")


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


# ==============================
# ROUTES
# ==============================

@app.route('/logout')
def logout():
    """Logs the user out by clearing cookies."""
    resp = flask.make_response(flask.redirect(flask.url_for('login.loginscreen')))
    resp.set_cookie('username', '', expires=0)
    resp.set_cookie('password', '', expires=0)
    return resp


@app.route('/profile')
def profile():
    username = flask.request.cookies.get('username')
    if not username:
        return flask.redirect(flask.url_for('login.loginscreen'))

    # --- Load DB and verify user ---
    user = users.get_user(db, username, password)
    if not user:
        return flask.redirect(flask.url_for('login.loginscreen'))

    user_info = user_record[0]
    return flask.render_template('profile.html', user=user_info)


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