import tinydb

def new_user(db, username, password):
    """
    Creates a new user with the new friend request data structure.
    """
    users = db.table('users')
    User = tinydb.Query()
    if users.get(User.username == username):
        return None
    
    # Add the new lists for the request system
    user_record = {
            'username': username,
            'password': password,
            'friends': [],
            'pending_requests_received': [], # Users who sent ME a request
            'pending_requests_sent': []      # Users I have sent a request TO
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

# --- NEW FRIEND REQUEST FUNCTIONS ---

def send_friend_request(db, sender_user, recipient_username):
    """
    Adds a request from the sender to the recipient.
    """
    users = db.table('users')
    User = tinydb.Query()
    
    recipient_user = get_user_by_name(db, recipient_username)

    # --- Validation ---
    if not recipient_user:
        return f"User '{recipient_username}' not found.", 'danger'
    if recipient_username == sender_user['username']:
        return "You cannot send a friend request to yourself.", 'warning'
    if recipient_username in sender_user['friends']:
        return f"You are already friends with {recipient_username}.", 'info'
    if recipient_username in sender_user['pending_requests_sent']:
        return f"You have already sent a request to {recipient_username}.", 'info'
    if recipient_username in sender_user['pending_requests_received']:
        return f"{recipient_username} has already sent you a request. Please accept it.", 'info'

    # --- Action ---
    # Add recipient to sender's "sent" list
    sender_user['pending_requests_sent'].append(recipient_username)
    # Add sender to recipient's "received" list
    recipient_user['pending_requests_received'].append(sender_user['username'])
    
    # Update both users in the database
    users.upsert(sender_user, User.username == sender_user['username'])
    users.upsert(recipient_user, User.username == recipient_user['username'])
    
    return f"Friend request sent to {recipient_username}.", 'success'

def accept_friend_request(db, user, requestor_username):
    """
    Accepts a request, moving users to each other's friends list.
    """
    users = db.table('users')
    User = tinydb.Query()
    
    requestor_user = get_user_by_name(db, requestor_username)
    
    # --- Validation ---
    if not requestor_user:
        return "Requestor user not found.", 'danger'
    if requestor_username not in user['pending_requests_received']:
        return f"You do not have a pending request from {requestor_username}.", 'warning'

    # --- Action ---
    # 1. Remove from user's "received" list
    user['pending_requests_received'].remove(requestor_username)
    # 2. Add to user's "friends" list
    user['friends'].append(requestor_username)
    
    # 3. Remove from requestor's "sent" list
    requestor_user['pending_requests_sent'].remove(user['username'])
    # 4. Add to requestor's "friends" list
    requestor_user['friends'].append(user['username'])
    
    # Update both users in the database
    users.upsert(user, User.username == user['username'])
    users.upsert(requestor_user, User.username == requestor_user['username'])
    
    return f"You are now friends with {requestor_username}!", 'success'

def reject_friend_request(db, user, requestor_username):
    """
    Rejects a request, removing it from both users' lists.
    """
    users = db.table('users')
    User = tinydb.Query()
    
    requestor_user = get_user_by_name(db, requestor_username)

    # --- Validation ---
    if not requestor_user:
        return "Requestor user not found.", 'danger'
    if requestor_username not in user['pending_requests_received']:
        return "No pending request to reject.", 'warning'

    # --- Action ---
    # 1. Remove from user's "received" list
    user['pending_requests_received'].remove(requestor_username)
    # 2. Remove from requestor's "sent" list
    requestor_user['pending_requests_sent'].remove(user['username'])
    
    # Update both users in the database
    users.upsert(user, User.username == user['username'])
    users.upsert(requestor_user, User.username == requestor_user['username'])
    
    return f"Request from {requestor_username} rejected.", 'info'


def remove_user_friend(db, user, friend_username):
    """
    Removes a friend from both users' friends lists (bi-directional).
    """
    users = db.table('users')
    User = tinydb.Query()
    
    friend_user = get_user_by_name(db, friend_username)

    # --- Action for current user ---
    if friend_username in user['friends']:
        user['friends'].remove(friend_username)
        users.upsert(user, User.username == user['username'])
    else:
        return f"You are not friends with {friend_username}.", 'warning'

    # --- Action for the (former) friend ---
    if friend_user and user['username'] in friend_user['friends']:
        friend_user['friends'].remove(user['username'])
        users.upsert(friend_user, User.username == friend_user['username'])
        
    return f"Friend {friend_username} successfully unfriended!", 'success'


# --- NEW HELPER FUNCTIONS FOR FETCHING LISTS ---

def get_user_friends(db, user):
    """
    Gets the full user documents for all of a user's friends.
    (This function logic remains the same)
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
    Finds all users who are not the user, not friends, and not pending.
    If a query is provided, filters by username.
    """
    users = db.table('users')
    all_users = users.all()
    
    current_username = user['username']
    
    # Create a set of all usernames to exclude
    exclude_list = set(user.get('friends', []))
    exclude_list.update(user.get('pending_requests_sent', []))
    exclude_list.update(user.get('pending_requests_received', []))
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