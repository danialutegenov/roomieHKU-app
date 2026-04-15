from decimal import Decimal

from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.db import IntegrityError
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

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
        self.author.profile_photo.save("author-avatar.gif", make_uploaded_image("author-avatar.gif"), save=True)
        self.author.refresh_from_db()
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
        self.author.profile_photo.save("author-avatar.gif", make_uploaded_image("author-avatar.gif"), save=True)
        self.author.refresh_from_db()
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

    def test_listing_detail_increments_views_count(self):
        self.assertEqual(self.post.views_count, 0)
        self.client.get(reverse("core:listing_detail", args=[self.post.pk]))
        self.post.refresh_from_db()
        self.assertEqual(self.post.views_count, 1)

    def test_feed_card_shows_author_image_and_timestamp(self):
        response = self.client.get(reverse("core:listing_list"))
        self.assertContains(response, self.author.username)
        self.assertContains(response, self.post.image_url.url)
        self.assertContains(response, self.author.profile_photo.url)
        rendered_timestamp = timezone.localtime(self.post.created_at).strftime("%Y-%m-%d %H:%M")
        self.assertContains(response, rendered_timestamp)

    def test_listing_detail_shows_author_profile_photo(self):
        response = self.client.get(reverse("core:listing_detail", args=[self.post.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.author.profile_photo.url)

    def test_anonymous_user_redirected_for_protected_routes(self):
        protected_routes = [
            reverse("core:listing_create"),
            reverse("core:listing_update", args=[self.post.pk]),
            reverse("core:listing_delete", args=[self.post.pk]),
            reverse("core:toggle_like", args=[self.post.pk]),
            reverse("core:toggle_save", args=[self.post.pk]),
            reverse("core:add_comment", args=[self.post.pk]),
            reverse("core:saved_listings"),
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

    def test_user_post_history_requires_login_and_scopes_to_current_user(self):
        anonymous_response = self.client.get(reverse("core:user_post_history"))
        self.assertEqual(anonymous_response.status_code, 302)
        self.assertTrue(anonymous_response.url.startswith(reverse("core:login")))

        other_post = Post.objects.create(
            author=self.other_user,
            title="Other User Post",
            description="Should not appear in author history",
            image_url=make_uploaded_image("history-other.gif"),
            listing_type="Dorm",
            location="Sai Ying Pun",
            price="6200.00",
        )

        self.client.login(username="author1", password="password123")
        history_response = self.client.get(reverse("core:user_post_history"))
        self.assertEqual(history_response.status_code, 200)
        post_ids = set(history_response.context["posts"].values_list("id", flat=True))
        self.assertEqual(post_ids, {self.post.id})
        self.assertNotIn(other_post.id, post_ids)

    def test_user_post_history_sort_by_popularity(self):
        second_post = Post.objects.create(
            author=self.author,
            title="Second Author Post",
            description="Second post for popularity sorting",
            image_url=make_uploaded_image("history-second.gif"),
            listing_type="Apartment",
            location="Kennedy Town",
            price="9800.00",
        )
        Like.objects.create(user=self.other_user, post=second_post)

        self.client.login(username="author1", password="password123")
        response = self.client.get(reverse("core:user_post_history"), {"sort_by": "popular"})
        ordered_ids = list(response.context["posts"].values_list("id", flat=True))
        self.assertEqual(ordered_ids[0], second_post.id)

    def test_saved_listings_requires_login_and_scopes_to_current_user(self):
        anonymous_response = self.client.get(reverse("core:saved_listings"))
        self.assertEqual(anonymous_response.status_code, 302)
        self.assertTrue(anonymous_response.url.startswith(reverse("core:login")))

        other_saved_post = Post.objects.create(
            author=self.author,
            title="Saved for another user",
            description="Should not appear in other user's saved page",
            image_url=make_uploaded_image("saved-other-user.gif"),
            listing_type="Dorm",
            location="Sai Ying Pun",
            price="6200.00",
        )
        hidden_saved_post = Post.objects.create(
            author=self.author,
            title="Hidden saved listing",
            description="Should not appear because listing is hidden",
            image_url=make_uploaded_image("saved-hidden.gif"),
            listing_type="Apartment",
            location="Kennedy Town",
            price="7300.00",
            is_hidden=True,
            hidden_at=timezone.now(),
        )

        SavedListing.objects.create(user=self.other_user, post=self.post)
        SavedListing.objects.create(user=self.other_user, post=hidden_saved_post)
        SavedListing.objects.create(user=self.author, post=other_saved_post)

        self.client.login(username="user2", password="password123")
        response = self.client.get(reverse("core:saved_listings"))
        self.assertEqual(response.status_code, 200)

        post_ids = set(response.context["posts"].values_list("id", flat=True))
        self.assertEqual(post_ids, {self.post.id})
        self.assertEqual(response.context["saved_count"], 1)

    def test_saved_listings_sort_by_popularity(self):
        second_saved_post = Post.objects.create(
            author=self.author,
            title="Second saved listing",
            description="Should rank first on popular sort",
            image_url=make_uploaded_image("saved-popular.gif"),
            listing_type="Apartment",
            location="Kennedy Town",
            price="9900.00",
        )
        fan = User.objects.create_user(
            username="savedfan",
            password="password123",
            email="savedfan@example.com",
        )

        SavedListing.objects.create(user=self.other_user, post=self.post)
        SavedListing.objects.create(user=self.other_user, post=second_saved_post)
        Like.objects.create(user=fan, post=second_saved_post)

        self.client.login(username="user2", password="password123")
        response = self.client.get(reverse("core:saved_listings"), {"sort_by": "popular"})
        ordered_ids = list(response.context["posts"].values_list("id", flat=True))
        self.assertEqual(ordered_ids[0], second_saved_post.id)


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

    def test_market_snapshot_aggregates_follow_filters(self):
        response = self.client.get(reverse("core:listing_list"), {"location": "Kennedy"})
        snapshot = response.context["market_snapshot"]
        self.assertEqual(snapshot["total_results"], 2)
        self.assertEqual(snapshot["min_price"], Decimal("5500"))
        self.assertEqual(snapshot["max_price"], Decimal("7000"))
        self.assertEqual(snapshot["avg_price"], Decimal("6250"))

    def test_sort_by_popularity_orders_feed(self):
        user_1 = User.objects.create_user(username="fan1", password="password123", email="fan1@example.com")
        user_2 = User.objects.create_user(username="fan2", password="password123", email="fan2@example.com")

        Like.objects.create(user=user_1, post=self.post_3)
        Like.objects.create(user=user_2, post=self.post_3)
        Like.objects.create(user=user_1, post=self.post_1)

        response = self.client.get(reverse("core:listing_list"), {"sort_by": "popular"})
        ordered_ids = list(response.context["posts"].values_list("id", flat=True))
        self.assertEqual(ordered_ids[0], self.post_3.id)


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
        self.comment = Comment.objects.create(post=self.post, author=self.user, content="Sample comment")
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

        page_response = self.client.get(reverse("core:profile_edit"))
        self.assertEqual(page_response.status_code, 200)
        self.assertContains(page_response, self.user.profile_photo.url)

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
        self.assertIn("location_demand", staff_response.context)
        self.assertIn("weekly_activity", staff_response.context)
        self.assertIn("top_viewed_listing", staff_response.context)
        self.assertEqual(staff_response.context["total_views"], 0)

        location_rows = list(staff_response.context["location_demand"])
        self.assertEqual(len(location_rows), 1)
        self.assertEqual(location_rows[0]["location"], "Pok Fu Lam")
        self.assertEqual(location_rows[0]["listing_count"], 1)

        weekly_rows = staff_response.context["weekly_activity"]
        self.assertEqual(len(weekly_rows), 8)
        self.assertEqual(sum(row["posts"] for row in weekly_rows), 1)
        self.assertEqual(sum(row["comments"] for row in weekly_rows), 1)
        self.assertEqual(sum(row["likes"] for row in weekly_rows), 1)

        top_viewed = staff_response.context["top_viewed_listing"]
        self.assertIsNotNone(top_viewed)
        self.assertEqual(top_viewed.pk, self.post.pk)

    def test_staff_moderation_actions(self):
        self.client.login(username="staffuser", password="password123")

        suspend_response = self.client.post(reverse("core:suspend_user", args=[self.user.pk]))
        self.assertRedirects(suspend_response, reverse("core:dashboard_home"))
        self.user.refresh_from_db()
        self.assertTrue(self.user.is_suspended)
        self.assertIsNotNone(self.user.suspended_at)

        reactivate_user_response = self.client.post(reverse("core:reactivate_user", args=[self.user.pk]))
        self.assertRedirects(reactivate_user_response, reverse("core:dashboard_home"))
        self.user.refresh_from_db()
        self.assertFalse(self.user.is_suspended)
        self.assertIsNone(self.user.suspended_at)

        hide_response = self.client.post(reverse("core:hide_listing", args=[self.post.pk]))
        self.assertRedirects(hide_response, reverse("core:dashboard_home"))
        self.post.refresh_from_db()
        self.assertTrue(self.post.is_hidden)
        self.assertIsNotNone(self.post.hidden_at)

        reactivate_listing_response = self.client.post(reverse("core:reactivate_listing", args=[self.post.pk]))
        self.assertRedirects(reactivate_listing_response, reverse("core:dashboard_home"))
        self.post.refresh_from_db()
        self.assertFalse(self.post.is_hidden)
        self.assertIsNone(self.post.hidden_at)

        delete_comment_response = self.client.post(
            reverse("core:dashboard_delete_comment", args=[self.comment.pk])
        )
        self.assertRedirects(delete_comment_response, reverse("core:dashboard_home"))
        self.assertFalse(Comment.objects.filter(pk=self.comment.pk).exists())

        delete_post = Post.objects.create(
            author=self.user,
            title="Dashboard Delete Post",
            description="To be deleted by staff",
            image_url=make_uploaded_image("dashboard-delete.gif"),
            listing_type="Dorm",
            location="Kennedy Town",
            price="5000.00",
        )
        delete_listing_response = self.client.post(reverse("core:delete_listing", args=[delete_post.pk]))
        self.assertRedirects(delete_listing_response, reverse("core:dashboard_home"))
        self.assertFalse(Post.objects.filter(pk=delete_post.pk).exists())

    def test_dashboard_moderation_requires_staff(self):
        self.client.login(username="normaluser", password="password123")
        moderation_routes = [
            reverse("core:suspend_user", args=[self.user.pk]),
            reverse("core:reactivate_user", args=[self.user.pk]),
            reverse("core:hide_listing", args=[self.post.pk]),
            reverse("core:reactivate_listing", args=[self.post.pk]),
            reverse("core:delete_listing", args=[self.post.pk]),
            reverse("core:dashboard_delete_comment", args=[self.comment.pk]),
        ]

        for route in moderation_routes:
            response = self.client.post(route)
            self.assertEqual(response.status_code, 302)
            self.assertTrue(response.url.startswith(reverse("admin:login")))

        self.user.refresh_from_db()
        self.post.refresh_from_db()
        self.assertFalse(self.user.is_suspended)
        self.assertFalse(self.post.is_hidden)
        self.assertTrue(Comment.objects.filter(pk=self.comment.pk).exists())
