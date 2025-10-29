# std imports
import time
import os # <-- NEW IMPORT

# installed imports
import flask
import timeago
import tinydb

# handlers
from handlers import friends, login, posts

# 1. --- Define Project Root for Robust Template Loading ---
# This ensures Flask knows where to look for the 'templates' folder,
# regardless of where the script is executed from.
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__)) 

app = flask.Flask(
    __name__,
    # 2. --- Explicitly set the template folder path ---
    template_folder=os.path.join(PROJECT_ROOT, 'templates')
)

@app.route('/logout')
def logout():
    resp = flask.make_response(flask.redirect(flask.url_for('login.loginscreen')))
    resp.set_cookie('username', '', expires=0)
    resp.set_cookie('password', '', expires=0)
    return resp

@app.template_filter('convert_time')
def convert_time(ts):
    """A jinja template helper to convert timestamps to timeago."""
    return timeago.format(ts, time.time())

app.register_blueprint(friends.blueprint)
app.register_blueprint(login.blueprint)
app.register_blueprint(posts.blueprint)

app.secret_key = 'mygroup'
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

# Note: The 'if __name__ == "__main__":' guard is good practice, 
# but I'll stick to your original code's structure for simplicity here.
app.run(debug=True, host='0.0.0.0', port=5005)
