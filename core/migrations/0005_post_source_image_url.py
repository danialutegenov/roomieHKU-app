from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0004_post_views_count"),
    ]

    operations = [
        migrations.AddField(
            model_name="post",
            name="source_image_url",
            field=models.URLField(
                blank=True,
                default="",
                help_text="Original remote image URL for imported listings",
                max_length=200,
            ),
        ),
    ]
