import flask

# Assuming these imports are correct based on your previous code structure
from handlers import copy
from db import posts, users, helpers

# Initialize the Flask Blueprint
blueprint = flask.Blueprint("friends", __name__)

# --- FRIEND REQUEST ROUTES ---

@blueprint.route('/send_request', methods=['POST'])
def send_request():
    db = helpers.load_db()
    username = flask.request.cookies.get('username')
    password = flask.request.cookies.get('password')
    user = users.get_user(db, username, password)
    if not user:
        flask.flash('You need to be logged in to do that.', 'danger')
        return flask.redirect(flask.url_for('login.loginscreen'))

    recipient_username = flask.request.form.get('username')
    msg, category = users.send_friend_request(db, user, recipient_username)
    
    flask.flash(msg, category)
    return flask.redirect(flask.request.referrer or flask.url_for('friends.friends_list'))


@blueprint.route('/accept_request', methods=['POST'])
def accept_request():
    db = helpers.load_db()
    username = flask.request.cookies.get('username')
    password = flask.request.cookies.get('password')
    user = users.get_user(db, username, password)
    if not user:
        return flask.redirect(flask.url_for('login.loginscreen'))

    requestor_username = flask.request.form.get('username')
    msg, category = users.accept_friend_request(db, user, requestor_username)
    
    flask.flash(msg, category)
    return flask.redirect(flask.url_for('friends.friends_list'))


@blueprint.route('/reject_request', methods=['POST'])
def reject_request():
    db = helpers.load_db()
    username = flask.request.cookies.get('username')
    password = flask.request.cookies.get('password')
    user = users.get_user(db, username, password)
    if not user:
        return flask.redirect(flask.url_for('login.loginscreen'))

    other_username = flask.request.form.get('username')
    msg, category = users.reject_friend_request(db, user, other_username)
    
    flask.flash(msg, category)
    return flask.redirect(flask.url_for('friends.friends_list'))


@blueprint.route('/unfriend', methods=['POST'])
def unfriend():
    db = helpers.load_db()
    username = flask.request.cookies.get('username')
    password = flask.request.cookies.get('password')
    user = users.get_user(db, username, password)
    if not user:
        flask.flash('You need to be logged in to do that.', 'danger')
        return flask.redirect(flask.url_for('login.loginscreen'))

    name = flask.request.form.get('name')
    msg, category = users.remove_user_friend(db, user, name)

    flask.flash(msg, category)
    return flask.redirect(flask.url_for('friends.friends_list'))


# --- NEW FOLLOW/UNFOLLOW ROUTES ---

@blueprint.route('/follow', methods=['POST'])
def follow():
    """Follows a user."""
    db = helpers.load_db()
    
    # Authentication check
    username = flask.request.cookies.get('username')
    password = flask.request.cookies.get('password')
    user = users.get_user(db, username, password)
    if not user:
        flask.flash('You need to be logged in to do that.', 'danger')
        return flask.redirect(flask.url_for('login.loginscreen'))

    user_to_follow_name = flask.request.form.get('username')
    if not user_to_follow_name:
        flask.flash('No user specified.', 'warning')
        return flask.redirect(flask.url_for('friends.friends_list'))

    msg, category = users.follow_user(db, user, user_to_follow_name)
    
    flask.flash(msg, category)
    return flask.redirect(flask.request.referrer or flask.url_for('friends.friends_list'))


@blueprint.route('/unfollow', methods=['POST'])
def unfollow():
    """Unfollows a user."""
    db = helpers.load_db()
    
    # Authentication check
    username = flask.request.cookies.get('username')
    password = flask.request.cookies.get('password')
    user = users.get_user(db, username, password)
    if not user:
        flask.flash('You need to be logged in to do that.', 'danger')
        return flask.redirect(flask.url_for('login.loginscreen'))

    user_to_unfollow_name = flask.request.form.get('username')
    if not user_to_unfollow_name:
        flask.flash('No user specified.', 'warning')
        return flask.redirect(flask.url_for('friends.friends_list'))

    msg, category = users.unfollow_user(db, user, user_to_unfollow_name)
    
    flask.flash(msg, category)
    return flask.redirect(flask.request.referrer or flask.url_for('friends.friends_list'))


# --- UPDATED VIEW ROUTES ---

@blueprint.route('/friend/<fname>')
def view_friend(fname):
    """View the page of a given friend (single profile view)."""
    db = helpers.load_db()

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

    username = flask.request.cookies.get('username')
    password = flask.request.cookies.get('password')
    user = users.get_user(db, username, password)
    if not user:
        flask.flash('You must be logged in to view your friends.', 'danger')
        return flask.redirect(flask.url_for('login.loginscreen'))

    current_friends = users.get_user_friends(db, user)
    pending_requests = users.get_pending_requests(db, user)
    
    # This now correctly gets only users with no relationship
    potential_friends = users.get_potential_friends(db, user, limit=5)

    return flask.render_template(
        'friends.html', 
        title=copy.title,
        subtitle=copy.subtitle, 
        user=user, 
        username=username,
        friends=current_friends,
        pending_requests=pending_requests,
        potential_friends=potential_friends
    )
    

@blueprint.route('/find_users')
def find_users():
    """
    Handles user search. This is now more powerful.
    It searches ALL users and lets the template decide which button to show.
    """
    db = helpers.load_db()

    username = flask.request.cookies.get('username')
    password = flask.request.cookies.get('password')
    user = users.get_user(db, username, password)
    if not user:
        flask.flash('You must be logged in to search for users.', 'danger')
        return flask.redirect(flask.url_for('login.loginscreen'))
        
    query = flask.request.args.get('query', '')
    
    # Fetch common data
    current_friends = users.get_user_friends(db, user)
    pending_requests = users.get_pending_requests(db, user)
    
    # --- NEW SEARCH LOGIC ---
    # Search all users in the DB
    all_users = db.table('users').all()
    search_results = []
    if query:
        for u in all_users:
            # Add if query matches and is NOT the user themselves
            if query.lower() in u['username'].lower() and u['username'] != user['username']:
                search_results.append(u)
    else:
        # If no query, just show nothing for search
        search_results = [] # Or you could use get_potential_friends here
        
    return flask.render_template(
        'freinds.html', 
        title=copy.title,
        subtitle=copy.subtitle, 
        user=user, 
        username=username,
        friends=current_friends,
        pending_requests=pending_requests,
        search_results=search_results, # Pass the new search results
        query=query
    )