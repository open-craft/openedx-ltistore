from django.test import TestCase
from lti_store.models import ExternalLtiConfiguration, LTIVersion


class LTIConfigurationTestCase(TestCase):
    def test_string_representation_of_model(self):
        cfg = ExternalLtiConfiguration.objects.create(
            name="Test Config", slug="test-config"
        )
        self.assertEqual(str(cfg), "<ExternalLtiConfiguration #1: test-config>")
        cfg.delete()
