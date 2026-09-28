from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0004_blogpost_category_picture_link'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='project',
            name='starred_by',
            field=models.ManyToManyField(blank=True, related_name='starred_projects', to=settings.AUTH_USER_MODEL),
        ),
    ]
