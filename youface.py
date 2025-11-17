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
from handlers import friends, login, posts, leaderboard
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

@app.route('/profile')
def profile():
    """Displays the currently logged-in user's profile page."""
    username = flask.request.cookies.get('username')
    password = flask.request.cookies.get('password') # Get password from cookie

    if not username or not password:
        flask.flash('You must be logged in to view your profile.', 'warning')
        return flask.redirect(flask.url_for('login.loginscreen'))

    # --- Load DB and verify user ---
    # We pass the 'db' instance from the top of this file
    user_doc = users.get_user(db, username, password) 
    
    if not user_doc:
        # User/pass combination is invalid, clear cookies and redirect
        flask.flash('Your login session is invalid. Please log in again.', 'danger')
        resp = flask.make_response(flask.redirect(flask.url_for('login.loginscreen')))
        resp.set_cookie('username', '', expires=0)
        resp.set_cookie('password', '', expires=0)
        return resp

    # user_doc is the user's dictionary. Pass it to the template.
    return flask.render_template('profile.html', user=user_doc)

# --- DELETED ---
# The old, conflicting @app.route('/leaderboard') was removed.
# The app will now correctly use the 'leaderboard.blueprint'.


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
app.register_blueprint(leaderboard.blueprint)


# ==============================
# MAIN APP ENTRY
# ==============================

if __name__ == "__main__":
    # --- Run the migration check *before* starting the server ---
    run_db_migration(db)
    
    # --- Start the app ---
    app.run(debug=True, host='0.0.0.0', port=5005)