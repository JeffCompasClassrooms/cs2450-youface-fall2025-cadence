import flask

# NOTE: We are importing the *database* functions from db.posts
from db import users, helpers, posts as db_posts 

blueprint = flask.Blueprint("posts", __name__)

@blueprint.route('/post', methods=['POST'])
def post():
    """Creates a new post."""
    db = helpers.load_db()

    username = flask.request.cookies.get('username')
    password = flask.request.cookies.get('password')

    user = users.get_user(db, username, password)
    if not user:
        flask.flash('You need to be logged in to do that.', 'danger')
        return flask.redirect(flask.url_for('login.loginscreen'))

    post_text = flask.request.form.get('post')
    
    # Use the add_post function from the database module (db.posts)
    # The updated add_post now stores the user's document ID from TinyDB
    db_posts.add_post(db, user, post_text)

    return flask.redirect(flask.url_for('login.index'))

@blueprint.route('/like/<int:post_id>', methods=['POST'])
def toggle_like(post_id):
    """Toggles the like status for a specific post."""
    db = helpers.load_db()
    
    username = flask.request.cookies.get('username')
    password = flask.request.cookies.get('password')

    user = users.get_user(db, username, password)
    
    # 1. Check for authentication
    if not user:
        flask.flash('You need to be logged in to like a post.', 'danger')
        return flask.redirect(flask.url_for('login.loginscreen'))

    user_id = user.doc_id
    
    # 2. Determine action (like or unlike)
    # The action is passed in the form data from the hidden input in feed.html
    action = flask.request.form.get('action') 

    if action == 'like':
        if db_posts.like_post(db, user_id, post_id):
            flask.flash('Post liked!', 'success')
        else:
            flask.flash('Post already liked.', 'info')
            
    elif action == 'unlike':
        if db_posts.unlike_post(db, user_id, post_id):
            flask.flash('Post unliked.', 'success')
        else:
            flask.flash('You have not liked this post.', 'info')
            
    # 3. Redirect back to the main feed
    return flask.redirect(flask.url_for('login.index'))

@blueprint.route('/comment/<int:post_id>', methods=['POST'])

def post_comment(post_id):
    """Handles AJAX submission for a new comment."""
    db = helpers.load_db()

    username = flask.request.cookies.get('username')
    password = flask.request.cookies.get('password')

    user = users.get_user(db, username, password)
    
    # --- Authentication Check ---
    if not user:
        # Return a 401 Unauthorized response for the AJAX call to handle
        return flask.jsonify({'error': 'Unauthorized: Please log in to comment.'}), 401
    
    comment_text = flask.request.form.get('comment_text')
    
    if not comment_text:
        return flask.jsonify({'error': 'Comment text is empty.'}), 400

    # --- Database Update ---
    new_comment_data = db_posts.add_comment(db, post_id, username, comment_text)

    # --- Response ---
    if new_comment_data:
        # Format the time for the JavaScript to display (using your convert_time filter logic)
        new_comment_data['time'] = timeago.format(new_comment_data['time'], time.time())
        
        # Return the new comment data as JSON with a 200 OK status
        return flask.jsonify(new_comment_data), 200
    else:
        # Post ID was not found
        return flask.jsonify({'error': f'Post with ID {post_id} not found.'}), 404
