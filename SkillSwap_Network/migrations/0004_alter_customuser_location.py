# Generated by Django 5.2.1 on 2025-06-06 09:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("SkillSwap_Network", "0003_alter_customuser_bio"),
    ]

    operations = [
        migrations.AlterField(
            model_name="customuser",
            name="location",
            field=models.CharField(max_length=200),
        ),
    ]
