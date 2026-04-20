from datetime import date
from decimal import Decimal
from urllib.request import Request, urlopen

from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.core.management.base import BaseCommand
from django.db import connection
from django.db.models import Count
from django.utils import timezone

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
                "username": "noah_chan",
                "password": "password123",
                "email": "noah.chan@hku.hk",
                "first_name": "Noah",
                "last_name": "Chan",
                "bio": "Year 4 CS at HKU. Big on clean kitchens, low-drama flat vibes, and sunrise coffee runs.",
                "phone_number": "+85291234567",
                "profile_photo_name": "student-noah-chan.jpg",
                "profile_photo_url": "https://unsplash.com/photos/VBIMtDdjuWc/download?force=true&w=700",
                "is_staff": False,
                "is_superuser": False,
            },
            {
                "username": "daniel_wong",
                "password": "password123",
                "email": "daniel.wong@hku.hk",
                "first_name": "Daniel",
                "last_name": "Wong",
                "bio": "MFin student hunting a bright room near campus with solid AC and a proper desk setup.",
                "phone_number": "+85292345678",
                "profile_photo_name": "student-daniel-wong.jpg",
                "profile_photo_url": "https://unsplash.com/photos/dbOaUuoPXhY/download?force=true&w=700",
                "is_staff": False,
                "is_superuser": False,
            },
            {
                "username": "marcus_leung",
                "password": "password123",
                "email": "marcus.leung@hku.hk",
                "first_name": "Marcus",
                "last_name": "Leung",
                "bio": "Economics undergrad. Respectful, tidy, and always down for a late-night cha chaan teng run.",
                "phone_number": "+85293456789",
                "profile_photo_name": "student-marcus-leung.jpg",
                "profile_photo_url": "https://unsplash.com/photos/-ZFvSWK4L28/download?force=true&w=700",
                "is_staff": False,
                "is_superuser": False,
            },
            {
                "username": "isaac_lau",
                "password": "password123",
                "email": "isaac.lau@hku.hk",
                "first_name": "Isaac",
                "last_name": "Lau",
                "bio": "Law student who loves a quiet weekday home and a social but chill weekend household.",
                "phone_number": "+85294567890",
                "profile_photo_name": "student-isaac-lau.jpg",
                "profile_photo_url": "https://unsplash.com/photos/_odDcwscl98/download?force=true&w=700",
                "is_staff": False,
                "is_superuser": False,
            },
            {
                "username": "maya_shah",
                "password": "password123",
                "email": "maya.shah@hku.hk",
                "first_name": "Maya",
                "last_name": "Shah",
                "bio": "Public Health student. Looking for roommates who keep shared spaces calm, clean, and cozy.",
                "phone_number": "+85295678901",
                "profile_photo_name": "student-maya-shah.jpg",
                "profile_photo_url": "https://unsplash.com/photos/naeJ0lmTdIg/download?force=true&w=700",
                "is_staff": False,
                "is_superuser": False,
            },
            {
                "username": "natalie_cheng",
                "password": "password123",
                "email": "natalie.cheng@hku.hk",
                "first_name": "Natalie",
                "last_name": "Cheng",
                "bio": "Architecture major who needs natural light, clean lines, and room for model-making nights.",
                "phone_number": "+85296789012",
                "profile_photo_name": "student-natalie-cheng.jpg",
                "profile_photo_url": "https://unsplash.com/photos/fjptyBGkKSM/download?force=true&w=700",
                "is_staff": False,
                "is_superuser": False,
            },
            {
                "username": "emily_kwok",
                "password": "password123",
                "email": "emily.kwok@hku.hk",
                "first_name": "Emily",
                "last_name": "Kwok",
                "bio": "Nursing student on rotation schedules. Appreciates considerate roommates and quiet sleep windows.",
                "phone_number": "+85297890123",
                "profile_photo_name": "student-emily-kwok.jpg",
                "profile_photo_url": "https://unsplash.com/photos/FcLyt7lW5wg/download?force=true&w=700",
                "is_staff": False,
                "is_superuser": False,
            },
            {
                "username": "sophie_ho",
                "password": "password123",
                "email": "sophie.ho@hku.hk",
                "first_name": "Sophie",
                "last_name": "Ho",
                "bio": "MBA candidate. Strong Wi-Fi, strong coffee, and a living room that still looks good at 2am.",
                "phone_number": "+85298901234",
                "profile_photo_name": "student-sophie-ho.jpg",
                "profile_photo_url": "https://unsplash.com/photos/EWN0rrwbBIQ/download?force=true&w=700",
                "is_staff": False,
                "is_superuser": False,
            },
            {
                "username": "hannah_ng",
                "password": "password123",
                "email": "hannah.ng@hku.hk",
                "first_name": "Hannah",
                "last_name": "Ng",
                "bio": "Social Sciences student, easygoing and organized. Loves a warm, homey shared apartment.",
                "phone_number": "+85299012345",
                "profile_photo_name": "student-hannah-ng.jpg",
                "profile_photo_url": "https://unsplash.com/photos/Ph2KD5qr7VQ/download?force=true&w=700",
                "is_staff": False,
                "is_superuser": False,
            },
            {
                "username": "leo_pang",
                "password": "password123",
                "email": "leo.pang@hku.hk",
                "first_name": "Leo",
                "last_name": "Pang",
                "bio": "Engineering student, gym-before-class routine, values direct communication and shared chore systems.",
                "phone_number": "+85291112233",
                "profile_photo_name": "student-leo-pang.jpg",
                "profile_photo_url": "https://unsplash.com/photos/laORtJZaieU/download?force=true&w=700",
                "is_staff": False,
                "is_superuser": False,
            },
            {
                "username": "grace_lam",
                "password": "password123",
                "email": "grace.lam@hku.hk",
                "first_name": "Grace",
                "last_name": "Lam",
                "bio": "Psychology student, loves calm interiors and host-small-dinner energy with good playlists.",
                "phone_number": "+85292223344",
                "profile_photo_name": "student-grace-lam.jpg",
                "profile_photo_url": "https://unsplash.com/photos/PchC6toZ3_c/download?force=true&w=700",
                "is_staff": False,
                "is_superuser": False,
            },
            {
                "username": "ethan_yu",
                "password": "password123",
                "email": "ethan.yu@hku.hk",
                "first_name": "Ethan",
                "last_name": "Yu",
                "bio": "Data Science student who keeps a minimalist room and a strict no-dishes-overnight policy.",
                "phone_number": "+85293334455",
                "profile_photo_name": "student-ethan-yu.jpg",
                "profile_photo_url": "https://unsplash.com/photos/AZrBFoXP_3I/download?force=true&w=700",
                "is_staff": False,
                "is_superuser": False,
            },
            {
                "username": "jasmine_lee",
                "password": "password123",
                "email": "jasmine.lee@hku.hk",
                "first_name": "Jasmine",
                "last_name": "Lee",
                "bio": "Education student, plant parent, and fan of cozy corners and thoughtful roommate boundaries.",
                "phone_number": "+85294445566",
                "profile_photo_name": "student-jasmine-lee.jpg",
                "profile_photo_url": "https://unsplash.com/photos/Ie_gHAEfBR4/download?force=true&w=700",
                "is_staff": False,
                "is_superuser": False,
            },
            {
                "username": "ryan_cheung",
                "password": "password123",
                "email": "ryan.cheung@hku.hk",
                "first_name": "Ryan",
                "last_name": "Cheung",
                "bio": "Media student and night owl editor. Needs a room where creative chaos still stays respectful.",
                "phone_number": "+85295556677",
                "profile_photo_name": "student-ryan-cheung.jpg",
                "profile_photo_url": "https://unsplash.com/photos/5l3lmWIeTE0/download?force=true&w=700",
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
                "profile_photo_name": "student-admin-tszho.jpg",
                "profile_photo_url": "https://unsplash.com/photos/AypTGow2TGQ/download?force=true&w=700",
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
        has_source_image_url_column = self._post_table_has_source_image_url_column()
        posts_data = [
            {
                "author": "noah_chan",
                "title": "2BR Flat in Kennedy Town (10 mins to HKU)",
                "description": (
                    "Sunny two-bedroom with a breezy living room and legit sunset views. "
                    "Current vibe is clean, friendly, and weekday-quiet after midnight."
                ),
                "image_name": "ktown-sunset-2br.jpg",
                "image_source_url": "https://unsplash.com/photos/k-559RP6fdo/download?force=true&w=1200",
                "listing_type": "Apartment",
                "location": "Kennedy Town",
                "price": Decimal("9800.00"),
                "move_in_date": date(2026, 5, 20),
                "gender_preference": "N",
                "lifestyle_notes": "No smoking indoors. Shared Google Sheet for chores keeps things smooth.",
            },
            {
                "author": "daniel_wong",
                "title": "Dorm Spot Available at Pok Fu Lam",
                "description": (
                    "Short-term hall sublet with good daylight and a calm floor community. "
                    "Great if you want campus access without the long commute grind."
                ),
                "image_name": "pokfulam-hall-spot.jpg",
                "image_source_url": "https://unsplash.com/photos/Ga3OJbM1nhs/download?force=true&w=1200",
                "listing_type": "Dorm",
                "location": "Pok Fu Lam",
                "price": Decimal("5200.00"),
                "move_in_date": date(2026, 6, 1),
                "gender_preference": "N",
                "lifestyle_notes": "Works best for someone who likes a tidy desk and early classes.",
            },
            {
                "author": "emily_kwok",
                "title": "Female Roommate Needed in Sai Ying Pun",
                "description": (
                    "Modern shared flat with warm lighting and a surprisingly spacious kitchen. "
                    "We keep it relaxed, respectful, and low-noise during exam weeks."
                ),
                "image_name": "syp-female-roommate-flat.jpg",
                "image_source_url": "https://unsplash.com/photos/wD3dur3v9aE/download?force=true&w=1200",
                "listing_type": "Roommate",
                "location": "Sai Ying Pun",
                "price": Decimal("7600.00"),
                "move_in_date": date(2026, 7, 10),
                "gender_preference": "F",
                "lifestyle_notes": "Night-shift friendly. Kitchen chat > house party energy.",
            },
            {
                "author": "maya_shah",
                "title": "Studio Near HKU MTR Exit B1",
                "description": (
                    "Compact studio with smart storage, strong AC, and a cozy reading nook by the window. "
                    "Perfect for focused semester mode."
                ),
                "image_name": "hku-mtr-minimal-studio.jpg",
                "image_source_url": "https://unsplash.com/photos/nwf0GGzeT3M/download?force=true&w=1200",
                "listing_type": "Apartment",
                "location": "Shek Tong Tsui",
                "price": Decimal("11200.00"),
                "move_in_date": date(2026, 8, 1),
                "gender_preference": "N",
                "lifestyle_notes": "No pets, no smoking, yes to peaceful evenings.",
            },
            {
                "author": "marcus_leung",
                "title": "Roommate Search for 3BR in Mid-Levels",
                "description": (
                    "Two postgrads already in. Looking for one roommate who is communicative, tidy, "
                    "and into a chill home base after hectic campus days."
                ),
                "image_name": "midlevels-3br-roommate.jpg",
                "image_source_url": "https://unsplash.com/photos/HC1KZPFxP38/download?force=true&w=1200",
                "listing_type": "Roommate",
                "location": "Mid-Levels",
                "price": Decimal("8900.00"),
                "move_in_date": date(2026, 9, 1),
                "gender_preference": "N",
                "lifestyle_notes": "Shared dinners are optional but highly encouraged.",
            },
            {
                "author": "leo_pang",
                "title": "Bunk Room in Pok Fu Lam Student Hostel",
                "description": (
                    "Affordable bunk setup with clean common areas and a social-but-not-chaotic floor. "
                    "Ideal for students who want value and campus proximity."
                ),
                "image_name": "pokfulam-bunk-hostel.jpg",
                "image_source_url": "https://unsplash.com/photos/4gvuZJ2weOs/download?force=true&w=1200",
                "listing_type": "Dorm",
                "location": "Pok Fu Lam",
                "price": Decimal("4300.00"),
                "move_in_date": date(2026, 5, 15),
                "gender_preference": "M",
                "lifestyle_notes": "Gym schedule mornings. Lights-out culture around midnight.",
            },
            {
                "author": "grace_lam",
                "title": "Bonham Road Shared Flat with Big Study Desk",
                "description": (
                    "Bright room with leafy street views and enough desk space for finals season chaos. "
                    "Flatmates are warm, independent, and considerate."
                ),
                "image_name": "bonham-road-study-flat.jpg",
                "image_source_url": "https://unsplash.com/photos/H7SqlUp4JVE/download?force=true&w=1200",
                "listing_type": "Apartment",
                "location": "Sai Ying Pun",
                "price": Decimal("8400.00"),
                "move_in_date": date(2026, 6, 20),
                "gender_preference": "F",
                "lifestyle_notes": "Plant-friendly home. Quiet hour after 11:30pm.",
            },
            {
                "author": "ethan_yu",
                "title": "Western District Dorm-Style Room for Summer Term",
                "description": (
                    "Simple setup, super practical location, and great if you need a base near HKU for summer. "
                    "Fast move-in possible."
                ),
                "image_name": "west-district-summer-dorm.jpg",
                "image_source_url": "https://unsplash.com/photos/KU5NrCY1cCc/download?force=true&w=1200",
                "listing_type": "Dorm",
                "location": "Western District",
                "price": Decimal("5000.00"),
                "move_in_date": date(2026, 5, 28),
                "gender_preference": "N",
                "lifestyle_notes": "No overnight guests on weekdays.",
            },
            {
                "author": "jasmine_lee",
                "title": "Spare Room in High Street Walk-Up",
                "description": (
                    "Character flat with wooden details, cozy lighting, and a super local neighborhood feel. "
                    "Great cafes, groceries, and transport all within minutes."
                ),
                "image_name": "high-street-walkup-room.jpg",
                "image_source_url": "https://unsplash.com/photos/i7-zqldb2os/download?force=true&w=1200",
                "listing_type": "Roommate",
                "location": "Sai Ying Pun",
                "price": Decimal("7800.00"),
                "move_in_date": date(2026, 7, 1),
                "gender_preference": "F",
                "lifestyle_notes": "Best fit for someone tidy and communicative.",
            },
            {
                "author": "ryan_cheung",
                "title": "Minimalist Room by HKU MTR (Plant-Lover Home)",
                "description": (
                    "Calm, minimal room with soft daylight and a mellow living room setup. "
                    "If you like quiet focus and low-key evenings, this one feels right."
                ),
                "image_name": "hku-mtr-minimal-plant-room.jpg",
                "image_source_url": "https://unsplash.com/photos/NcuDuNcf5Rs/download?force=true&w=1200",
                "listing_type": "Apartment",
                "location": "Shek Tong Tsui",
                "price": Decimal("8600.00"),
                "move_in_date": date(2026, 8, 18),
                "gender_preference": "N",
                "lifestyle_notes": "No smoking. Low-volume music nights are welcome.",
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
            post = Post.objects.filter(author=author, title=row["title"]).first()
            if post is None:
                if has_source_image_url_column:
                    post = self._create_post_with_source_image_url(author, row, defaults)
                else:
                    post = Post.objects.create(author=author, title=row["title"], **defaults)
                created = True
            else:
                created = False

            changed = created
            if not created:
                for field, value in defaults.items():
                    if getattr(post, field) != value:
                        setattr(post, field, value)
                        changed = True

            if has_source_image_url_column:
                self._sync_source_image_url_column(post.pk, row["image_source_url"])

            if self._ensure_uploaded_image(
                field_file=post.image_url,
                relative_name=row["image_name"],
                source_url=row.get("image_source_url"),
            ):
                changed = True

            if changed:
                post.save()
            posts[row["title"]] = post
        return posts

    def _post_table_has_source_image_url_column(self):
        with connection.cursor() as cursor:
            cursor.execute("PRAGMA table_info(core_post)")
            return any(column[1] == "source_image_url" for column in cursor.fetchall())

    def _create_post_with_source_image_url(self, author, row, defaults):
        now = timezone.now()
        with connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO core_post (
                    title,
                    description,
                    image_url,
                    listing_type,
                    location,
                    price,
                    move_in_date,
                    gender_preference,
                    lifestyle_notes,
                    likes_count,
                    created_at,
                    updated_at,
                    author_id,
                    hidden_at,
                    is_hidden,
                    views_count,
                    source_image_url
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """,
                [
                    row["title"],
                    defaults["description"],
                    "",
                    defaults["listing_type"],
                    defaults["location"],
                    defaults["price"],
                    defaults["move_in_date"],
                    defaults["gender_preference"],
                    defaults["lifestyle_notes"],
                    0,
                    now,
                    now,
                    author.pk,
                    None,
                    False,
                    0,
                    row["image_source_url"],
                ],
            )
            post_id = cursor.lastrowid
        return Post.objects.get(pk=post_id)

    def _sync_source_image_url_column(self, post_id, source_image_url):
        with connection.cursor() as cursor:
            cursor.execute(
                "UPDATE core_post SET source_image_url = %s WHERE id = %s",
                [source_image_url, post_id],
            )

    def _seed_comments(self, users, posts):
        comments_data = [
            ("daniel_wong", "2BR Flat in Kennedy Town (10 mins to HKU)", "This place has exactly the sunset vibe I was looking for."),
            ("hannah_ng", "2BR Flat in Kennedy Town (10 mins to HKU)", "Can we do a quick viewing after class tomorrow?"),
            ("sophie_ho", "Female Roommate Needed in Sai Ying Pun", "Love this area. Commute and food options are elite."),
            ("noah_chan", "Roommate Search for 3BR in Mid-Levels", "How's the morning light in the available room?"),
            ("grace_lam", "Studio Near HKU MTR Exit B1", "Is the desk included or is that your setup?"),
            ("ethan_yu", "Western District Dorm-Style Room for Summer Term", "Is short lease until August okay?"),
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
            ("leo_pang", "Bunk Room in Pok Fu Lam Student Hostel"),
            ("grace_lam", "Bonham Road Shared Flat with Big Study Desk"),
            ("ethan_yu", "Minimalist Room by HKU MTR (Plant-Lover Home)"),
            ("jasmine_lee", "Studio Near HKU MTR Exit B1"),
            ("ryan_cheung", "Spare Room in High Street Walk-Up"),
            ("emily_kwok", "Western District Dorm-Style Room for Summer Term"),
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
            ("leo_pang", "Bonham Road Shared Flat with Big Study Desk"),
            ("grace_lam", "Minimalist Room by HKU MTR (Plant-Lover Home)"),
            ("ethan_yu", "Spare Room in High Street Walk-Up"),
            ("jasmine_lee", "Roommate Search for 3BR in Mid-Levels"),
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

    def _ensure_uploaded_image(self, field_file, relative_name, source_url=None):
        upload_to = field_file.field.upload_to
        upload_prefix = upload_to if upload_to.endswith("/") else f"{upload_to}/"
        storage_name = f"{upload_prefix}{relative_name}"

        if not default_storage.exists(storage_name):
            content = self._download_or_placeholder(source_url) if source_url else DEMO_IMAGE_BYTES
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
                    f"Could not download image from {source_url}: {exc}. Using placeholder."
                )
            )

        return DEMO_IMAGE_BYTES

    def _download_image_bytes(self, source_url):
        request = Request(source_url, headers={"User-Agent": "RoomieHKU-Seed/1.0"})
        with urlopen(request, timeout=20) as response:  # nosec B310
            return response.read()

    def _looks_like_image_bytes(self, payload):
        return (
            payload.startswith(b"\x89PNG\r\n\x1a\n")
            or payload.startswith(b"\xff\xd8\xff")
            or payload.startswith(b"GIF87a")
            or payload.startswith(b"GIF89a")
            or (len(payload) > 12 and payload.startswith(b"RIFF") and payload[8:12] == b"WEBP")
        )
