import flask
from db import helpers
import tinydb

blueprint = flask.Blueprint("leaderboard", __name__)

# --- THE CLOUT ALGORITHM ---
# Adjust these numbers to change how the leaderboard works!
POINTS_PER_FOLLOWER = 50
POINTS_PER_COMMENT_RECEIVED = 20
POINTS_PER_LIKE_RECEIVED = 10
POINTS_PER_POST_MADE = 5

@blueprint.route('/leaderboard')
def leaderboard_page():
    """Calculates scores and displays the leaderboard."""
    db = helpers.load_db()
    
    # Load all tables
    users_table = db.table('users')
    posts_table = db.table('posts')
    likes_table = db.table('likes')

    all_users = users_table.all()
    all_posts = posts_table.all()
    all_likes = likes_table.all()

    # 1. Initialize Score Dictionary
    # Format: {'username': {'username': 'name', 'points': 0, 'followers': 0}}
    leaderboard_data = {}
    
    for user in all_users:
        username = user['username']
        follower_count = len(user.get('followers', []))
        
        leaderboard_data[username] = {
            'username': username,
            'points': 0,
            'stats': {
                'followers': follower_count,
                'likes': 0,
                'comments': 0
            }
        }
        
        # Apply Points for Followers
        leaderboard_data[username]['points'] += (follower_count * POINTS_PER_FOLLOWER)

    # 2. Calculate Post Points & Map Post IDs to Owners
    # We need to know who owns which post_id to give them points for likes later
    post_owner_map = {} 

    for post in all_posts:
        owner = post.get('user')
        post_id = post.doc_id
        
        # Skip if user was deleted but post remains
        if owner not in leaderboard_data:
            continue

        post_owner_map[post_id] = owner

        # Points for making a post
        leaderboard_data[owner]['points'] += POINTS_PER_POST_MADE

        # Points for comments received on this post
        comments = post.get('comments', [])
        comment_count = len(comments)
        leaderboard_data[owner]['stats']['comments'] += comment_count
        leaderboard_data[owner]['points'] += (comment_count * POINTS_PER_COMMENT_RECEIVED)

    # 3. Calculate Like Points
    for like in all_likes:
        post_id = like.get('post_id')
        
        # Find who owns the post that was liked
        if post_id in post_owner_map:
            owner = post_owner_map[post_id]
            
            # Give points to the owner of the post (not the person who clicked like)
            leaderboard_data[owner]['stats']['likes'] += 1
            leaderboard_data[owner]['points'] += POINTS_PER_LIKE_RECEIVED

    # 4. Convert to List and Sort
    # Turn the dictionary values into a list: [UserA, UserB, UserC...]
    final_list = list(leaderboard_data.values())
    
    # Sort by points (Descending / Highest first)
    final_list.sort(key=lambda x: x['points'], reverse=True)

    # Get current user data for the header
    username = flask.request.cookies.get('username')

    # 5. Render Template
    # We pass the top 3 separately for the podium, and the rest for the list
    return flask.render_template(
        'leaderboard.html',
        username=username,
        top_users=final_list[:3],      # The Podium (Top 3)
        other_users=final_list[3:20],  # The List (Rank 4-20)
        all_users=final_list           # Backup full list
    )