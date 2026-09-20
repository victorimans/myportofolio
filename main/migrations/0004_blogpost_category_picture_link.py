from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("main", "0003_project"),
    ]

    operations = [
        migrations.AddField(
            model_name="blogpost",
            name="category",
            field=models.CharField(
                choices=[
                    ("ai", "AI"),
                    ("dsa", "DSA"),
                    ("web-development", "Web Development"),
                    ("career", "Career"),
                    ("personal", "Personal"),
                ],
                default="ai",
                max_length=30,
            ),
        ),
        migrations.AddField(
            model_name="blogpost",
            name="picture_link",
            field=models.URLField(blank=True, null=True),
        ),
    ]
