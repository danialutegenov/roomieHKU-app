from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import FileExtensionValidator
from django.core.validators import MinValueValidator


class User(AbstractUser):
    """
    Custom User model extending Django's AbstractUser.
    Satisfies Core Requirement: Unique usernames (built-in).
    """
    # For contact purposes (Optional as per diagram)
    email = models.EmailField("Email for contact", max_length=255)
    phone_number = models.CharField(
        max_length=20,
        blank=True,
        default="",
        help_text="Contact number for interested parties"
    )

    # User profile details
    bio = models.TextField(blank=True)
    profile_photo = models.FileField(
        upload_to="profile_photos/",
        null=True,
        blank=True,
        validators=[FileExtensionValidator(allowed_extensions=["jpg", "jpeg", "png", "gif", "webp"])],
    )
    
    # Admin moderation
    is_suspended = models.BooleanField(default=False)
    suspended_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.username


class Post(models.Model):
    """
    Main entity for housing/roommate listings.
    Maps exactly to the POST table in the ER diagram.
    """
    LISTING_TYPE_CHOICES = [
        ('Apartment', 'Apartment'),
        ('Dorm', 'Dorm'),
        ('Roommate', 'Roommate Request'),
    ]

    GENDER_PREF_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('N', 'No preference'),
    ]

    # Core identification & visual representation
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts')
    title = models.CharField(max_length=200)
    description = models.TextField()
    image_url = models.FileField(
        upload_to="listing_images/",
        help_text="Upload listing image",
        validators=[FileExtensionValidator(allowed_extensions=["jpg", "jpeg", "png", "gif", "webp"])],
    )

    # RoomieHKU Business Logic
    listing_type = models.CharField(max_length=20, choices=LISTING_TYPE_CHOICES)
    location = models.CharField(max_length=100, db_index=True, help_text="e.g., Kennedy Town")
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        help_text="Rent or Budget"
    )

    # Availability & Compatibility
    move_in_date = models.DateField(null=True, blank=True)
    gender_preference = models.CharField(
        max_length=1,
        choices=GENDER_PREF_CHOICES,
        default='N'
    )
    lifestyle_notes = models.TextField(blank=True, help_text="For roommate matching")

    # Optimization: Denormalized for popularity sorting
    likes_count = models.PositiveIntegerField(default=0)

    # Core Feature: Timestamp
    is_hidden = models.BooleanField(default=False)
    hidden_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']  # Default sorting: newest first
        indexes = [
            models.Index(fields=['listing_type']),
            models.Index(fields=['created_at']),
        ]
        constraints = [
            models.CheckConstraint(
                condition=models.Q(price__gte=0),
                name='post_price_gte_0'
            ),
        ]
    def __str__(self):
        return f"{self.listing_type}: {self.title}"


class Comment(models.Model):
    """
    Maps to the COMMENT table in the ER diagram.
    Allows user interaction on posts.
    """
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comment by {self.author.username} on {self.post.title}"


class Like(models.Model):
    """
    Maps to the LIKE table in the ER diagram.
    Facilitates the 'Like/Unlike' functionality.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='likes')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        # Prevents a single user from liking the same post multiple times
        constraints = [
            models.UniqueConstraint(fields=['user', 'post'], name='unique_like_user_post'),
        ]


class SavedListing(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="saved_items")
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="saved_by")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["user", "post"], name="unique_savedlisting_user_post"),
        ]
