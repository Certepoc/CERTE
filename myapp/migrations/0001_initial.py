# Generated by Django 5.1.2 on 2024-12-19 08:36

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Voucher',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('certification_name', models.CharField(max_length=255)),
                ('voucher_code', models.CharField(max_length=100)),
                ('expiration_date', models.DateField()),
            ],
            options={
                'db_table': 'vouchers',
            },
        ),
    ]
