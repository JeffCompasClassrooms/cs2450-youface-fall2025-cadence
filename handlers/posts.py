# posts2.py (Updated with Like/Unlike Route and doc_id storage)
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
