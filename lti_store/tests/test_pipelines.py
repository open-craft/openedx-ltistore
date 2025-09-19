from lti_store.pipelines import GetLtiConfigurations

from django.test import TestCase
from unittest.mock import Mock
from lti_store.models import ExternalLtiConfiguration
from lti_store.apps import LtiStoreConfig as App
from Cryptodome.PublicKey import RSA


class TestGetLtiConfigurations(TestCase):
    def setUp(self) -> None:
        super().setUp()
        pipeline = Mock("Pipeline")
        filter_type = "org.openedx.xblock.lti_consumer.configuration.listed.v1"
        self.filter_step = GetLtiConfigurations(filter_type, pipeline)

    def test_run_filter_returns_an_empty_list_when_there_are_no_configs(self):
        data = self.filter_step.run_filter({}, "", {})

        self.assertIn("configurations", data)
        self.assertIn("config_id", data)
        self.assertIn("context", data)

        self.assertEqual(data["configurations"], {})

    def test_run_filter_returns_a_single_extra_configuration_when_config_id_is_specified(
        self,
    ):
        first = ExternalLtiConfiguration.objects.create(name="Test", slug="test")
        self.assertEqual(first.id, 1)

        data = self.filter_step.run_filter({}, f"{App.name}:test", {})

        self.assertEqual(len(data["configurations"]), 1)
        self.assertIn(f"{App.name}:test", data["configurations"])
        self.assertEqual(data["configurations"][f"{App.name}:test"]["name"], "Test")
        first.delete()

    def test_filter_returns_configurations_unmodified_if_id_is_not_found(self):
        data = self.filter_step.run_filter({}, f"{App.name}:non-existant-config", {})

        self.assertSequenceEqual(data["configurations"], {})

    def test_filter_returns_all_the_available_configs_when_config_id_is_not_set(self):
        first = ExternalLtiConfiguration.objects.create(
            name="First Config", slug="first-config"
        )
        second = ExternalLtiConfiguration.objects.create(
            name="Second Config", slug="second-config"
        )
        self.assertEqual(first.id, 1)
        self.assertEqual(second.id, 2)

        data = self.filter_step.run_filter({}, "", {})

        self.assertEqual(len(data["configurations"]), 2)
        self.assertIn(f"{App.name}:first-config", data["configurations"])
        self.assertIn(f"{App.name}:second-config", data["configurations"])
        self.assertEqual(
            data["configurations"][f"{App.name}:first-config"]["name"], "First Config"
        )
        self.assertEqual(
            data["configurations"][f"{App.name}:second-config"]["name"], "Second Config"
        )
        first.delete()
        second.delete()

    def test_filter_includes_lti_1p3_public_jwk_field_in_serialized_config(self):
        # Generate a test RSA key pair
        key = RSA.generate(2048)
        private_key_pem = key.export_key().decode('utf-8')
        public_key_pem = key.publickey().export_key().decode('utf-8')

        lti_config = ExternalLtiConfiguration.objects.create(
            name="LTI 1.3 Config",
            slug="lti-1p3-config",
            version="lti_1p3",
            lti_1p3_private_key=private_key_pem,
            lti_1p3_tool_public_key=public_key_pem
        )

        data = self.filter_step.run_filter({}, f"{App.name}:lti-1p3-config", {})

        config_data = data["configurations"][f"{App.name}:lti-1p3-config"]
        self.assertIn("lti_1p3_public_jwk", config_data)

        jwk_data = config_data['lti_1p3_public_jwk']
        self.assertIsInstance(jwk_data, dict)
        assert "keys" in jwk_data
        assert jwk_data['keys'][0]['kid'] == lti_config.lti_1p3_private_key_id

        lti_config.delete()
