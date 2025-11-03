import time
import tinydb

# Use the TinyDB Query object for filtering
Post = tinydb.Query()
# Define a Query object for the 'likes' table
Like = tinydb.Query()

def add_post(db, user, text):
    """Creates a new post in the 'posts' table."""
    posts_table = db.table('posts')
    # Store the user's ID (the user dictionary contains an 'id' which is the TinyDB doc_id)
    posts_table.insert({
        'user': user['username'], 
        'text': text, 
        'time': time.time(),
        'user_id': user.doc_id # Store the user's document ID for easier lookups
    })

def get_posts(db, user):
    """
    Retrieves all non-empty posts created by a specific user using TinyDB.
    
    Args:
        db (tinydb.TinyDB): The loaded database instance.
        user (dict): The dictionary object for the user.

    Returns:
        list: A list of post dictionaries.
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

def get_all_valid_posts(db, current_user_id=None):
    """
    Retrieves all non-empty posts from the entire database using TinyDB.
    
    Args:
        db (tinydb.TinyDB): The loaded database instance.
        current_user_id (int, optional): The user ID of the currently logged-in user.
                                         Used to check if the user has liked a post.
    """
    posts_table = db.table('posts')
    likes_table = db.table('likes')
    
    # Search for all posts where the text is not an empty string
    all_valid_posts = posts_table.search(Post.text != '')
    
    # Enrich posts with like data
    for post in all_valid_posts:
        post_id = post.doc_id
        
        # 1. Get the total like count for the post
        post['like_count'] = len(likes_table.search(Like.post_id == post_id))
        
        # 2. Check if the current user has liked this post
        post['liked_by_user'] = False
        if current_user_id is not None:
            like_record = likes_table.get(
                (Like.user_id == current_user_id) & (Like.post_id == post_id)
            )
            if like_record:
                post['liked_by_user'] = True
                
    # Sort the posts by time, newest first
    all_valid_posts.sort(key=lambda p: p['time'], reverse=True)

    return all_valid_posts

def like_post(db, user_id, post_id):
    """Adds a like from a user to a post."""
    likes_table = db.table('likes')
    
    # Check if the user has already liked this post
    existing_like = likes_table.get(
        (Like.user_id == user_id) & (Like.post_id == post_id)
    )
    
    if not existing_like:
        likes_table.insert({
            'user_id': user_id,
            'post_id': post_id,
            'time': time.time()
        })
        return True # Like added
    return False # Already liked

def unlike_post(db, user_id, post_id):
    """Removes a like from a user to a post."""
    likes_table = db.table('likes')
    
    # Remove the like record
    delete_count = likes_table.remove(
        (Like.user_id == user_id) & (Like.post_id == post_id)
    )
    
    return delete_count > 0 # Returns True if a like was removed

def add_comment(db, post_id, username, text):
    """
    Adds a comment to a specific post by its doc_id.
    """
    posts_table = db.table('posts')
    # 1. Find the post by its TinyDB document ID (post_id)
    post_record = posts_table.get(doc_id=post_id)

    if post_record:
        # 2. Prepare the new comment data
        new_comment = {
            'user': username,
            'text': text,
            'time': time.time()
        }
        
        # Initialize the 'comments' key if it doesn't exist
        if 'comments' not in post_record:
            post_record['comments'] = []
            
        # 3. Add the new comment to the list
        post_record['comments'].append(new_comment)
        
        # 4. Update the record in the database
        posts_table.update(post_record, doc_ids=[post_id])
        
        # Return the new comment data for the AJAX response
        return new_comment
    
    return None # Return None if the post ID was not found
