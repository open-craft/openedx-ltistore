import uuid
import json

from Cryptodome.PublicKey import RSA
from jwkest import jwk
from jwkest.jwk import RSAKey
from django.db import models
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

MESSAGES = {
    "required": _("This field is required."),
    "required_pubkey_or_keyset": _("LTI 1.3 requires either a public key or a keyset URL."),
    "invalid_rsa_key": _("Invalid RSA key format."),
    "invalid_list_field": _('Should be a list (Example: ["id-1", "id-2", ...]).'),
}


def validate_rsa_key(key):
    """Validate RSA key format."""
    try:
        RSA.import_key(key)
    except ValueError:
        raise ValidationError(MESSAGES["invalid_rsa_key"])

    return key


def validate_list_field(string):
    """Validate list field format."""
    try:
        deserialized = json.loads(string)
    except ValueError:
        raise ValidationError(MESSAGES["invalid_list_field"])

    if not isinstance(deserialized, list):
        raise ValidationError(MESSAGES["invalid_list_field"])


class LTIVersion(models.TextChoices):
    LTI_1P1 = "lti_1p1", _("LTI 1.1")
    LTI_1P3 = "lti_1p3", _("LTI 1.3")


class LTIAdvantageAGS(models.TextChoices):
    DISABLED = "disabled", _("Disabled")
    DECLARATIVE = "declarative", _("Allow tools to submit grades only (declarative)")
    PROGRAMMATIC = "programmatic", _("Allow tools to manage and submit grade (programmatic)")


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

    # LTI 1.3 Related variables
    lti_1p3_client_id = models.CharField(
        "LTI 1.3 Client ID",
        max_length=255,
        blank=True,
        help_text=_("Client ID used by LTI tool"),
    )
    lti_1p3_deployment_id = models.CharField(
        "LTI 1.3 Deployment ID",
        max_length=255,
        blank=True,
        help_text=_("Deployment ID used by LTI tool"),
    )
    lti_1p3_oidc_url = models.URLField(
        "LTI 1.3 OIDC URL",
        max_length=255,
        blank=True,
        help_text=_("""This is the OIDC third-party initiated login endpoint URL in the LTI 1.3 flow,
        which should be provided by the LTI Tool."""),
    )
    lti_1p3_launch_url = models.URLField(
        "LTI 1.3 Launch URL",
        max_length=255,
        blank=True,
        help_text=_("""This is the LTI launch URL, otherwise known as the target_link_uri.
        It represents the LTI resource to launch to or load in the second leg of the launch flow,
        when the resource is actually launched or loaded."""),
    )
    lti_1p3_private_key = models.TextField(
        "LTI 1.3 Private Key",
        blank=True,
        help_text=_("Platform's generated Private key. Keep this value secret."),
        validators=[validate_rsa_key],
    )
    lti_1p3_private_key_id = models.CharField(
        "LTI 1.3 Private Key ID",
        max_length=255,
        blank=True,
        help_text=_("Platform's generated Private key ID"),
    )
    lti_1p3_tool_public_key = models.TextField(
        "LTI 1.3 Tool Public Key",
        blank=True,
        help_text=_("""This is the LTI Tool's public key.
        This should be provided by the LTI Tool.
        One of either lti_1p3_tool_public_key or
        lti_1p3_tool_keyset_url must not be blank."""),
        validators=[validate_rsa_key],
    )
    lti_1p3_tool_keyset_url = models.URLField(
        "LTI 1.3 Tool Keyset URL",
        max_length=255,
        blank=True,
        help_text=_("""This is the LTI Tool's JWK (JSON Web Key)
        Keyset (JWKS) URL. This should be provided by the LTI
        Tool. One of either lti_1p3_tool_public_key or
        lti_1p3_tool_keyset_url must not be blank."""),
    )
    lti_1p3_redirect_uris = models.TextField(
        "LTI 1.3 Redirect URIs",
        default=list,
        blank=True,
        help_text=_("""Valid urls the Tool may request us to redirect the id token to.
        The redirect uris are often the same as the launch url/deep linking url so if
        this field is empty, it will use them as the default. If you need to use different
        redirect uri's, enter them here. If you use this field you must enter all valid
        redirect uri's the tool may request."""),
        validators=[validate_list_field],
    )
    lti_1p3_public_jwk = models.JSONField(
        "LTI 1.3 Public JWK",
        default=dict,
        blank=True,
        editable=False,
        help_text=_("Platform's generated JWK keyset."),
    )

    # LTI 1.3 Advantage Related Variables
    lti_advantage_enable_nrps = models.BooleanField(
        "Enable LTI Advantage Names and Role Provisioning Services",
        default=False,
        help_text=_("Enable LTI Advantage Names and Role Provisioning Services."),
    )
    lti_advantage_deep_linking_enabled = models.BooleanField(
        "Enable LTI Advantage Deep Linking",
        default=False,
        help_text=_("Enable LTI Advantage Deep Linking."),
    )
    lti_advantage_deep_linking_launch_url = models.URLField(
        "LTI Advantage Deep Linking launch URL",
        max_length=255,
        blank=True,
        help_text=_("""This is the LTI Advantage Deep Linking launch URL. If the LTI Tool
        does not provide one, use the same value as lti_1p3_launch_url."""),
    )
    lti_advantage_ags_mode = models.CharField(
        "LTI Advantage Assignment and Grade Services Mode",
        max_length=20,
        choices=LTIAdvantageAGS.choices,
        default=LTIAdvantageAGS.DECLARATIVE,
        help_text=_("""Enable LTI Advantage Assignment and Grade Services and select the functionality
        enabled for LTI tools. The "declarative" mode (default) will provide a tool with a LineItem
        created from the XBlock settings, while the "programmatic" one will allow tools to manage,
        create and link the grades.""")
    )

    def __str__(self):
        return f"<ExternalLtiConfiguration #{self.id}: {self.slug}>"

    def clean(self):
        validation_errors = {}

        if self.version == LTIVersion.LTI_1P1:
            for field in [
                "lti_1p1_launch_url",
                "lti_1p1_client_key",
                "lti_1p1_client_secret",
            ]:
                # Raise ValidationError exception for any missing LTI 1.1 field.
                if not getattr(self, field):
                    validation_errors.update({field: _(MESSAGES["required"])})

        if self.version == LTIVersion.LTI_1P3:
            if not self.lti_1p3_private_key:
                # Raise ValidationError if private key is missing.
                validation_errors.update(
                    {"lti_1p3_private_key": _(MESSAGES["required"])},
                )
            if not self.lti_1p3_tool_public_key and not self.lti_1p3_tool_keyset_url:
                # Raise ValidationError if public key and keyset URL are missing.
                validation_errors.update({
                    "lti_1p3_tool_public_key": MESSAGES["required_pubkey_or_keyset"],
                    "lti_1p3_tool_keyset_url": MESSAGES["required_pubkey_or_keyset"],
                })

        if validation_errors:
            raise ValidationError(validation_errors)

    def save(self, *args, **kwargs):
        if self.version == LTIVersion.LTI_1P3:
            # Generate client ID or private key ID if missing.
            if not self.lti_1p3_client_id:
                self.lti_1p3_client_id = str(uuid.uuid4())
            if not self.lti_1p3_private_key_id:
                self.lti_1p3_private_key_id = str(uuid.uuid4())

            # Regenerate public JWK.
            public_keys = jwk.KEYS()
            public_keys.append(RSAKey(
                kid=self.lti_1p3_private_key_id,
                key=RSA.import_key(self.lti_1p3_private_key),
            ))
            self.lti_1p3_public_jwk = json.loads(public_keys.dump_jwks())

        super().save(*args, **kwargs)
