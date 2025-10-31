import time
import tinydb

# Use the TinyDB Query object for filtering
Post = tinydb.Query()

def add_post(db, user, text):
    """Creates a new post in the 'posts' table."""
    posts_table = db.table('posts')
    # NOTE: Initialize 'likes' field here for new posts
    posts_table.insert({
        'user': user['username'], 
        'text': text, 
        'time': time.time(),
        'likes': 0  # <--- Added initialization
    })

# ... [get_posts and get_all_valid_posts remain the same] ...

# --- NEW FUNCTION FOR LIKE TOGGLING ---
def toggle_post_like(db, post_doc_id, user_username):
    """
    Toggles the like status for a post by a user.
    Uses a separate 'likes' table to track user-like relationships.
    Returns the new status ('liked' or 'unliked') and the new total count.
    """
    posts_table = db.table('posts')
    likes_table = db.table('likes')
    Like = tinydb.Query()
    
    # 1. Check if the user has already liked this post
    # Note: TinyDB document IDs are integers, ensure post_doc_id is int.
    try:
        post_doc_id = int(post_doc_id)
    except ValueError:
        return 'error', 0 

    like_entry = likes_table.get(
        (Like.user == user_username) & 
        (Like.post_id == post_doc_id)
    )

    # Fetch the post document using its ID
    post_doc = posts_table.get(doc_id=post_doc_id)
    if not post_doc:
        return 'error', 0 # Post not found

    # Ensure the post object has a 'likes' field, initialize if missing
    current_likes = post_doc.get('likes', 0)

    if like_entry:
        # 2. UNLIKE: Remove the record and decrement the count
        likes_table.remove(doc_ids=[like_entry.doc_id])
        new_count = current_likes - 1 if current_likes > 0 else 0
        new_status = 'unliked'
    else:
        # 3. LIKE: Add a record and increment the count
        likes_table.insert({
            'user': user_username, 
            'post_id': post_doc_id, 
            'time': time.time()
        })
        new_count = current_likes + 1
        new_status = 'liked'
    
    # 4. Update the 'posts' table with the new total count
    posts_table.update({'likes': new_count}, doc_ids=[post_doc_id])
    
    return new_status, new_count
