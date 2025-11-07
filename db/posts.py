import time
import tinydb

# Use the TinyDB Query object for filtering
Post = tinydb.Query()
Like = tinydb.Query()

def add_post(db, user, text):
    """Creates a new post in the 'posts' table."""
    posts_table = db.table('posts')
    posts_table.insert({
        'user': user['username'], 
        'text': text, 
        'time': time.time(),
        'user_id': user.doc_id  # store user doc_id for easy lookup
    })

def get_posts(db, user):
    """Retrieves all non-empty posts for a specific user."""
    posts_table = db.table('posts')
    target_username = user.get('username')

    if not target_username:
        return []
    
    user_posts = posts_table.search(
        (Post.user == target_username) & 
        (Post.text != '')
    )
    
    return user_posts

def get_all_valid_posts(db, current_user_id=None):
    """Retrieves all valid (non-empty) posts and adds like info."""
    posts_table = db.table('posts')
    likes_table = db.table('likes')

    all_valid_posts = posts_table.search(Post.text != '')

    for post in all_valid_posts:
        post_id = post.doc_id

        # Total likes for this post
        post['like_count'] = len(likes_table.search(Like.post_id == post_id))

        # Check if current user liked this post
        post['liked_by_user'] = False
        if current_user_id is not None:
            like_record = likes_table.get(
                (Like.user_id == current_user_id) & (Like.post_id == post_id)
            )
            if like_record:
                post['liked_by_user'] = True

    # Sort newest first
    all_valid_posts.sort(key=lambda p: p['time'], reverse=True)
    return all_valid_posts

def like_post(db, user_id, post_id):
    """Adds a like from a user to a post."""
    likes_table = db.table('likes')
    existing_like = likes_table.get(
        (Like.user_id == user_id) & (Like.post_id == post_id)
    )
    if not existing_like:
        likes_table.insert({
            'user_id': user_id,
            'post_id': post_id,
            'time': time.time()
        })
        return True
    return False

def unlike_post(db, user_id, post_id):
    """Removes a like."""
    likes_table = db.table('likes')
    delete_count = likes_table.remove(
        (Like.user_id == user_id) & (Like.post_id == post_id)
    )
    return delete_count > 0

def add_comment(db, post_id, username, text):
    """
    Adds a comment to a specific post by its TinyDB doc_id.
    """
    posts_table = db.table('posts')
    post_record = posts_table.get(doc_id=post_id)

    if post_record:
        new_comment = {
            'user': username,
            'text': text,
            'time': time.time()
        }

        if 'comments' not in post_record:
            post_record['comments'] = []

        post_record['comments'].append(new_comment)
        posts_table.update(post_record, doc_ids=[post_id])

        return new_comment
    
    return None
