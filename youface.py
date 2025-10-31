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
    db = helpers.load_db()
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
    app.run(debug=True, host='0.0.0.0', port=5005)

