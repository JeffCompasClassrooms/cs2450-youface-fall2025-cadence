import time
import tinydb

Post = tinydb.Query()
Like = tinydb.Query()

def add_post(db, user, text):
    """Creates a new post in the 'posts' table."""
    posts_table = db.table('posts')
    posts_table.insert({
        'user': user['username'], 
        'text': text, 
        'time': time.time(),
        'user_id': user.doc_id
    })

def get_posts(db, user):
    """Retrieves all non-empty posts created by a specific user."""
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
    """Retrieves all non-empty posts with like data."""
    posts_table = db.table('posts')
    likes_table = db.table('likes')
    
    all_valid_posts = posts_table.search(Post.text != '')
    
    for post in all_valid_posts:
        post_id = post.doc_id
        post['like_count'] = len(likes_table.search(Like.post_id == post_id))
        post['liked_by_user'] = False
        if current_user_id is not None:
            like_record = likes_table.get(
                (Like.user_id == current_user_id) & (Like.post_id == post_id)
            )
            if like_record:
                post['liked_by_user'] = True
                
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
    """Removes a like from a user to a post."""
    likes_table = db.table('likes')
    delete_count = likes_table.remove(
        (Like.user_id == user_id) & (Like.post_id == post_id)
    )
    return delete_count > 0

def add_comment(db, post_id, username, text):
    """
    Safely adds a comment to a specific post by its doc_id.
    """
    posts_table = db.table('posts')
    post_record = posts_table.get(doc_id=post_id)

    if not post_record:
        return None

    # Prepare new comment
    new_comment = {
        'user': username,
        'text': text,
        'time': time.time()
    }

    # Get existing comments or start new list
    comments = post_record.get('comments', [])
    comments.append(new_comment)

    # Only update comments field (not entire post)
    posts_table.update({'comments': comments}, doc_ids=[post_id])

    return new_comment
