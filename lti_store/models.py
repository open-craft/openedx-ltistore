from django.db import models
from django.utils.translation import gettext_lazy as _


class LTIVersion(models.TextChoices):
    LTI_1P1 = "lti_1p1", _("LTI 1.1")


class ExternalLtiConfiguration(models.Model):

    name = models.CharField(max_length=80, unique=True)
    slug = models.SlugField(max_length=80, unique=True)
    description = models.TextField(blank=True, default="")

    version = models.CharField(
        max_length=10, choices=LTIVersion.choices, default=LTIVersion.LTI_1P1
    )

    # LTI 1.1 Related variables
    lti_1p1_launch_url = models.CharField(
        max_length=255,
        blank=True,
        help_text=_("The URL of the external tool that initiates the launch."),
    )
    lti_1p1_client_key = models.CharField(
        max_length=255,
        blank=True,
        help_text=_("Client key provided by the LTI tool provider."),
    )

    lti_1p1_client_secret = models.CharField(
        max_length=255,
        blank=True,
        help_text=_("Client secret provided by the LTI tool provider."),
    )

    def __str__(self):
        return f"<ExternalLtiConfiguration #{self.id}: {self.slug}>"
