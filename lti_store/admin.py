from django.contrib import admin

from .models import ExternalLtiConfiguration
from .apps import LtiStoreConfig as App


class LtiConfigurationAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "version", "filter_key")
    list_filter = ("version",)
    prepopulated_fields = {"slug": ("name",)}

    def filter_key(self, obj):
        return f"{App.name}:{obj.slug}"


admin.site.register(ExternalLtiConfiguration, LtiConfigurationAdmin)
