import tinydb

def new_user(db, username, password):
    """
    Creates a new user with the new friend request AND follow data structure.
    """
    users = db.table('users')
    User = tinydb.Query()
    if users.get(User.username == username):
        return None
    
    user_record = {
            'username': username,
            'password': password,
            'friends': [],
            'pending_requests_received': [], # Users who sent ME a request
            'pending_requests_sent': [],     # Users I have sent a request TO
            'following': [],                 # Users I am following
            'followers': []                  # Users who are following me
            }
    return users.insert(user_record)

def get_user(db, username, password):
    """Gets a user document by username and password."""
    users = db.table('users')
    User = tinydb.Query()
    return users.get((User.username == username) &
                     (User.password == password))

def get_user_by_name(db, username):
    """Gets a user document by only their username."""
    users = db.table('users')
    User = tinydb.Query()
    return users.get(User.username == username)

def delete_user(db, username, password):
    """Deletes a user."""
    users = db.table('users')
    User = tinydb.Query()
    return users.remove((User.username == username) &
                        (User.password == password))

# --- FRIEND REQUEST FUNCTIONS ---

def send_friend_request(db, sender_user, recipient_username):
    users = db.table('users')
    User = tinydb.Query()
    
    recipient_user = get_user_by_name(db, recipient_username)

    if not recipient_user:
        return f"User '{recipient_username}' not found.", 'danger'
    if recipient_username == sender_user['username']:
        return "You cannot send a friend request to yourself.", 'warning'
    
    # Safe-get all lists
    sender_friends = sender_user.get('friends', [])
    sender_sent = sender_user.get('pending_requests_sent', [])
    sender_received = sender_user.get('pending_requests_received', [])

    if recipient_username in sender_friends:
        return f"You are already friends with {recipient_username}.", 'info'
    if recipient_username in sender_sent:
        return f"You have already sent a request to {recipient_username}.", 'info'
    if recipient_username in sender_received:
        return f"{recipient_username} has already sent you a request. Please accept it.", 'info'

    # Add recipient to sender's "sent" list
    sender_user.setdefault('pending_requests_sent', []).append(recipient_username)
    # Add sender to recipient's "received" list
    recipient_user.setdefault('pending_requests_received', []).append(sender_user['username'])
    
    users.upsert(sender_user, User.username == sender_user['username'])
    users.upsert(recipient_user, User.username == recipient_user['username'])
    
    return f"Friend request sent to {recipient_username}.", 'success'

def accept_friend_request(db, user, requestor_username):
    users = db.table('users')
    User = tinydb.Query()
    
    requestor_user = get_user_by_name(db, requestor_username)
    
    if not requestor_user:
        return "Requestor user not found.", 'danger'
    
    # Safe-get lists
    user_received = user.get('pending_requests_received', [])
    
    if requestor_username not in user_received:
        return f"You do not have a pending request from {requestor_username}.", 'warning'

    # 1. Remove from user's "received" list
    user_received.remove(requestor_username)
    # 2. Add to user's "friends" list
    user.setdefault('friends', []).append(requestor_username)
    
    # 3. Remove from requestor's "sent" list
    requestor_sent = requestor_user.get('pending_requests_sent', [])
    if user['username'] in requestor_sent:
        requestor_sent.remove(user['username'])
    # 4. Add to requestor's "friends" list
    requestor_user.setdefault('friends', []).append(user['username'])
    
    users.upsert(user, User.username == user['username'])
    users.upsert(requestor_user, User.username == requestor_user['username'])
    
    return f"You are now friends with {requestor_username}!", 'success'

def reject_friend_request(db, user, requestor_username):
    users = db.table('users')
    User = tinydb.Query()
    
    requestor_user = get_user_by_name(db, requestor_username)

    if not requestor_user:
        return "Requestor user not found.", 'danger'
    
    user_received = user.get('pending_requests_received', [])
    
    if requestor_username not in user_received:
        return "No pending request to reject.", 'warning'

    # 1. Remove from user's "received" list
    user_received.remove(requestor_username)
    # 2. Remove from requestor's "sent" list
    requestor_sent = requestor_user.get('pending_requests_sent', [])
    if user['username'] in requestor_sent:
        requestor_sent.remove(user['username'])
    
    users.upsert(user, User.username == user['username'])
    users.upsert(requestor_user, User.username == requestor_user['username'])
    
    return f"Request from {requestor_username} rejected.", 'info'


def remove_user_friend(db, user, friend_username):
    users = db.table('users')
    User = tinydb.Query()
    
    friend_user = get_user_by_name(db, friend_username)
    user_friends = user.get('friends', [])

    if friend_username in user_friends:
        user_friends.remove(friend_username)
        users.upsert(user, User.username == user['username'])
    else:
        return f"You are not friends with {friend_username}.", 'warning'

    if friend_user:
        friend_friends = friend_user.get('friends', [])
        if user['username'] in friend_friends:
            friend_friends.remove(user['username'])
            users.upsert(friend_user, User.username == friend_user['username'])
            
    return f"Friend {friend_username} successfully unfriended!", 'success'

# --- NEW FOLLOW/UNFOLLOW FUNCTIONS ---

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
    # Use setdefault to create the list if it doesn't exist
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


# --- HELPER FUNCTIONS FOR FETCHING LISTS ---

def get_user_friends(db, user):
    """
    Gets the full user documents for all of a user's friends.
    """
    users = db.table('users')
    User = tinydb.Query()
    friends = []
    # Ensure friends list exists before iterating
    for friend_name in user.get('friends', []):
        friend_doc = users.get(User.username == friend_name)
        if friend_doc:
            friends.append(friend_doc)
    return friends

def get_pending_requests(db, user):
    """
    Gets the full user documents for all pending received requests.
    """
    users = db.table('users')
    User = tinydb.Query()
    requestors = []
    for requestor_name in user.get('pending_requests_received', []):
        requestor_doc = users.get(User.username == requestor_name)
        if requestor_doc:
            requestors.append(requestor_doc)
    return requestors

def get_potential_friends(db, user, query=None, limit=None):
    """
    Finds all users who are not the user, not friends, not pending, and not already followed.
    If a query is provided, filters by username.
    """
    users = db.table('users')
    all_users = users.all()
    
    current_username = user['username']
    
    # Create a set of all usernames to exclude
    exclude_list = set(user.get('friends', []))
    exclude_list.update(user.get('pending_requests_sent', []))
    exclude_list.update(user.get('pending_requests_received', []))
    exclude_list.update(user.get('following', [])) # <-- Now excludes people you follow
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