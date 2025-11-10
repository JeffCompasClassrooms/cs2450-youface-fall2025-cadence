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
    """Toggles a like for a specific post."""
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
        db_posts.like_post(db, user_id, post_id)
    elif action == 'unlike':
        db_posts.unlike_post(db, user_id, post_id)

    return flask.redirect(flask.url_for('login.index'))

@blueprint.route('/comment/<int:post_id>', methods=['POST'])
def post_comment(post_id):
    """Handles AJAX submission for a new comment."""
    db = helpers.load_db()
    username = flask.request.cookies.get('username')
    password = flask.request.cookies.get('password')
    user = users.get_user(db, username, password)

    if not user:
        return flask.jsonify({'error': 'Unauthorized: Please log in to comment.'}), 401

    comment_text = flask.request.form.get('comment_text')
    if not comment_text:
        return flask.jsonify({'error': 'Comment text is empty.'}), 400

    # Add the comment to the database
    new_comment_data = db_posts.add_comment(db, post_id, username, comment_text)

    if new_comment_data:
        new_comment_data['time'] = timeago.format(new_comment_data['time'], time.time())
        return flask.jsonify(new_comment_data), 200
    else:
        return flask.jsonify({'error': f'Post with ID {post_id} not found.'}), 404
