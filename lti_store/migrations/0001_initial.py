# Generated by Django 3.2.12 on 2022-04-08 20:30

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="ExternalLtiConfiguration",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=80, unique=True)),
                ("slug", models.SlugField(max_length=80, unique=True)),
                ("description", models.TextField(blank=True, default="")),
                (
                    "version",
                    models.CharField(
                        choices=[("lti_1p1", "LTI 1.1"),],
                        default="lti_1p1",
                        max_length=10,
                    ),
                ),
                (
                    "lti_1p1_launch_url",
                    models.CharField(
                        blank=True,
                        help_text="The URL of the external tool that initiates the launch.",
                        max_length=255,
                    ),
                ),
                (
                    "lti_1p1_client_key",
                    models.CharField(
                        blank=True,
                        help_text="Client key provided by the LTI tool provider.",
                        max_length=255,
                    ),
                ),
                (
                    "lti_1p1_client_secret",
                    models.CharField(
                        blank=True,
                        help_text="Client secret provided by the LTI tool provider.",
                        max_length=255,
                    ),
                ),
            ],
        ),
    ]
