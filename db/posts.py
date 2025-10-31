import time
import tinydb

# Use the TinyDB Query object for filtering
Post = tinydb.Query()
Like = tinydb.Query() # NEW: Query object for the likes table

def add_post(db, user, text):
    """Creates a new post in the 'posts' table."""
    posts_table = db.table('posts')
    posts_table.insert({
        'user': user['username'], 
        'text': text, 
        'time': time.time(),
        'likes': 0  # Initialize likes counter for new posts
    })

def get_posts(db, user):
    """
    Retrieves all non-empty posts created by a specific user using TinyDB.
    """
    posts_table = db.table('posts')
    target_username = user.get('username')
    
    if not target_username:
        return []
        
    # Search for posts belonging to the user AND where the text is not an empty string
    user_posts = posts_table.search(
        (Post.user == target_username) & 
        (Post.text != '') 
    )
    
    return user_posts

# --- FIX FOR AttributeError: get_all_valid_posts ---
def get_all_valid_posts(db):
    """
    Retrieves all non-empty posts from the entire database using TinyDB.
    """
    posts_table = db.table('posts')
    
    # Search for all posts where the text is not an empty string
    all_valid_posts = posts_table.search(Post.text != '')
    
    return all_valid_posts
# --------------------------------------------------

# --- NEW FUNCTION TO SUPPORT THE LIKE BUTTON ---
def toggle_post_like(db, post_doc_id, user_username):
    """
    Toggles the like status for a post by a user and updates the post count.
    """
    posts_table = db.table('posts')
    likes_table = db.table('likes') # New table to track relationships
    
    # 1. Type check and error handling for post_doc_id
    try:
        post_doc_id = int(post_doc_id)
    except ValueError:
        return 'error', 0 

    # 2. Check if the user has already liked this post
    like_entry = likes_table.get(
        (Like.user == user_username) & 
        (Like.post_id == post_doc_id)
    )

    post_doc = posts_table.get(doc_id=post_doc_id)
    if not post_doc:
        return 'error', 0 

    current_likes = post_doc.get('likes', 0)

    if like_entry:
        # 3. UNLIKE: Remove record and decrement count
        likes_table.remove(doc_ids=[like_entry.doc_id])
        new_count = current_likes - 1 if current_likes > 0 else 0
        new_status = 'unliked'
    else:
        # 4. LIKE: Add record and increment count
        likes_table.insert({
            'user': user_username, 
            'post_id': post_doc_id, 
            'time': time.time()
        })
        new_count = current_likes + 1
        new_status = 'liked'
    
    # 5. Update the 'posts' table with the new total count
    posts_table.update({'likes': new_count}, doc_ids=[post_doc_id])
    
    return new_status, new_count
