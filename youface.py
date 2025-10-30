# ==============================
# youface.py
# ==============================

# --- Standard Imports ---
import os
import time

# --- Installed Imports ---
import flask
import timeago
import tinydb

# --- Handlers ---
from handlers import friends, login, posts

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

# --- Database (TinyDB) Setup ---
db = tinydb.TinyDB(os.path.join(PROJECT_ROOT, 'database.json'))
User = tinydb.Query()

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

    user_record = db.search(User.username == username)
    if not user_record:
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
    app.run(debug=True, host='0.0.0.0', port=5005)

