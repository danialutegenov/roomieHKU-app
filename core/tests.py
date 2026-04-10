from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.db import IntegrityError
from django.test import TestCase
from django.urls import reverse

from .models import Comment, Like, Post, SavedListing, User


def make_uploaded_image(filename):
    image_bytes = (
        b"GIF89a\x01\x00\x01\x00\x80\x00\x00\x00\x00\x00"
        b"\xff\xff\xff!\xf9\x04\x00\x00\x00\x00\x00,\x00\x00"
        b"\x00\x00\x01\x00\x01\x00\x00\x02\x02D\x01\x00;"
    )
    return SimpleUploadedFile(filename, image_bytes, content_type="image/gif")


class CoreModelTests(TestCase):
    def setUp(self):
        self.author = User.objects.create_user(
            username="author1",
            password="password123",
            email="author1@example.com",
        )
        self.other_user = User.objects.create_user(
            username="user2",
            password="password123",
            email="user2@example.com",
        )
        self.post = Post.objects.create(
            author=self.author,
            title="Near HKU Station",
            description="Two-bedroom flat with shared kitchen.",
            image_url=make_uploaded_image("coremodel-listing.gif"),
            listing_type="Apartment",
            location="Kennedy Town",
            price="9500.00",
        )

    def test_like_unique_per_user_post(self):
        Like.objects.create(user=self.other_user, post=self.post)
        with self.assertRaises(IntegrityError):
            Like.objects.create(user=self.other_user, post=self.post)

    def test_saved_listing_unique_per_user_post(self):
        SavedListing.objects.create(user=self.other_user, post=self.post)
        with self.assertRaises(IntegrityError):
            SavedListing.objects.create(user=self.other_user, post=self.post)

    def test_post_price_must_be_non_negative(self):
        invalid_post = Post(
            author=self.author,
            title="Invalid Price Listing",
            description="Should fail validation.",
            image_url=make_uploaded_image("invalid-price.gif"),
            listing_type="Roommate",
            location="Sai Ying Pun",
            price="-1.00",
        )
        with self.assertRaises(ValidationError):
            invalid_post.full_clean()

    def test_likes_count_syncs_on_like_create_and_delete(self):
        self.assertEqual(self.post.likes_count, 0)

        like = Like.objects.create(user=self.other_user, post=self.post)
        self.post.refresh_from_db()
        self.assertEqual(self.post.likes_count, 1)

        like.delete()
        self.post.refresh_from_db()
        self.assertEqual(self.post.likes_count, 0)


class AuthFlowTests(TestCase):
    def test_signup_creates_user_and_logs_in(self):
        response = self.client.post(
            reverse("core:signup"),
            {
                "username": "newuser",
                "email": "newuser@example.com",
                "password1": "StrongPass123",
                "password2": "StrongPass123",
            },
        )
        self.assertRedirects(response, reverse("core:listing_list"))
        self.assertTrue(User.objects.filter(username="newuser").exists())
        self.assertIn("_auth_user_id", self.client.session)

    def test_login_and_logout(self):
        User.objects.create_user(
            username="loginuser",
            password="password123",
            email="login@example.com",
        )
        login_response = self.client.post(
            reverse("core:login"),
            {"username": "loginuser", "password": "password123"},
        )
        self.assertRedirects(login_response, reverse("core:listing_list"))
        self.assertIn("_auth_user_id", self.client.session)

        logout_response = self.client.post(reverse("core:logout"))
        self.assertRedirects(logout_response, reverse("core:listing_list"))
        self.assertNotIn("_auth_user_id", self.client.session)


class ListingAndPermissionTests(TestCase):
    def setUp(self):
        self.author = User.objects.create_user(
            username="author1",
            password="password123",
            email="author1@example.com",
        )
        self.other_user = User.objects.create_user(
            username="user2",
            password="password123",
            email="user2@example.com",
        )
        self.post = Post.objects.create(
            author=self.author,
            title="Near HKU Station",
            description="Two-bedroom flat with shared kitchen.",
            image_url=make_uploaded_image("perm-listing.gif"),
            listing_type="Apartment",
            location="Kennedy Town",
            price="9500.00",
        )

    def test_listing_list_and_detail_are_public(self):
        list_response = self.client.get(reverse("core:listing_list"))
        detail_response = self.client.get(reverse("core:listing_detail", args=[self.post.pk]))
        self.assertEqual(list_response.status_code, 200)
        self.assertEqual(detail_response.status_code, 200)

    def test_anonymous_user_redirected_for_protected_routes(self):
        protected_routes = [
            reverse("core:listing_create"),
            reverse("core:listing_update", args=[self.post.pk]),
            reverse("core:listing_delete", args=[self.post.pk]),
            reverse("core:toggle_like", args=[self.post.pk]),
            reverse("core:toggle_save", args=[self.post.pk]),
            reverse("core:add_comment", args=[self.post.pk]),
            reverse("core:profile_edit"),
        ]
        for route in protected_routes:
            response = self.client.post(route)
            self.assertEqual(response.status_code, 302)
            self.assertTrue(response.url.startswith(reverse("core:login")))

    def test_non_owner_cannot_edit_or_delete_post(self):
        self.client.login(username="user2", password="password123")
        edit_response = self.client.get(reverse("core:listing_update", args=[self.post.pk]))
        delete_response = self.client.post(reverse("core:listing_delete", args=[self.post.pk]))
        self.assertEqual(edit_response.status_code, 403)
        self.assertEqual(delete_response.status_code, 403)

    def test_non_owner_cannot_delete_comment(self):
        comment = Comment.objects.create(post=self.post, author=self.author, content="Owner comment")
        self.client.login(username="user2", password="password123")
        response = self.client.post(reverse("core:delete_comment", args=[comment.pk]))
        self.assertEqual(response.status_code, 403)
        self.assertTrue(Comment.objects.filter(pk=comment.pk).exists())


class ListingFilterTests(TestCase):
    def setUp(self):
        author = User.objects.create_user(
            username="author",
            password="password123",
            email="author@example.com",
        )
        self.post_1 = Post.objects.create(
            author=author,
            title="Studio near HKU",
            description="Quiet and clean studio",
            image_url=make_uploaded_image("filter-1.gif"),
            listing_type="Apartment",
            location="Kennedy Town",
            price="7000.00",
        )
        self.post_2 = Post.objects.create(
            author=author,
            title="Dorm bed space",
            description="Affordable dorm option",
            image_url=make_uploaded_image("filter-2.gif"),
            listing_type="Dorm",
            location="Pok Fu Lam",
            price="4000.00",
        )
        self.post_3 = Post.objects.create(
            author=author,
            title="Roommate wanted",
            description="Looking for tidy roommate",
            image_url=make_uploaded_image("filter-3.gif"),
            listing_type="Roommate",
            location="Kennedy Town",
            price="5500.00",
        )

    def test_keyword_filter(self):
        response = self.client.get(reverse("core:listing_list"), {"q": "studio"})
        post_ids = set(response.context["posts"].values_list("id", flat=True))
        self.assertEqual(post_ids, {self.post_1.id})

    def test_type_location_and_price_filters(self):
        response = self.client.get(
            reverse("core:listing_list"),
            {
                "listing_type": "Roommate",
                "location": "Kennedy",
                "min_price": "5000",
                "max_price": "6000",
            },
        )
        post_ids = set(response.context["posts"].values_list("id", flat=True))
        self.assertEqual(post_ids, {self.post_3.id})


class PostCrudTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="creator",
            password="password123",
            email="creator@example.com",
        )
        self.post = Post.objects.create(
            author=self.user,
            title="Initial Listing",
            description="Initial description",
            image_url=make_uploaded_image("crud-initial.gif"),
            listing_type="Apartment",
            location="Sai Ying Pun",
            price="8000.00",
        )

    def test_owner_create_update_delete_post(self):
        self.client.login(username="creator", password="password123")
        create_response = self.client.post(
            reverse("core:listing_create"),
            {
                "title": "New Listing",
                "description": "Created through test",
                "image_url": make_uploaded_image("crud-new.gif"),
                "listing_type": "Dorm",
                "location": "Kennedy Town",
                "price": "6000.00",
                "move_in_date": "2026-05-01",
                "gender_preference": "N",
                "lifestyle_notes": "No smoking",
            },
        )
        created_post = Post.objects.get(title="New Listing")
        self.assertRedirects(create_response, reverse("core:listing_detail", args=[created_post.pk]))
        self.assertEqual(created_post.author, self.user)

        update_response = self.client.post(
            reverse("core:listing_update", args=[self.post.pk]),
            {
                "title": "Updated Listing",
                "description": self.post.description,
                "image_url": self.post.image_url,
                "listing_type": self.post.listing_type,
                "location": self.post.location,
                "price": self.post.price,
                "move_in_date": "",
                "gender_preference": self.post.gender_preference,
                "lifestyle_notes": self.post.lifestyle_notes,
            },
        )
        self.assertRedirects(update_response, reverse("core:listing_detail", args=[self.post.pk]))
        self.post.refresh_from_db()
        self.assertEqual(self.post.title, "Updated Listing")

        delete_response = self.client.post(reverse("core:listing_delete", args=[self.post.pk]))
        self.assertRedirects(delete_response, reverse("core:listing_list"))
        self.assertFalse(Post.objects.filter(pk=self.post.pk).exists())


class InteractionTests(TestCase):
    def setUp(self):
        self.author = User.objects.create_user(
            username="author",
            password="password123",
            email="author@example.com",
        )
        self.user = User.objects.create_user(
            username="viewer",
            password="password123",
            email="viewer@example.com",
        )
        self.post = Post.objects.create(
            author=self.author,
            title="Likeable Listing",
            description="Description",
            image_url=make_uploaded_image("interaction-listing.gif"),
            listing_type="Apartment",
            location="Kennedy Town",
            price="9500.00",
        )
        self.client.login(username="viewer", password="password123")

    def test_like_toggle(self):
        first = self.client.post(reverse("core:toggle_like", args=[self.post.pk]))
        self.assertRedirects(first, reverse("core:listing_detail", args=[self.post.pk]))
        self.assertTrue(Like.objects.filter(user=self.user, post=self.post).exists())
        self.post.refresh_from_db()
        self.assertEqual(self.post.likes_count, 1)

        second = self.client.post(reverse("core:toggle_like", args=[self.post.pk]))
        self.assertRedirects(second, reverse("core:listing_detail", args=[self.post.pk]))
        self.assertFalse(Like.objects.filter(user=self.user, post=self.post).exists())
        self.post.refresh_from_db()
        self.assertEqual(self.post.likes_count, 0)

    def test_save_toggle(self):
        first = self.client.post(reverse("core:toggle_save", args=[self.post.pk]))
        self.assertRedirects(first, reverse("core:listing_detail", args=[self.post.pk]))
        self.assertTrue(SavedListing.objects.filter(user=self.user, post=self.post).exists())

        second = self.client.post(reverse("core:toggle_save", args=[self.post.pk]))
        self.assertRedirects(second, reverse("core:listing_detail", args=[self.post.pk]))
        self.assertFalse(SavedListing.objects.filter(user=self.user, post=self.post).exists())

    def test_create_and_delete_own_comment(self):
        create_response = self.client.post(
            reverse("core:add_comment", args=[self.post.pk]),
            {"content": "Interested!"},
        )
        self.assertRedirects(create_response, reverse("core:listing_detail", args=[self.post.pk]))
        comment = Comment.objects.get(author=self.user, post=self.post)
        self.assertEqual(comment.content, "Interested!")

        delete_response = self.client.post(reverse("core:delete_comment", args=[comment.pk]))
        self.assertRedirects(delete_response, reverse("core:listing_detail", args=[self.post.pk]))
        self.assertFalse(Comment.objects.filter(pk=comment.pk).exists())


class ProfileAndDashboardTests(TestCase):
    def setUp(self):
        self.staff_user = User.objects.create_user(
            username="staffuser",
            password="password123",
            email="staff@example.com",
            is_staff=True,
        )
        self.user = User.objects.create_user(
            username="normaluser",
            password="password123",
            email="normal@example.com",
        )
        self.post = Post.objects.create(
            author=self.user,
            title="Dashboard Post",
            description="Desc",
            image_url=make_uploaded_image("dashboard-listing.gif"),
            listing_type="Apartment",
            location="Pok Fu Lam",
            price="7000.00",
        )
        Comment.objects.create(post=self.post, author=self.user, content="Sample comment")
        Like.objects.create(user=self.staff_user, post=self.post)
        SavedListing.objects.create(user=self.staff_user, post=self.post)

    def test_profile_edit(self):
        self.client.login(username="normaluser", password="password123")
        response = self.client.post(
            reverse("core:profile_edit"),
            {
                "email": "updated@example.com",
                "bio": "Updated bio",
                "phone_number": "12345678",
                "profile_photo": make_uploaded_image("profile-photo.gif"),
            },
        )
        self.assertRedirects(response, reverse("core:profile_edit"))
        self.user.refresh_from_db()
        self.assertEqual(self.user.email, "updated@example.com")
        self.assertEqual(self.user.bio, "Updated bio")
        self.assertEqual(self.user.phone_number, "12345678")
        self.assertIn("profile_photos/", self.user.profile_photo.name)

    def test_dashboard_access_and_context(self):
        anonymous_response = self.client.get(reverse("core:dashboard_home"))
        self.assertEqual(anonymous_response.status_code, 302)

        self.client.login(username="normaluser", password="password123")
        non_staff_response = self.client.get(reverse("core:dashboard_home"))
        self.assertEqual(non_staff_response.status_code, 302)

        self.client.logout()
        self.client.login(username="staffuser", password="password123")
        staff_response = self.client.get(reverse("core:dashboard_home"))
        self.assertEqual(staff_response.status_code, 200)
        self.assertIn("stats", staff_response.context)
        self.assertIn("recent_posts", staff_response.context)
        self.assertIn("recent_comments", staff_response.context)
