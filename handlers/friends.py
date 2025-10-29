import flask

# Assuming these imports are correct based on your previous code structure
from handlers import copy
from db import posts, users, helpers

# Initialize the Flask Blueprint
blueprint = flask.Blueprint("friends", __name__)

@blueprint.route('/addfriend', methods=['POST'])
def addfriend():
    """Adds a friend to the user's friends list."""
    db = helpers.load_db()

    # Make sure the user is logged in (Authentication check)
    username = flask.request.cookies.get('username')
    password = flask.request.cookies.get('password')

    if username is None and password is None:
        return flask.redirect(flask.url_for('login.loginscreen'))

    user = users.get_user(db, username, password)
    if not user:
        flask.flash('You need to be logged in to do that.', 'danger')
        return flask.redirect(flask.url_for('login.loginscreen'))

    # Add the friend
    name = flask.request.form.get('name')
    msg, category = users.add_user_friend(db, user, name)

    flask.flash(msg, category)
    return flask.redirect(flask.url_for('login.index'))

@blueprint.route('/unfriend', methods=['POST'])
def unfriend():
    """Removes a user from the user's friends list."""
    db = helpers.load_db()

    # Authentication check
    username = flask.request.cookies.get('username')
    password = flask.request.cookies.get('password')

    user = users.get_user(db, username, password)
    if not user:
        flask.flash('You need to be logged in to do that.', 'danger')
        return flask.redirect(flask.url_for('login.loginscreen'))

    # Remove the friend
    name = flask.request.form.get('name')
    msg, category = users.remove_user_friend(db, user, name)

    flask.flash(msg, category)
    return flask.redirect(flask.url_for('login.index'))

@blueprint.route('/friend/<fname>')
def view_friend(fname):
    """View the page of a given friend (single profile view)."""
    db = helpers.load_db()

    # Authentication check
    username = flask.request.cookies.get('username')
    password = flask.request.cookies.get('password')

    user = users.get_user(db, username, password)
    if not user:
        flask.flash('You must be logged in to do that.', 'danger')
        return flask.redirect(flask.url_for('login.loginscreen'))

    # Retrieve the specific friend's data and their posts
    friend = users.get_user_by_name(db, fname)
    if not friend:
        flask.flash(f"User '{fname}' not found.", 'danger')
        return flask.redirect(flask.url_for('friends.friends_list')) 

    all_posts = posts.get_posts(db, friend)[::-1] # reverse order

    return flask.render_template(
        'friend.html', 
        title=copy.title,
        subtitle=copy.subtitle, 
        user=user, 
        username=username,
        friend=friend['username'],
        friends=users.get_user_friends(db, user), 
        posts=all_posts
    )

# --- NEW ROUTE: Displays the list of all friends ---
@blueprint.route('/friends')
def friends_list():
    """Renders the main page showing the list of the current user's friends."""
    db = helpers.load_db()

    # Authentication Check
    username = flask.request.cookies.get('username')
    password = flask.request.cookies.get('password')

    user = users.get_user(db, username, password)
    if not user:
        flask.flash('You must be logged in to view your friends.', 'danger')
        return flask.redirect(flask.url_for('login.loginscreen'))

    # Fetch real data using your DB helper
    current_friends_list = users.get_user_friends(db, user)

    # Render the 'friends.html' template
    return flask.render_template(
        'friends.html', 
        title=copy.title,
        subtitle=copy.subtitle, 
        user=user, 
        username=username,
        friends=current_friends_list # This list populates the template
    )
    
# --- MISSING ROUTE: Resolves the BuildError from friends.html ---
@blueprint.route('/find_users')
def find_users():
    """Handles the page where the user can search for and add new users."""
    db = helpers.load_db()

    # Authentication Check
    username = flask.request.cookies.get('username')
    password = flask.request.cookies.get('password')

    user = users.get_user(db, username, password)
    if not user:
        flask.flash('You must be logged in to search for users.', 'danger')
        return flask.redirect(flask.url_for('login.loginscreen'))
        
    # In a real app, you'd handle search forms and query the DB for users here.
    # For now, we'll just redirect to the index or a dedicated search template.
    
    # You will need to create a 'find_users.html' template for this route.
    # For testing, we'll redirect back to the friend list with a message.
    flask.flash("User search feature is coming soon!", "info")
    return flask.redirect(flask.url_for('friends.friends_list'))
    
# You can uncomment and update the above to render a new template later:
# return flask.render_template(
#     'find_users.html', 
#     title=copy.title,
#     subtitle=copy.subtitle, 
#     user=user, 
#     username=username,
#     search_results=[]
# )
