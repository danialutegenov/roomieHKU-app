from datetime import date
from decimal import Decimal
from html import unescape
from pathlib import Path
import re
import tempfile
from urllib.parse import urlencode, urljoin
from urllib.request import Request, urlopen
import zipfile

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

KAGGLE_HOUSE_ROOMS_ZIP_URL = (
    "https://www.kaggle.com/api/v1/datasets/download/barelydedicated/airbnb-duplicate-image-detection"
)
KAGGLE_HOUSE_ROOMS_ZIP_CACHE = (
    Path(tempfile.gettempdir()) / "roomiehku-airbnb-room-images-v1.zip"
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
                "username": "noah_chan",
                "password": "password123",
                "email": "noah.chan@hku.hk",
                "first_name": "Noah",
                "last_name": "Chan",
                "bio": "Year 4 Computer Science student looking for a clean shared flat near HKU MTR.",
                "phone_number": "+85291234567",
                "profile_photo_name": "ffhq-noah-chan.png",
                "profile_photo_url": "https://drive.google.com/uc?id=1FvLyVJJiJvYSIvyjy_TOCE6iR5Maofd1",
                "is_staff": False,
                "is_superuser": False,
            },
            {
                "username": "daniel_wong",
                "password": "password123",
                "email": "daniel.wong@hku.hk",
                "first_name": "Daniel",
                "last_name": "Wong",
                "bio": "MFin student who prefers furnished studio listings within 20 minutes of campus.",
                "phone_number": "+85292345678",
                "profile_photo_name": "ffhq-daniel-wong.png",
                "profile_photo_url": "https://drive.google.com/uc?id=1-P0LEIijkcPDvPokqnbUEDAvLsCcO4vH",
                "is_staff": False,
                "is_superuser": False,
            },
            {
                "username": "marcus_leung",
                "password": "password123",
                "email": "marcus.leung@hku.hk",
                "first_name": "Marcus",
                "last_name": "Leung",
                "bio": "Economics undergrad searching for a long-term roommate setup around Sai Ying Pun.",
                "phone_number": "+85293456789",
                "profile_photo_name": "ffhq-marcus-leung.png",
                "profile_photo_url": "https://drive.google.com/uc?id=17qgFSi6ZcX2CH0LQpDbTQbl-DD8LyciB",
                "is_staff": False,
                "is_superuser": False,
            },
            {
                "username": "isaac_lau",
                "password": "password123",
                "email": "isaac.lau@hku.hk",
                "first_name": "Isaac",
                "last_name": "Lau",
                "bio": "Law student who values quiet study hours and reliable flatmates.",
                "phone_number": "+85294567890",
                "profile_photo_name": "ffhq-isaac-lau.png",
                "profile_photo_url": "https://drive.google.com/uc?id=1TCQFy4eOBVVBurwhkMF8GSqWXRvCuDiP",
                "is_staff": False,
                "is_superuser": False,
            },
            {
                "username": "maya_shah",
                "password": "password123",
                "email": "maya.shah@hku.hk",
                "first_name": "Maya",
                "last_name": "Shah",
                "bio": "Public Health student looking for a roommate who keeps shared spaces organized.",
                "phone_number": "+85295678901",
                "profile_photo_name": "ffhq-maya-shah.png",
                "profile_photo_url": "https://drive.google.com/uc?id=1wMH8tyiFK7dDDcnDuHj7N9EGzOwbcbpi",
                "is_staff": False,
                "is_superuser": False,
            },
            {
                "username": "natalie_cheng",
                "password": "password123",
                "email": "natalie.cheng@hku.hk",
                "first_name": "Natalie",
                "last_name": "Cheng",
                "bio": "Architecture student seeking a bright apartment close to bus routes and groceries.",
                "phone_number": "+85296789012",
                "profile_photo_name": "ffhq-natalie-cheng.png",
                "profile_photo_url": "https://drive.google.com/uc?id=1Mvbb3LybCvjTBr3oqhjCsXflYVGeAqvV",
                "is_staff": False,
                "is_superuser": False,
            },
            {
                "username": "emily_kwok",
                "password": "password123",
                "email": "emily.kwok@hku.hk",
                "first_name": "Emily",
                "last_name": "Kwok",
                "bio": "Nursing student open to shared flats with late-night transport convenience.",
                "phone_number": "+85297890123",
                "profile_photo_name": "ffhq-emily-kwok.png",
                "profile_photo_url": "https://drive.google.com/uc?id=1el1DG4GPc5Jqenor1DvEWcD5l8XIVZp-",
                "is_staff": False,
                "is_superuser": False,
            },
            {
                "username": "sophie_ho",
                "password": "password123",
                "email": "sophie.ho@hku.hk",
                "first_name": "Sophie",
                "last_name": "Ho",
                "bio": "MBA candidate preferring well-managed apartments with good internet and desk space.",
                "phone_number": "+85298901234",
                "profile_photo_name": "ffhq-sophie-ho.png",
                "profile_photo_url": "https://drive.google.com/uc?id=1VJs7pk9REsZ-zCGFvnoc8_Dyu36UQWfg",
                "is_staff": False,
                "is_superuser": False,
            },
            {
                "username": "hannah_ng",
                "password": "password123",
                "email": "hannah.ng@hku.hk",
                "first_name": "Hannah",
                "last_name": "Ng",
                "bio": "Social Sciences student searching for a female-friendly shared apartment near campus.",
                "phone_number": "+85299012345",
                "profile_photo_name": "ffhq-hannah-ng.png",
                "profile_photo_url": "https://drive.google.com/uc?id=1JjOslkBXUQS0KSztVl2TA0HBXuzVaEny",
                "is_staff": False,
                "is_superuser": False,
            },
            {
                "username": "admin_tszho",
                "password": "password123",
                "email": "tsz.ho@roomiehku.local",
                "first_name": "Tsz",
                "last_name": "Ho",
                "bio": "RoomieHKU staff moderator account for demo support and report handling.",
                "phone_number": "+85290123456",
                "profile_photo_name": "ffhq-staff.png",
                "profile_photo_url": "https://drive.google.com/uc?id=1ZbYrBs2VxQcBBi03kJLpF2PCVn5feWsD",
                "is_staff": True,
                "is_superuser": False,
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
                source_url=row.get("profile_photo_url"),
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
                "author": "noah_chan",
                "title": "2BR Flat in Kennedy Town (10 mins to HKU)",
                "description": (
                    "Bright two-bedroom flat with shared kitchen and washer. "
                    "Looking for one tidy roommate."
                ),
                "image_name": "listing-kennedy-town-room.jpg",
                "kaggle_member_path": "Airbnb Data/Training Data/living-room/seattle_1686930_1.jpg",
                "listing_type": "Apartment",
                "location": "Kennedy Town",
                "price": Decimal("9500.00"),
                "move_in_date": date(2026, 5, 1),
                "gender_preference": "N",
                "lifestyle_notes": "No smoking, quiet after 11pm.",
            },
            {
                "author": "daniel_wong",
                "title": "Dorm Spot Available at Pok Fu Lam",
                "description": (
                    "Subletting a dorm bed space for summer. Great for short-term stay."
                ),
                "image_name": "listing-pok-fulam-dorm-room.jpg",
                "kaggle_member_path": "Airbnb Data/Test Data/bedroom/berlin_17650843_2.jpg",
                "listing_type": "Dorm",
                "location": "Pok Fu Lam",
                "price": Decimal("4800.00"),
                "move_in_date": date(2026, 6, 1),
                "gender_preference": "N",
                "lifestyle_notes": "Best for early risers.",
            },
            {
                "author": "emily_kwok",
                "title": "Female Roommate Needed in Sai Ying Pun",
                "description": "Looking for a female roommate for a modern shared flat.",
                "image_name": "listing-sai-ying-pun-roommate-room.jpg",
                "kaggle_member_path": "Airbnb Data/Training Data/living-room/boston_11474629_1.jpg",
                "listing_type": "Roommate",
                "location": "Sai Ying Pun",
                "price": Decimal("7200.00"),
                "move_in_date": date(2026, 8, 15),
                "gender_preference": "F",
                "lifestyle_notes": "Clean and considerate shared living.",
            },
            {
                "author": "maya_shah",
                "title": "Studio Near HKU MTR Exit B1",
                "description": "Compact furnished studio, utilities included.",
                "image_name": "listing-hku-studio-room.jpg",
                "kaggle_member_path": "Airbnb Data/Test Data/kitchen/berlin_18646765_2.jpg",
                "listing_type": "Apartment",
                "location": "Shek Tong Tsui",
                "price": Decimal("11000.00"),
                "move_in_date": date(2026, 7, 1),
                "gender_preference": "N",
                "lifestyle_notes": "Ideal for one person, no pets.",
            },
            {
                "author": "marcus_leung",
                "title": "Roommate Search for 3BR in Mid-Levels",
                "description": "Two HKU postgrads seeking one more roommate.",
                "image_name": "listing-mid-levels-roommate-room.jpg",
                "kaggle_member_path": "Airbnb Data/Training Data/dining-room/boston_4351047_1.jpg",
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
                kaggle_member_path=row.get("kaggle_member_path"),
            ):
                changed = True

            if changed:
                post.save()
            posts[row["title"]] = post
        return posts

    def _seed_comments(self, users, posts):
        comments_data = [
            ("daniel_wong", "2BR Flat in Kennedy Town (10 mins to HKU)", "Is this still available for June move-in?"),
            ("hannah_ng", "2BR Flat in Kennedy Town (10 mins to HKU)", "Can I schedule a viewing this weekend?"),
            ("sophie_ho", "Female Roommate Needed in Sai Ying Pun", "This area is super convenient for HKU."),
            ("noah_chan", "Roommate Search for 3BR in Mid-Levels", "What is the nearest bus stop?"),
        ]
        for username, post_title, content in comments_data:
            Comment.objects.get_or_create(
                author=users[username],
                post=posts[post_title],
                content=content,
            )

    def _seed_likes(self, users, posts):
        likes_data = [
            ("daniel_wong", "2BR Flat in Kennedy Town (10 mins to HKU)"),
            ("hannah_ng", "2BR Flat in Kennedy Town (10 mins to HKU)"),
            ("maya_shah", "Female Roommate Needed in Sai Ying Pun"),
            ("admin_tszho", "Roommate Search for 3BR in Mid-Levels"),
        ]
        for username, post_title in likes_data:
            Like.objects.get_or_create(
                user=users[username],
                post=posts[post_title],
            )

    def _seed_saved_listings(self, users, posts):
        saved_data = [
            ("noah_chan", "Dorm Spot Available at Pok Fu Lam"),
            ("sophie_ho", "Studio Near HKU MTR Exit B1"),
            ("natalie_cheng", "2BR Flat in Kennedy Town (10 mins to HKU)"),
            ("admin_tszho", "Female Roommate Needed in Sai Ying Pun"),
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

    def _ensure_uploaded_image(
        self,
        field_file,
        relative_name,
        source_url=None,
        kaggle_member_path=None,
    ):
        upload_to = field_file.field.upload_to
        upload_prefix = upload_to if upload_to.endswith("/") else f"{upload_to}/"
        storage_name = f"{upload_prefix}{relative_name}"

        if not default_storage.exists(storage_name):
            if kaggle_member_path:
                content = self._download_kaggle_room_image_or_placeholder(kaggle_member_path)
            elif source_url:
                content = self._download_or_placeholder(source_url)
            else:
                content = DEMO_IMAGE_BYTES
            default_storage.save(storage_name, ContentFile(content))

        if field_file.name != storage_name:
            field_file.name = storage_name
            return True
        return False

    def _download_or_placeholder(self, source_url):
        if not source_url:
            return DEMO_IMAGE_BYTES

        try:
            data = self._download_image_bytes(source_url)
            if self._looks_like_image_bytes(data):
                return data
        except Exception as exc:
            self.stdout.write(
                self.style.WARNING(
                    f"Could not download profile image from {source_url}: {exc}. Using placeholder."
                )
            )

        return DEMO_IMAGE_BYTES

    def _download_kaggle_room_image_or_placeholder(self, member_path):
        try:
            data = self._read_kaggle_room_image_bytes(member_path)
            if self._looks_like_image_bytes(data):
                return data
        except Exception as exc:
            self.stdout.write(
                self.style.WARNING(
                    f"Could not read Kaggle room image {member_path}: {exc}. Using placeholder."
                )
            )

        return DEMO_IMAGE_BYTES

    def _read_kaggle_room_image_bytes(self, member_path):
        zip_path = self._ensure_kaggle_house_rooms_zip()
        with zipfile.ZipFile(zip_path) as archive:
            return archive.read(member_path)

    def _ensure_kaggle_house_rooms_zip(self):
        cache_path = KAGGLE_HOUSE_ROOMS_ZIP_CACHE
        if cache_path.exists() and cache_path.stat().st_size > 100_000_000:
            return cache_path

        request = Request(
            KAGGLE_HOUSE_ROOMS_ZIP_URL,
            headers={"User-Agent": "RoomieHKU-Seed/1.0"},
        )
        tmp_path = cache_path.with_suffix(".tmp")

        with urlopen(request, timeout=60) as response:  # nosec B310
            with tmp_path.open("wb") as target:
                while True:
                    chunk = response.read(1024 * 1024)
                    if not chunk:
                        break
                    target.write(chunk)

        tmp_path.replace(cache_path)
        return cache_path

    def _download_image_bytes(self, source_url):
        request = Request(source_url, headers={"User-Agent": "RoomieHKU-Seed/1.0"})
        with urlopen(request, timeout=20) as response:  # nosec B310
            payload = response.read()
            content_type = response.headers.get_content_type() if response.headers else ""
            final_url = response.geturl()

        if self._looks_like_image_bytes(payload):
            return payload

        if content_type == "text/html" or b"<html" in payload[:512].lower():
            action_url, query_params = self._extract_google_drive_download_form(
                html_text=payload.decode("utf-8", errors="ignore"),
                base_url=final_url,
            )
            if action_url and query_params:
                follow_up_url = f"{action_url}?{urlencode(query_params)}"
                follow_request = Request(follow_up_url, headers={"User-Agent": "RoomieHKU-Seed/1.0"})
                with urlopen(follow_request, timeout=20) as response:  # nosec B310
                    follow_payload = response.read()
                if self._looks_like_image_bytes(follow_payload):
                    return follow_payload

        raise ValueError("No valid image payload returned")

    def _extract_google_drive_download_form(self, html_text, base_url):
        action_match = re.search(
            r"<form[^>]+id=['\"]download-form['\"][^>]+action=['\"]([^'\"]+)['\"]",
            html_text,
            re.IGNORECASE,
        )
        if not action_match:
            return None, None

        input_matches = re.findall(
            r"<input[^>]+name=['\"]([^'\"]+)['\"][^>]+value=['\"]([^'\"]*)['\"]",
            html_text,
            re.IGNORECASE,
        )
        if not input_matches:
            return None, None

        action_url = urljoin(base_url, unescape(action_match.group(1)))
        query_params = {name: unescape(value) for name, value in input_matches}
        return action_url, query_params

    def _looks_like_image_bytes(self, payload):
        return (
            payload.startswith(b"\x89PNG\r\n\x1a\n")
            or payload.startswith(b"\xff\xd8\xff")
            or payload.startswith(b"GIF87a")
            or payload.startswith(b"GIF89a")
            or (len(payload) > 12 and payload.startswith(b"RIFF") and payload[8:12] == b"WEBP")
        )
