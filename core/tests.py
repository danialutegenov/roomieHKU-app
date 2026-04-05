from django.test import TestCase
from django.core.exceptions import ValidationError
from django.db import IntegrityError

from .models import User, Post, Like, SavedListing


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
            image_url="https://example.com/listing.jpg",
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
            image_url="https://example.com/invalid.jpg",
            listing_type="Roommate",
            location="Sai Ying Pun",
            price="-1.00",
        )
        with self.assertRaises(ValidationError):
            invalid_post.full_clean()
