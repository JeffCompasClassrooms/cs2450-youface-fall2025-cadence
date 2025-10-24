import flask

from handlers import copy
from db import posts, users, helpers

blueprint = flask.Blueprint("login", __name__)

@blueprint.route('/loginscreen')
def loginscreen():
    """Present a form to the user to enter their username and password."""
    db = helpers.load_db()

    # First check if already logged in
    username = flask.request.cookies.get('username')
    password = flask.request.cookies.get('password')

    if username is not None and password is not None:
        if users.get_user(db, username, password):
            # If they are logged in, redirect them to the feed page
            flask.flash('You are already logged in.', 'warning')
            return flask.redirect(flask.url_for('login.index'))

    return flask.render_template('of_login', title=copy.title,
                                 subtitle=copy.subtitle)

@blueprint.route('/login', methods=['POST'])
def login():
    """Log in the user.

    Using the username and password fields on the form, log in a user.
    """
    db = helpers.load_db()

    username = flask.request.form.get('username')
    password = flask.request.form.get('password')

    # --- UPDATED LOGIN LOGIC ---

    # 1. First, check if the user *exists* at all
    user = users.get_user_by_name(db, username)

    if not user:
        # Case 1: Username not found
        flask.flash(f'User "{username}" does not exist.', 'danger')
        return flask.redirect(flask.url_for('login.loginscreen'))

    # 2. User exists, *now* check the password
    if user['password'] == password:
        # Case 2a: Password is correct (Successful login)
        resp = flask.make_response(flask.redirect(flask.url_for('login.index')))
        resp.set_cookie('username', username)
        resp.set_cookie('password', password)

        return resp
    else:
        # Case 2b: Password is incorrect
        flask.flash('Incorrect password. Please try again.', 'danger')
        return flask.redirect(flask.url_for('login.loginscreen'))


@blueprint.route('/createaccount')
def createaccount_page():
    """Serves the page for creating a new account."""
    return flask.render_template('create_account', title=copy.title,
                                 subtitle=copy.subtitle)

@blueprint.route('/createaccount', methods=['POST'])
def createaccount_submit():
    """Handles the submission of the new account form."""
    db = helpers.load_db()

    username = flask.request.form.get('username')
    password = flask.request.form.get('password')
    confirm = flask.request.form.get('confirm')

    # --- Validation ---
    if not username or not password or not confirm:
        flask.flash('All fields are required.', 'danger')
        return flask.redirect(flask.url_for('login.createaccount_page'))

    if password != confirm:
        flask.flash('Passwords do not match. Please try again.', 'danger')
        return flask.redirect(flask.url_for('login.createaccount_page'))
    
    # Try to create the new user
    if users.new_user(db, username, password) is None:
        flask.flash(f'Username {username} already taken!', 'danger')
        return flask.redirect(flask.url_for('login.createaccount_page'))

    # Redirect back to the login screen so they can log in
    flask.flash(f'User {username} created successfully! Please log in.', 'success') # Test Message
    return flask.redirect(flask.url_for('login.loginscreen'))


@blueprint.route('/')
def index():
    """Serves the main feed page for the user."""
    db = helpers.load_db()

    # make sure the user is logged in
    username = flask.request.cookies.get('username')
    password = flask.request.cookies.get('password')
    if username is None or password is None: # Added 'or' for safety
        return flask.redirect(flask.url_for('login.loginscreen'))
    
    user = users.get_user(db, username, password)
    if not user:
        flask.flash('Invalid credentials. Please try again.', 'danger')
        # Clear bad cookies
        resp = flask.make_response(flask.redirect(flask.url_for('login.loginscreen')))
        resp.set_cookie('username', '', expires=0)
        resp.set_cookie('password', '', expires=0)
        return resp

    # get the info for the user's feed
    friends = users.get_user_friends(db, user)
    all_posts = []
    for friend in friends + [user]:
        all_posts += posts.get_posts(db, friend)
    
    # sort posts
    sorted_posts = sorted(all_posts, key=lambda post: post['time'], reverse=True)

    return flask.render_template('feed.html', title=copy.title,
                                 subtitle=copy.subtitle, user=user, username=username,
                                 friends=friends, posts=sorted_posts)


