import flask

from handlers import copy
from db import users, helpers, posts as db_posts

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
    db = helpers.load_db()

    username = flask.request.form.get('username')
    password = flask.request.form.get('password')

    # 1. Check if the user exists
    user = users.get_user_by_name(db, username)
    if not user:
        flask.flash(f'User "{username}" does not exist.', 'danger')
        return flask.redirect(flask.url_for('login.loginscreen'))

    # 2. Validate password
    if user['password'] == password:
        # ✅ Successful login
        resp = flask.make_response(flask.redirect(flask.url_for('login.index')))
        resp.set_cookie('username', username, path='/')  # <-- cookie available site-wide
        resp.set_cookie('password', password, path='/')
        return resp

    else:
        # ❌ Wrong password
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

    # 1. Authentication Check
    username = flask.request.cookies.get('username')
    password = flask.request.cookies.get('password')
    
    if not username or not password:
        flask.flash('You need to be logged in to access the feed.', 'danger')
        return flask.redirect(flask.url_for('login.loginscreen'))
    
    user = users.get_user(db, username, password)
    
    if not user:
        flask.flash('Invalid credentials. Please try again.', 'danger')
        # Clear bad cookies and redirect
        resp = flask.make_response(flask.redirect(flask.url_for('login.loginscreen')))
        resp.set_cookie('username', '', expires=0)
        resp.set_cookie('password', '', expires=0)
        return resp

    # --- DEBUGGING OUTPUT (Check your terminal for this!) ---
    # We keep the debugging for friend status, but we change how posts are fetched.
    print(f"\n--- DEBUG FEED FETCH for User: {username} ---")

    # 2. Data Aggregation
    
    # Get the list of friends (still needed for the sidebar)
    friends = users.get_user_friends(db, user)
    
    # DEBUG: Print friends list to verify
    print(f"Friends fetched: {[f['username'] for f in friends]}")
    
    # NEW FIX: Fetch ALL valid posts from the entire database, 
    # since friend lists are currently empty.
    all_posts = db_posts.get_all_valid_posts(db)
    
    # DEBUG: Total count
    print(f"Total valid posts found across ALL users: {len(all_posts)}")
    print("------------------------------------------\n")
    
    # 3. Sort Posts
    # Sort the aggregated list of posts by 'time', newest first
    sorted_posts = sorted(all_posts, key=lambda post: post['time'], reverse=True)

    # 4. Render Template
    # Using getattr for config variables ensures a fallback if the copy module is missing data
    return flask.render_template('feed.html', 
                                 title=getattr(copy, 'title', 'Celebrity Feed'),
                                 subtitle=getattr(copy, 'subtitle', 'Latest Gossip'), 
                                 user=user, 
                                 username=username,
                                 friends=friends, 
                                 posts=sorted_posts)

