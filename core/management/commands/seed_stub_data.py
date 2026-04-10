from datetime import date
from decimal import Decimal

from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.core.management.base import BaseCommand
from django.db.models import Count

from core.models import Comment, Like, Post, SavedListing, User


DEMO_IMAGE_BYTES = (
    b"GIF89a\x01\x00\x01\x00\x80\x00\x00\x00\x00\x00"
    b"\xff\xff\xff!\xf9\x04\x00\x00\x00\x00\x00,\x00\x00"
    b"\x00\x00\x01\x00\x01\x00\x00\x02\x02D\x01\x00;"
)


class Command(BaseCommand):
    help = "Seed demo stub data for local RoomieHKU MVP preview (idempotent)."

    def handle(self, *args, **options):
        users = self._seed_users()
        posts = self._seed_posts(users)
        self._seed_comments(users, posts)
        self._seed_likes(users, posts)
        self._seed_saved_listings(users, posts)
        self._sync_likes_count()

        self.stdout.write(self.style.SUCCESS("Stub data ready."))
        self.stdout.write(
            f"Users={User.objects.count()} Posts={Post.objects.count()} "
            f"Comments={Comment.objects.count()} Likes={Like.objects.count()} "
            f"Saves={SavedListing.objects.count()}"
        )

    def _seed_users(self):
        users_data = [
            {
                "username": "alice_hku",
                "password": "password123",
                "email": "alice@hku.hk",
                "first_name": "Alice",
                "last_name": "Chan",
                "bio": "Year 3 student looking for a quiet shared apartment near HKU.",
                "phone_number": "+85291234567",
                "profile_photo_name": "alice_hku.gif",
                "is_staff": False,
                "is_superuser": False,
            },
            {
                "username": "brian_hku",
                "password": "password123",
                "email": "brian@hku.hk",
                "first_name": "Brian",
                "last_name": "Wong",
                "bio": "Exchange student preferring furnished studio options.",
                "phone_number": "+85292345678",
                "profile_photo_name": "brian_hku.gif",
                "is_staff": False,
                "is_superuser": False,
            },
            {
                "username": "cynthia_hku",
                "password": "password123",
                "email": "cynthia@hku.hk",
                "first_name": "Cynthia",
                "last_name": "Lee",
                "bio": "Looking for female roommate for next semester.",
                "phone_number": "+85293456789",
                "profile_photo_name": "cynthia_hku.gif",
                "is_staff": False,
                "is_superuser": False,
            },
            {
                "username": "staff_demo",
                "password": "password123",
                "email": "staff@roomiehku.local",
                "first_name": "Staff",
                "last_name": "Demo",
                "bio": "Demo staff moderator account.",
                "phone_number": "",
                "profile_photo_name": "staff_demo.gif",
                "is_staff": True,
                "is_superuser": True,
            },
        ]

        users = {}
        for row in users_data:
            username = row["username"]
            defaults = {
                "email": row["email"],
                "first_name": row["first_name"],
                "last_name": row["last_name"],
                "bio": row["bio"],
                "phone_number": row["phone_number"],
                "is_staff": row["is_staff"],
                "is_superuser": row["is_superuser"],
            }
            user, created = User.objects.get_or_create(username=username, defaults=defaults)

            changed = created
            if not created:
                for field, value in defaults.items():
                    if getattr(user, field) != value:
                        setattr(user, field, value)
                        changed = True

            if self._ensure_uploaded_image(
                field_file=user.profile_photo,
                relative_name=row["profile_photo_name"],
            ):
                changed = True

            if not user.check_password(row["password"]):
                user.set_password(row["password"])
                changed = True

            if changed:
                user.save()

            users[username] = user
        return users

    def _seed_posts(self, users):
        posts_data = [
            {
                "author": "alice_hku",
                "title": "2BR Flat in Kennedy Town (10 mins to HKU)",
                "description": (
                    "Bright two-bedroom flat with shared kitchen and washer. "
                    "Looking for one tidy roommate."
                ),
                "image_name": "listing-kennedy-town.gif",
                "listing_type": "Apartment",
                "location": "Kennedy Town",
                "price": Decimal("9500.00"),
                "move_in_date": date(2026, 5, 1),
                "gender_preference": "N",
                "lifestyle_notes": "No smoking, quiet after 11pm.",
            },
            {
                "author": "brian_hku",
                "title": "Dorm Spot Available at Pok Fu Lam",
                "description": (
                    "Subletting a dorm bed space for summer. Great for short-term stay."
                ),
                "image_name": "listing-pok-fulam-dorm.gif",
                "listing_type": "Dorm",
                "location": "Pok Fu Lam",
                "price": Decimal("4800.00"),
                "move_in_date": date(2026, 6, 1),
                "gender_preference": "N",
                "lifestyle_notes": "Best for early risers.",
            },
            {
                "author": "cynthia_hku",
                "title": "Female Roommate Needed in Sai Ying Pun",
                "description": "Looking for a female roommate for a modern shared flat.",
                "image_name": "listing-sai-ying-pun-roommate.gif",
                "listing_type": "Roommate",
                "location": "Sai Ying Pun",
                "price": Decimal("7200.00"),
                "move_in_date": date(2026, 8, 15),
                "gender_preference": "F",
                "lifestyle_notes": "Clean and considerate shared living.",
            },
            {
                "author": "alice_hku",
                "title": "Studio Near HKU MTR Exit B1",
                "description": "Compact furnished studio, utilities included.",
                "image_name": "listing-hku-studio.gif",
                "listing_type": "Apartment",
                "location": "Shek Tong Tsui",
                "price": Decimal("11000.00"),
                "move_in_date": date(2026, 7, 1),
                "gender_preference": "N",
                "lifestyle_notes": "Ideal for one person, no pets.",
            },
            {
                "author": "brian_hku",
                "title": "Roommate Search for 3BR in Mid-Levels",
                "description": "Two HKU postgrads seeking one more roommate.",
                "image_name": "listing-mid-levels-roommate.gif",
                "listing_type": "Roommate",
                "location": "Mid-Levels",
                "price": Decimal("8700.00"),
                "move_in_date": date(2026, 9, 1),
                "gender_preference": "N",
                "lifestyle_notes": "Shared cooking, study-friendly environment.",
            },
        ]

        posts = {}
        for row in posts_data:
            author = users[row["author"]]
            defaults = {
                "description": row["description"],
                "listing_type": row["listing_type"],
                "location": row["location"],
                "price": row["price"],
                "move_in_date": row["move_in_date"],
                "gender_preference": row["gender_preference"],
                "lifestyle_notes": row["lifestyle_notes"],
            }
            post, created = Post.objects.get_or_create(
                author=author,
                title=row["title"],
                defaults=defaults,
            )

            changed = created
            if not created:
                for field, value in defaults.items():
                    if getattr(post, field) != value:
                        setattr(post, field, value)
                        changed = True

            if self._ensure_uploaded_image(
                field_file=post.image_url,
                relative_name=row["image_name"],
            ):
                changed = True

            if changed:
                post.save()
            posts[row["title"]] = post
        return posts

    def _seed_comments(self, users, posts):
        comments_data = [
            ("brian_hku", "2BR Flat in Kennedy Town (10 mins to HKU)", "Is this still available for June move-in?"),
            ("cynthia_hku", "2BR Flat in Kennedy Town (10 mins to HKU)", "Can I schedule a viewing this weekend?"),
            ("alice_hku", "Female Roommate Needed in Sai Ying Pun", "This area is super convenient for HKU."),
            ("alice_hku", "Roommate Search for 3BR in Mid-Levels", "What is the nearest bus stop?"),
        ]
        for username, post_title, content in comments_data:
            Comment.objects.get_or_create(
                author=users[username],
                post=posts[post_title],
                content=content,
            )

    def _seed_likes(self, users, posts):
        likes_data = [
            ("brian_hku", "2BR Flat in Kennedy Town (10 mins to HKU)"),
            ("cynthia_hku", "2BR Flat in Kennedy Town (10 mins to HKU)"),
            ("alice_hku", "Female Roommate Needed in Sai Ying Pun"),
            ("staff_demo", "Roommate Search for 3BR in Mid-Levels"),
        ]
        for username, post_title in likes_data:
            Like.objects.get_or_create(
                user=users[username],
                post=posts[post_title],
            )

    def _seed_saved_listings(self, users, posts):
        saved_data = [
            ("alice_hku", "Dorm Spot Available at Pok Fu Lam"),
            ("brian_hku", "Studio Near HKU MTR Exit B1"),
            ("cynthia_hku", "2BR Flat in Kennedy Town (10 mins to HKU)"),
            ("staff_demo", "Female Roommate Needed in Sai Ying Pun"),
        ]
        for username, post_title in saved_data:
            SavedListing.objects.get_or_create(
                user=users[username],
                post=posts[post_title],
            )

    def _sync_likes_count(self):
        for post in Post.objects.annotate(total_likes=Count("likes")):
            if post.likes_count != post.total_likes:
                Post.objects.filter(pk=post.pk).update(likes_count=post.total_likes)

    def _ensure_uploaded_image(self, field_file, relative_name):
        upload_to = field_file.field.upload_to
        upload_prefix = upload_to if upload_to.endswith("/") else f"{upload_to}/"
        storage_name = f"{upload_prefix}{relative_name}"

        if not default_storage.exists(storage_name):
            default_storage.save(storage_name, ContentFile(DEMO_IMAGE_BYTES))

        if field_file.name != storage_name:
            field_file.name = storage_name
            return True
        return False
