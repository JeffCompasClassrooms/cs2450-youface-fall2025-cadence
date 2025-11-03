import flask

# Assuming these imports are correct based on your previous code structure
from handlers import copy
from db import posts, users, helpers

# Initialize the Flask Blueprint
blueprint = flask.Blueprint("friends", __name__)

# --- NEW/UPDATED ROUTES for Request System ---

@blueprint.route('/send_request', methods=['POST'])
def send_request():
    """Sends a friend request to another user."""
    db = helpers.load_db()
    
    # Authentication check
    username = flask.request.cookies.get('username')
    password = flask.request.cookies.get('password')
    user = users.get_user(db, username, password)
    if not user:
        flask.flash('You need to be logged in to do that.', 'danger')
        return flask.redirect(flask.url_for('login.loginscreen'))

    # Get the username from the form
    recipient_username = flask.request.form.get('username')
    if not recipient_username:
        flask.flash('No user specified.', 'warning')
        return flask.redirect(flask.url_for('friends.friends_list'))

    # Call your new DB helper function
    # This function should add recipient to user['pending_requests_sent']
    # and add user to recipient['pending_requests_received']
    msg, category = users.send_friend_request(db, user, recipient_username)
    
    flask.flash(msg, category)
    # Redirect back to the page they were on
    return flask.redirect(flask.request.referrer or flask.url_for('friends.friends_list'))


@blueprint.route('/accept_request', methods=['POST'])
def accept_request():
    """Accepts a pending friend request."""
    db = helpers.load_db()
    
    # Authentication check
    username = flask.request.cookies.get('username')
    password = flask.request.cookies.get('password')
    user = users.get_user(db, username, password)
    if not user:
        return flask.redirect(flask.url_for('login.loginscreen'))

    requestor_username = flask.request.form.get('username')

    # Call your new DB helper function
    # This function should:
    # 1. Remove requestor from user['pending_requests_received']
    # 2. Remove user from requestor['pending_requests_sent']
    # 3. Add requestor to user['friends']
    # 4. Add user to requestor['friends']
    msg, category = users.accept_friend_request(db, user, requestor_username)
    
    flask.flash(msg, category)
    return flask.redirect(flask.url_for('friends.friends_list'))


@blueprint.route('/reject_request', methods=['POST'])
def reject_request():
    """Rejects or cancels a pending friend request."""
    db = helpers.load_db()
    
    # Authentication check
    username = flask.request.cookies.get('username')
    password = flask.request.cookies.get('password')
    user = users.get_user(db, username, password)
    if not user:
        return flask.redirect(flask.url_for('login.loginscreen'))

    other_username = flask.request.form.get('username')

    # Call your new DB helper function
    # This function should:
    # 1. Remove other_username from user['pending_requests_received']
    # 2. Remove user from other_username['pending_requests_sent']
    msg, category = users.reject_friend_request(db, user, other_username)
    
    flask.flash(msg, category)
    return flask.redirect(flask.url_for('friends.friends_list'))


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

    # This route remains largely the same
    name = flask.request.form.get('name')
    msg, category = users.remove_user_friend(db, user, name)

    flask.flash(msg, category)
    return flask.redirect(flask.url_for('friends.friends_list'))

# --- UPDATED VIEW ROUTES ---

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

@blueprint.route('/friends')
def friends_list():
    """Renders the main page showing friends, requests, and suggestions."""
    db = helpers.load_db()

    # Authentication Check
    username = flask.request.cookies.get('username')
    password = flask.request.cookies.get('password')
    user = users.get_user(db, username, password)
    if not user:
        flask.flash('You must be logged in to view your friends.', 'danger')
        return flask.redirect(flask.url_for('login.loginscreen'))

    # Fetch all the data needed for the template
    current_friends = users.get_user_friends(db, user)
    pending_requests = users.get_pending_requests(db, user)
    # Get a few suggestions for the "People You May Know" box
    potential_friends = users.get_potential_friends(db, user, limit=5)

    # Render the 'friends.html' template
    return flask.render_template(
        'friends.html', 
        title=copy.title,
        subtitle=copy.subtitle, 
        user=user, 
        username=username,
        friends=current_friends,
        pending_requests=pending_requests,
        potential_friends=potential_friends
        # Note: search_results is not defined here, so the 'else' block
        # in the template's right column will be used.
    )
    

@blueprint.route('/find_users')
def find_users():
    """Handles the user search and displays results on the same friends page."""
    db = helpers.load_db()

    # Authentication Check
    username = flask.request.cookies.get('username')
    password = flask.request.cookies.get('password')
    user = users.get_user(db, username, password)
    if not user:
        flask.flash('You must be logged in to search for users.', 'danger')
        return flask.redirect(flask.url_for('login.loginscreen'))
        
    # Get the search query from the URL
    query = flask.request.args.get('query', '')
    
    # --- This route now re-renders friends.html, just like friends_list ---
    # But it passes an *additional* variable: search_results
    
    # Fetch all the data needed for the template
    current_friends = users.get_user_friends(db, user)
    pending_requests = users.get_pending_requests(db, user)
    
    # Get search results using your new helper
    if query:
        search_results = users.get_potential_friends(db, user, query=query)
    else:
        # If search is empty, show all potential friends
        search_results = users.get_potential_friends(db, user)

    # We pass search_results, which the template will use for the right column
    # We don't need potential_friends here since search_results takes precedence
    return flask.render_template(
        'friends.html', 
        title=copy.title,
        subtitle=copy.subtitle, 
        user=user, 
        username=username,
        friends=current_friends,
        pending_requests=pending_requests,
        search_results=search_results, # This is the key variable for the search
        query=query # Pass the query back to pre-fill the search box
    )