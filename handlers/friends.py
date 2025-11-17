import flask

# Assuming these imports are correct based on your previous code structure
from handlers import copy
from db import posts, users, helpers

# Initialize the Flask Blueprint
blueprint = flask.Blueprint("friends", __name__)

# --- GONE: All send_request, accept_request, reject_request, unfriend routes ---


# --- NEW FOLLOW/UNFOLLOW ROUTES (These are the main actions) ---

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
    # Redirect back to the page the user was on
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
    # Redirect back to the page the user was on
    return flask.redirect(flask.request.referrer or flask.url_for('friends.friends_list'))


# --- UPDATED VIEW ROUTES ---

@blueprint.route('/friend/<fname>')
def view_friend(fname):
    """View the page of a given user (single profile view)."""
    db = helpers.load_db()

    username = flask.request.cookies.get('username')
    password = flask.request.cookies.get('password')
    user = users.get_user(db, username, password)
    if not user:
        flask.flash('You must be logged in to do that.', 'danger')
        return flask.redirect(flask.url_for('login.loginscreen'))

    # Renamed 'friend' to 'profile_user' for clarity
    profile_user = users.get_user_by_name(db, fname)
    if not profile_user:
        flask.flash(f"User '{fname}' not found.", 'danger')
        return flask.redirect(flask.url_for('friends.friends_list')) 

    all_posts = posts.get_posts(db, profile_user)[::-1] # reverse order

    return flask.render_template(
        'friend.html', 
        title=copy.title,
        subtitle=copy.subtitle, 
        user=user, 
        username=username,
        friend=profile_user['username'], # template might still use 'friend'
        # Pass the new lists to the template
        friends=users.get_user_friends(db, user), 
        following=users.get_user_following(db, user),
        followers=users.get_user_followers(db, user),
        posts=all_posts,
        active_page='friends' 
    )

@blueprint.route('/friends')
def friends_list():
    """Renders the main page showing Friends, Following, Followers, and Suggestions."""
    db = helpers.load_db()

    username = flask.request.cookies.get('username')
    password = flask.request.cookies.get('password')
    user = users.get_user(db, username, password)
    if not user:
        flask.flash('You must be logged in to view your friends.', 'danger')
        return flask.redirect(flask.url_for('login.loginscreen'))

    # --- Get the three new lists ---
    friends = users.get_user_friends(db, user) # Mutuals
    following = users.get_user_following(db, user) # People I follow
    followers = users.get_user_followers(db, user) # People following me
    
    # This now correctly gets only users the user is NOT following
    potential_friends = users.get_potential_friends(db, user, limit=5)

    return flask.render_template(
        'friends.html', 
        title=copy.title,
        subtitle=copy.subtitle, 
        user=user, 
        username=username,
        friends=friends,
        following=following,
        followers=followers,
        potential_friends=potential_friends,
        active_page='friends' 
    )
    

@blueprint.route('/find_users')
def find_users():
    """
    Handles user search. This renders the same 'friends.html' template
    but passes 'search_results' to the sidebar.
    """
    db = helpers.load_db()

    username = flask.request.cookies.get('username')
    password = flask.request.cookies.get('password')
    user = users.get_user(db, username, password)
    if not user:
        flask.flash('You must be logged in to search for users.', 'danger')
        return flask.redirect(flask.url_for('login.loginscreen'))
        
    query = flask.request.args.get('query', '')
    
    # --- Fetch all necessary data for the template ---
    friends = users.get_user_friends(db, user)
    following = users.get_user_following(db, user)
    followers = users.get_user_followers(db, user)
    
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
        search_results = []
        
    return flask.render_template(
        'friends.html', # Fixed typo: 'freinds.html' -> 'friends.html'
        title=copy.title,
        subtitle=copy.subtitle, 
        user=user, 
        username=username,
        friends=friends,
        following=following,
        followers=followers,
        search_results=search_results, # Pass the new search results
        query=query,
        active_page='friends' 
    )