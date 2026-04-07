import os
import sys
import django
import random
from datetime import date, timedelta

# 1. Setup Django Environment
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'roomiehku.settings')
django.setup()

# 2. Import models
from core.models import User, Post, Comment, Like, SavedListing


def generate_test_data():
    print("--- Starting Full Data Generation ---")

    # 1. Create 5 Users
    users = []
    user_data = [
        ("alice", "Alice Wong", "91234567"),
        ("bob", "Bob Chen", "61234567"),
        ("charlie", "Charlie Li", "51234567"),
        ("david", "David Ho", "98765432"),
        ("eve", "Eve Zhang", "68765432"),
    ]

    for username, full_name, phone in user_data:
        user, created = User.objects.get_or_create(
            username=username,
            defaults={
                'email': f"{username}@example.com",
                'phone_number': phone,
                'bio': f"Hi, I'm {full_name}. Looking for a roommate near HKU!",
                'profile_photo': f"https://api.dicebear.com/7.x/avataaars/svg?seed={username}"
            }
        )
        if created:
            user.set_password("password123")
            user.save()
            print(f"Created User: {username}")
        users.append(user)

    # 2. Create 10 Posts
    locations = ["Kennedy Town", "Sai Ying Pun", "Pok Fu Lam", "Sheung Wan", "HKU Station"]
    titles = [
        "Cozy Room near HKU", "Quiet roommate wanted", "Spacious Flat",
        "Modern Studio", "Dormmate for St. John's", "Flatshare in SYP",
        "Master Room in K-Town", "Student Housing", "Near MTR Station", "Sea View Apartment"
    ]

    posts = []
    for i in range(10):
        post = Post.objects.create(
            author=random.choice(users),
            title=f"{random.choice(titles)} #{i + 1}",
            description="Fully furnished, high-speed Wi-Fi, 5 mins walk to HKU campus.",
            image_url=f"https://picsum.photos/seed/hku_post_{i}/800/600",
            listing_type=random.choice(['Apartment', 'Dorm', 'Roommate']),
            location=random.choice(locations),
            price=random.randint(5000, 15000),
            move_in_date=date.today() + timedelta(days=random.randint(7, 60)),
            gender_preference=random.choice(['M', 'F', 'N']),
            lifestyle_notes="Non-smoker, clean, no pets allowed."
        )
        posts.append(post)
        print(f"Created Post: {post.title}")

    # 3. Create Comments (approx 20 comments)
    comment_pool = [
        "Is this still available?", "Interested! Can I visit tomorrow?",
        "What is the walk time to HKU?", "Does it include utilities?", "PMed you!"
    ]
    for _ in range(20):
        Comment.objects.create(
            post=random.choice(posts),
            author=random.choice(users),
            content=random.choice(comment_pool)
        )
    print(f"Created 20 comments.")

    # 4. Create Likes (and sync likes_count)
    for post in posts:
        # Each post liked by 0-5 users
        likers = random.sample(users, k=random.randint(0, len(users)))
        for u in likers:
            Like.objects.get_or_create(user=u, post=post)

        # Update the denormalized likes_count field
        post.likes_count = post.likes.count()
        post.save()
    print("Created Likes and updated likes_count.")

    # 5. Create Saved Listings
    for user in users:
        # Each user saves 1-3 random posts
        saved_posts = random.sample(posts, k=random.randint(1, 3))
        for p in saved_posts:
            SavedListing.objects.get_or_create(user=user, post=p)
    print("Created Saved Listings for users.")

    print("--- Success: All test data generated! ---")


if __name__ == "__main__":
    generate_test_data()