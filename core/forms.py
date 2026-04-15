from django import forms
from django.contrib.auth.forms import UserCreationForm

from .models import Post, User


class SignupForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("username", "email", "password1", "password2")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["email"].required = True


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = (
            "title",
            "description",
            "image_url",
            "listing_type",
            "location",
            "price",
            "move_in_date",
            "gender_preference",
            "lifestyle_notes",
        )
        widgets = {
            "move_in_date": forms.DateInput(attrs={"type": "date"}),
            "image_url": forms.ClearableFileInput(attrs={"accept": "image/*"}),
        }


class ProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ("email", "bio", "phone_number", "profile_photo")
        widgets = {
            "profile_photo": forms.ClearableFileInput(attrs={"accept": "image/*"}),
        }


class ListingFilterForm(forms.Form):
    SORT_CHOICES = [
        ("newest", "Newest"),
        ("popular", "Most Popular"),
    ]

    q = forms.CharField(required=False, label="Keyword")
    listing_type = forms.ChoiceField(
        required=False,
        choices=[("", "All Types"), *Post.LISTING_TYPE_CHOICES],
    )
    location = forms.CharField(required=False)
    min_price = forms.DecimalField(required=False, min_value=0)
    max_price = forms.DecimalField(required=False, min_value=0)
    sort_by = forms.ChoiceField(required=False, choices=SORT_CHOICES, initial="newest")

    def clean(self):
        cleaned_data = super().clean()
        min_price = cleaned_data.get("min_price")
        max_price = cleaned_data.get("max_price")
        if min_price is not None and max_price is not None and min_price > max_price:
            raise forms.ValidationError("Maximum price must be greater than or equal to minimum price.")
        return cleaned_data


class CommentCreateForm(forms.Form):
    content = forms.CharField(widget=forms.Textarea(attrs={"rows": 3}), max_length=2000)
