import flask

# NOTE: We are importing the *database* functions from db.posts
# The db_posts module now contains toggle_post_like
from db import users, helpers, posts as db_posts 

blueprint = flask.Blueprint("posts", __name__)

# ... [Existing @blueprint.route('/post') remains the same] ...

# --- NEW ROUTE FOR LIKE TOGGLING ---
@blueprint.route('/like_post/<int:post_doc_id>', methods=['POST'])
def like_post(post_doc_id):
    """
    Handles the AJAX request to toggle a like on a post.
    The post_doc_id comes from the URL path.
    """
    db = helpers.load_db()

    # 1. Authentication Check (Crucial for security and identity)
    username = flask.request.cookies.get('username')
    password = flask.request.cookies.get('password')

    user = users.get_user(db, username, password)
    
    if not user:
        # 401: Unauthorized access
        return flask.jsonify({'status': 'error', 'message': 'Authentication required'}), 401

    # 2. Call the new database function to handle the logic
    status, new_count = db_posts.toggle_post_like(db, post_doc_id, user['username'])
    
    if status == 'error':
        # 404: Post ID likely invalid
        return flask.jsonify({'status': 'error', 'message': 'Post not found'}), 404

    # 3. Return a successful JSON response to the frontend
    return flask.jsonify({
        'status': status,
        'new_likes': new_count
    }), 200
