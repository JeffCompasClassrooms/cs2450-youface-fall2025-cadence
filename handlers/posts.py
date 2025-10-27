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
    db_posts.add_post(db, user, post_text)

    return flask.redirect(flask.url_for('login.index'))
