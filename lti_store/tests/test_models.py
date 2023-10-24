from unittest.mock import patch, call

from ddt import ddt, data
from Cryptodome.PublicKey import RSA
from django.core.exceptions import ValidationError
from django.test import TestCase
from lti_store.models import ExternalLtiConfiguration, LTIVersion, MESSAGES


@ddt
class LTIConfigurationTestCase(TestCase):

    REQUIRED_FIELDS = {
        "name": "Test Config",
        "slug": "test-config",
    }
    UUID4 = "test-uuid4"
    KEY_OBJ = RSA.generate(2048)
    PRIVATE_KEY = KEY_OBJ.exportKey().decode()
    PUBLIC_KEY = KEY_OBJ.publickey().exportKey().decode()
    PUBLIC_JWK = "test-public-jwk"

    def test_string_representation_of_model(self):
        config = ExternalLtiConfiguration.objects.create(**self.REQUIRED_FIELDS)
        self.assertEqual(
            str(config),
            f"<ExternalLtiConfiguration #1: {self.REQUIRED_FIELDS['slug']}>",
        )

    def test_1p1_missing_fields(self):
        """Test clean method on a LTI 1.1 configuration with missing fields."""
        with self.assertRaises(ValidationError) as exc:
            ExternalLtiConfiguration(
                **self.REQUIRED_FIELDS,
                version=LTIVersion.LTI_1P1,
            ).clean()

        self.assertEqual(
            str(exc.exception),
            str(
                {
                    "lti_1p1_launch_url": [MESSAGES["required"]],
                    "lti_1p1_client_key": [MESSAGES["required"]],
                    "lti_1p1_client_secret": [MESSAGES["required"]],
                },
            ),
        )

    def test_1p3_missing_private_key(self):
        """Test clean method on a LTI 1.3 configuration with missing private key."""
        with self.assertRaises(ValidationError) as exc:
            ExternalLtiConfiguration(
                **self.REQUIRED_FIELDS,
                version=LTIVersion.LTI_1P3,
                lti_1p3_tool_public_key=self.PUBLIC_KEY,
            ).clean()

        self.assertEqual(
            str(exc.exception),
            str(
                {
                    "lti_1p3_private_key": [MESSAGES["required"]],
                },
            ),
        )

    def test_1p3_invalid_private_key(self):
        """Test clean method on a LTI 1.3 configuration with invalid private key."""
        with self.assertRaises(ValidationError) as exc:
            ExternalLtiConfiguration(
                **self.REQUIRED_FIELDS,
                version=LTIVersion.LTI_1P3,
                lti_1p3_private_key="invalid-private-key",
                lti_1p3_tool_public_key=self.PUBLIC_KEY,
            ).full_clean()

        self.assertEqual(
            str(exc.exception),
            str(
                {
                    "lti_1p3_private_key": [MESSAGES["invalid_rsa_key"]],
                },
            ),
        )

    def test_1p3_invalid_tool_public_key(self):
        """Test clean method on a LTI 1.3 configuration with invalid tool public key."""
        with self.assertRaises(ValidationError) as exc:
            ExternalLtiConfiguration(
                **self.REQUIRED_FIELDS,
                version=LTIVersion.LTI_1P3,
                lti_1p3_private_key=self.PRIVATE_KEY,
                lti_1p3_tool_public_key="invalid-public-key",
            ).full_clean()

        self.assertEqual(
            str(exc.exception),
            str(
                {
                    "lti_1p3_tool_public_key": [MESSAGES["invalid_rsa_key"]],
                },
            ),
        )

    @data("invalid-redirect-uris", '{"test": "test"}')
    def test_1p3_invalid_redirect_uris(self, value):
        """Test clean method on a LTI 1.3 configuration with invalid redirect URIs."""
        with self.assertRaises(ValidationError) as exc:
            ExternalLtiConfiguration(
                **self.REQUIRED_FIELDS,
                version=LTIVersion.LTI_1P3,
                lti_1p3_private_key=self.PRIVATE_KEY,
                lti_1p3_tool_public_key=self.PUBLIC_KEY,
                lti_1p3_redirect_uris=value,
            ).full_clean()

        self.assertEqual(
            str(exc.exception),
            str(
                {
                    "lti_1p3_redirect_uris": [MESSAGES["invalid_list_field"]],
                },
            ),
        )

    def test_1p3_missing_public_key_and_keyset_url(self):
        """Test clean method on a LTI 1.3 configuration with missing public key or keyset URL."""
        with self.assertRaises(ValidationError) as exc:
            ExternalLtiConfiguration(
                **self.REQUIRED_FIELDS,
                version=LTIVersion.LTI_1P3,
                lti_1p3_private_key=self.PRIVATE_KEY,
            ).clean()

        self.assertEqual(
            str(exc.exception),
            str(
                {
                    "lti_1p3_tool_public_key": [MESSAGES["required_pubkey_or_keyset"]],
                    "lti_1p3_tool_keyset_url": [MESSAGES["required_pubkey_or_keyset"]],
                },
            ),
        )

    @patch("lti_store.models.json.loads")
    @patch.object(RSA, "import_key")
    @patch("lti_store.models.RSAKey")
    @patch("lti_store.models.jwk.KEYS")
    @patch("lti_store.models.uuid.uuid4")
    def test_1p3_save(
        self,
        uuid4_mock,
        keys_mock,
        rsakey_mock,
        rsa_import_key_mock,
        loads_mock,
    ):
        """Test save method on a LTI 1.3 configuration."""
        uuid4_mock.return_value = self.UUID4
        loads_mock.return_value = self.PUBLIC_JWK

        config = ExternalLtiConfiguration(
            **self.REQUIRED_FIELDS,
            version=LTIVersion.LTI_1P3,
            lti_1p3_private_key=self.PRIVATE_KEY,
            lti_1p3_tool_public_key=self.PUBLIC_KEY,
        )
        config.save()

        self.assertEqual(config.lti_1p3_client_id, self.UUID4)
        self.assertEqual(config.lti_1p3_private_key_id, self.UUID4)
        self.assertEqual(config.lti_1p3_public_jwk, self.PUBLIC_JWK)
        uuid4_mock.assert_has_calls([call(), call()])
        keys_mock.assert_called_once_with()
        rsa_import_key_mock.assert_called_once_with(self.PRIVATE_KEY)
        rsakey_mock.assert_called_once_with(kid=self.UUID4, key=rsa_import_key_mock())
        keys_mock().append.assert_called_once_with(rsakey_mock())
        keys_mock().dump_jwks.assert_called_once_with()
        loads_mock.assert_called_once_with(keys_mock().dump_jwks())
