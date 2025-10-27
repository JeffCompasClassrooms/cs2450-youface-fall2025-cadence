import time
import tinydb

# Use the TinyDB Query object for filtering
Post = tinydb.Query()

def add_post(db, user, text):
    """Creates a new post in the 'posts' table."""
    posts_table = db.table('posts')
    posts_table.insert({
        'user': user['username'], 
        'text': text, 
        'time': time.time()
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
    # TinyDB requires querying for a non-empty string as it doesn't have a built-in .strip()
    user_posts = posts_table.search(
        (Post.user == target_username) & 
        (Post.text != '') 
    )
    
    return user_posts

def get_all_valid_posts(db):
    """
    Retrieves all non-empty posts from the entire database using TinyDB.
    """
    posts_table = db.table('posts')
    
    # Search for all posts where the text is not an empty string
    all_valid_posts = posts_table.search(Post.text != '')
    
    return all_valid_posts
