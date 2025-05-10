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
        ('api', '0001_initial'),  # Replace with your last migration
    ]

    operations = [
        # We'll skip adding the field if it already exists
        # Instead, just update existing slugs and make them unique
        migrations.RunPython(generate_unique_slugs),
        migrations.AlterField(
            model_name='userprofile',
            name='slug',
            field=models.SlugField(blank=True, unique=True),
        ),
    ]
