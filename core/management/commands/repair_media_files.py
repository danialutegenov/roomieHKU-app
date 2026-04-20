from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.core.management.base import BaseCommand

from core.models import Post, User

PLACEHOLDER_GIF = (
    b"GIF89a\x01\x00\x01\x00\x80\x00\x00\x00\x00\x00"
    b"\xff\xff\xff!\xf9\x04\x00\x00\x00\x00\x00,\x00\x00"
    b"\x00\x00\x01\x00\x01\x00\x00\x02\x02D\x01\x00;"
)


class Command(BaseCommand):
    help = "Repair missing uploaded media files referenced by users and posts."

    def handle(self, *args, **options):
        user_scanned, user_repaired = self._repair_queryset(
            queryset=User.objects.exclude(profile_photo__isnull=True).exclude(profile_photo=""),
            field_name="profile_photo",
        )
        post_scanned, post_repaired = self._repair_queryset(
            queryset=Post.objects.exclude(image_url=""),
            field_name="image_url",
        )

        total_scanned = user_scanned + post_scanned
        total_repaired = user_repaired + post_repaired
        self.stdout.write(
            self.style.SUCCESS(
                f"Scanned {total_scanned} media references; repaired {total_repaired} missing files."
            )
        )

    def _repair_queryset(self, queryset, field_name):
        scanned = 0
        repaired = 0

        for obj in queryset.only("id", field_name):
            value = str(getattr(obj, field_name) or "")
            if not value:
                continue

            scanned += 1

            # Keep direct external URLs untouched.
            if value.startswith(("http://", "https://")):
                continue

            if default_storage.exists(value):
                continue

            default_storage.save(value, ContentFile(PLACEHOLDER_GIF))
            repaired += 1

        return scanned, repaired
