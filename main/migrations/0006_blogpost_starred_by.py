from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0005_project_starred_by'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='blogpost',
            name='starred_by',
            field=models.ManyToManyField(blank=True, related_name='starred_blog_posts', to=settings.AUTH_USER_MODEL),
        ),
    ]
