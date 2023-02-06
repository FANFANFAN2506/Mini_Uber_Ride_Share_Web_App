# Generated by Django 4.1.5 on 2023-02-02 04:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("ride", "0009_alter_ride_vehicle_type"),
    ]

    operations = [
        migrations.AlterField(
            model_name="ride",
            name="vehicle_type",
            field=models.CharField(
                blank=True,
                choices=[("economy", "economy"), ("luxury", "luxury")],
                default="economy",
                help_text="Vehicle type",
                max_length=100,
            ),
        ),
    ]