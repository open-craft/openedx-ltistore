from lti_store.pipelines import GetLtiConfigurations

from django.test import TestCase
from unittest.mock import Mock
from lti_store.models import ExternalLtiConfiguration
from lti_store.apps import LtiStoreConfig as App


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
