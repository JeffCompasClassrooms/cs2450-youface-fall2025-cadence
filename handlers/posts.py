import time
import timeago
import flask
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
    db_posts.add_post(db, user, post_text)
    return flask.redirect(flask.url_for('login.index'))

@blueprint.route('/like/<int:post_id>', methods=['POST'])
def toggle_like(post_id):
    """Toggles like/unlike status for a post."""
    db = helpers.load_db()
    username = flask.request.cookies.get('username')
    password = flask.request.cookies.get('password')
    user = users.get_user(db, username, password)

    if not user:
        flask.flash('You need to be logged in to like a post.', 'danger')
        return flask.redirect(flask.url_for('login.loginscreen'))

    user_id = user.doc_id
    action = flask.request.form.get('action')

    if action == 'like':
        if db_posts.like_post(db, user_id, post_id):
            flask.flash('Post liked!', 'success')
        else:
            flask.flash('Post already liked.', 'info')
    elif action == 'unlike':
        if db_posts.unlike_post(db, user_id, post_id):
            flask.flash('Post unliked!', 'success')
        else:
            flask.flash('You have not liked this post.', 'info')

    return flask.redirect(flask.url_for('login.index'))

@blueprint.route('/comment/<int:post_id>', methods=['POST'])
def post_comment(post_id):
    """Handles AJAX comment submission."""
    db = helpers.load_db()
    username = flask.request.cookies.get('username')
    password = flask.request.cookies.get('password')
    user = users.get_user(db, username, password)

    # --- Authentication check ---
    if not user:
        return flask.jsonify({'error': 'Unauthorized: Please log in to comment.'}), 401

    comment_text = flask.request.form.get('comment_text')
    if not comment_text:
        return flask.jsonify({'error': 'Comment text is empty.'}), 400

    # --- Add comment ---
    new_comment_data = db_posts.add_comment(db, post_id, username, comment_text)

    # --- Response ---
    if new_comment_data:
        formatted_comment = {
            'user': new_comment_data['user'],
            'text': new_comment_data['text'],
            'time': timeago.format(new_comment_data['time'], time.time())
        }
        return flask.jsonify(formatted_comment), 200
    else:
        return flask.jsonify({'error': f'Post with ID {post_id} not found.'}), 404
