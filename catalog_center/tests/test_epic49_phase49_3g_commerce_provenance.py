from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MODULE = ROOT / "app" / "phase49_3g_commerce_provenance.py"
LAUNCHER = ROOT / "launch.py"


class Phase493GCommerceProvenanceContractTests(unittest.TestCase):
    def test_commerce_page_exposes_material_ai_ownership_controls(self):
        source = MODULE.read_text(encoding="utf-8")
        self.assertIn("مالکیت AI در سفارش و قیمت", source)
        self.assertIn('MATERIAL_GROUP = "materials"', source)
        self.assertIn("خاموش/روشن AI", source)
        self.assertIn("اجازه بازنویسی AI", source)

    def test_pricing_and_commercial_approval_remain_operator_owned(self):
        source = MODULE.read_text(encoding="utf-8")
        self.assertIn("قیمت قطعی", source)
        self.assertIn("تأیید فروش", source)
        self.assertIn("مجوز", source)
        self.assertIn("Production", source)
        self.assertNotIn("final_price_var.set", source)
        self.assertNotIn("approved_var.set", source)
        self.assertNotIn("license_var.set", source)

    def test_launcher_installs_commerce_provenance_after_main_3g_workspace(self):
        launcher = LAUNCHER.read_text(encoding="utf-8")
        main_call = "install_phase49_3g_workspace(ProductWorkspace, readiness_module)"
        commerce_call = "install_phase49_3g_commerce_provenance(ProductWorkspace)"
        self.assertIn(main_call, launcher)
        self.assertIn(commerce_call, launcher)
        self.assertLess(launcher.index(main_call), launcher.index(commerce_call))
        self.assertIn("EPIC49_3G_COMMERCE_PROVENANCE=ENABLED", launcher)


if __name__ == "__main__":
    unittest.main()
