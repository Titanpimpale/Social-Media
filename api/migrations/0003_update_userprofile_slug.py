from django.db import migrations, models

import uuid
from django.utils.text import slugify

def generate_unique_slugs(apps, schema_editor):
    UserProfile = apps.get_model('api', 'UserProfile')
    for profile in UserProfile.objects.all():
        if not profile.slug:  # Only update profiles without a slug
            base_slug = slugify(profile.user.username)
            unique_id = str(uuid.uuid4())[:8]
            profile.slug = f"{base_slug}-{unique_id}"
            profile.save()

class Migration(migrations.Migration):

    dependencies = [
        ('api', '0002_add_slug_to_userprofile'),  # Make sure this points to your last migration
    ]

    operations = [
        migrations.RunPython(generate_unique_slugs),
        migrations.AlterField(
            model_name='userprofile',
            name='slug',
            field=models.SlugField(blank=True, unique=True),
        ),
    ]