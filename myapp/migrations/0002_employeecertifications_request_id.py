# Generated by Django 5.1.4 on 2025-01-28 05:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='employeecertifications',
            name='request_id',
            field=models.CharField(max_length=100, null=True),
        ),
    ]
