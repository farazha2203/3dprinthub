from __future__ import annotations

from django.test import TestCase

from store.management.commands.phase34b_import_makerworld import (
    resolve_makerworld_source,
)
from store.models import CatalogSourcePolicy, PrintCatalogSource


class Phase34BSourceResolutionTests(TestCase):
    def test_seeded_custom_source_is_resolved_by_code(self):
        source = PrintCatalogSource.objects.get(code="makerworld")
        self.assertEqual(source.adapter_key, "custom")

        resolved_source, policy = resolve_makerworld_source()

        self.assertEqual(resolved_source.pk, source.pk)
        self.assertEqual(resolved_source.code, "makerworld")
        self.assertEqual(resolved_source.adapter_key, "custom")
        self.assertTrue(resolved_source.is_active)
        self.assertEqual(policy.source_kind, "makerworld")
        self.assertTrue(policy.is_active)

    def test_missing_source_and_policy_are_recreated(self):
        CatalogSourcePolicy.objects.filter(
            source__code="makerworld"
        ).delete()
        PrintCatalogSource.objects.filter(code="makerworld").delete()

        source, policy = resolve_makerworld_source()

        self.assertEqual(source.code, "makerworld")
        self.assertEqual(source.adapter_key, "custom")
        self.assertTrue(source.is_active)
        self.assertEqual(policy.source, source)
        self.assertEqual(policy.source_kind, "makerworld")
        self.assertTrue(policy.is_active)
