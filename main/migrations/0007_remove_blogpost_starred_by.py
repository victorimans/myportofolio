from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0006_blogpost_starred_by'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='blogpost',
            name='starred_by',
        ),
    ]
