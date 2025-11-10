import tinydb
# Define the Query object once at the top, globally
User = tinydb.Query()

# --- All other code follows ---

def new_user(db, username, password):
    """
    Creates a new user with the new *follow-only* data structure.
    """
    users = db.table('users')
    if users.get(User.username == username):
        return None
    
    user_record = {
        'username': username,
        'password': password,
        'following': [],  # Users I am following
        'followers': []   # Users who are following me
    }
    return users.insert(user_record)

def get_user(db, username, password):
    """Gets a user document by username and password."""
    users = db.table('users')
    return users.get((User.username == username) &
                     (User.password == password))

def get_user_by_name(db, username):
    """Gets a user document by only their username."""
    users = db.table('users')
    # REMOVE: User = tinydb.Query()
    return users.get(User.username == username)

def delete_user(db, username, password):
    """Deletes a user."""
    users = db.table('users')
    # REMOVE: User = tinydb.Query()
    return users.remove((User.username == username) &
                        (User.password == password))

# --- GONE: All send_request, accept_request, reject_request, remove_user_friend functions ---


# --- FOLLOW/UNFOLLOW FUNCTIONS (These are now the primary actions) ---

def follow_user(db, follower_user, user_to_follow_name):
    """
    Adds a one-way follow relationship.
    """
    users = db.table('users')
    User = tinydb.Query()
    
    user_to_follow = get_user_by_name(db, user_to_follow_name)
    
    # --- Validation ---
    if not user_to_follow:
        return f"User '{user_to_follow_name}' not found.", 'danger'
    if user_to_follow_name == follower_user['username']:
        return "You cannot follow yourself.", 'warning'
    
    follower_following = follower_user.get('following', [])
    
    if user_to_follow_name in follower_following:
        return f"You are already following {user_to_follow_name}.", 'info'

    # --- Action ---
    # 1. Add to follower's "following" list
    follower_following.append(user_to_follow_name)
    
    # 2. Add to followed user's "followers" list
    user_to_follow.setdefault('followers', []).append(follower_user['username'])
    
    # Update both users in the database
    users.upsert(follower_user, User.username == follower_user['username'])
    users.upsert(user_to_follow, User.username == user_to_follow['username'])
    
    return f"You are now following {user_to_follow_name}.", 'success'

def unfollow_user(db, follower_user, user_to_unfollow_name):
    """
    Removes a one-way follow relationship.
    """
    users = db.table('users')
    User = tinydb.Query()
    
    user_to_unfollow = get_user_by_name(db, user_to_unfollow_name)
    follower_following = follower_user.get('following', [])

    # --- Validation ---
    if user_to_unfollow_name not in follower_following:
        return "You are not following this user.", 'warning'

    # --- Action ---
    # 1. Remove from follower's "following" list
    follower_following.remove(user_to_unfollow_name)
    
    # 2. Remove from unfollowed user's "followers" list
    if user_to_unfollow:
        user_followers = user_to_unfollow.get('followers', [])
        if follower_user['username'] in user_followers:
            user_followers.remove(follower_user['username'])
            
    # Update both users
    users.upsert(follower_user, User.username == follower_user['username'])
    if user_to_unfollow:
        users.upsert(user_to_unfollow, User.username == user_to_unfollow['username'])
        
    return f"You are no longer following {user_to_unfollow_name}.", 'success'


# --- NEW HELPER FUNCTIONS FOR FETCHING LISTS ---

def get_user_friends(db, user):
    """
    Gets user docs for MUTUAL follows (A follows B and B follows A).
    This is the new definition of "Friends".
    """
    users = db.table('users')
    User = tinydb.Query()
    
    # Use sets for efficient intersection
    following = set(user.get('following', []))
    followers = set(user.get('followers', []))
    
    mutual_friend_names = following.intersection(followers)
    
    friends = []
    for friend_name in mutual_friend_names:
        friend_doc = users.get(User.username == friend_name)
        if friend_doc:
            friends.append(friend_doc)
    return friends

def get_user_following(db, user):
    """
    Gets user docs for people the user follows, but who DO NOT follow back.
    """
    users = db.table('users')
    User = tinydb.Query()
    
    following = set(user.get('following', []))
    followers = set(user.get('followers', []))
    
    # People I follow minus people who follow me
    following_only_names = following - followers
    
    following_list = []
    for user_name in following_only_names:
        user_doc = users.get(User.username == user_name)
        if user_doc:
            following_list.append(user_doc)
    return following_list

def get_user_followers(db, user):
    """
    Gets user docs for people who follow the user, but who the user DOES NOT follow back.
    """
    users = db.table('users')
    User = tinydb.Query()
    
    following = set(user.get('following', []))
    followers = set(user.get('followers', []))
    
    # People who follow me minus people I follow
    followers_only_names = followers - following
    
    followers_list = []
    for user_name in followers_only_names:
        user_doc = users.get(User.username == user_name)
        if user_doc:
            followers_list.append(user_doc)
    return followers_list


def get_potential_friends(db, user, query=None, limit=None):
    """
    Finds all users who the current user is NOT already following.
    (This suggests people to follow).
    """
    users = db.table('users')
    all_users = users.all()
    
    current_username = user['username']
    
    # Create a set of all usernames to exclude
    # We only exclude people we are ALREADY following, and ourselves.
    exclude_list = set(user.get('following', []))
    exclude_list.add(current_username)
    
    potential_friends = []
    for potential_user in all_users:
        potential_username = potential_user['username']
        
        # Skip if user is in the exclude list
        if potential_username in exclude_list:
            continue
            
        # If there's a search query, check if it matches
        if query:
            if query.lower() not in potential_username.lower():
                continue # Query doesn't match, skip
        
        # If we get here, the user is a valid potential friend
        potential_friends.append(potential_user)
        
        # If a limit is set and we've reached it, stop
        if limit and len(potential_friends) >= limit:
            break
            
    return potential_friends