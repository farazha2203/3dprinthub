from __future__ import annotations

from .epic49_product_studio import (
    LICENSE_CODE_TO_LABEL,
    LICENSE_LABEL_TO_CODE,
    ProductStudio as EditableProductStudio,
)


class ProductStudio(EditableProductStudio):
    """Final Epic49 studio with two-way license synchronization."""

    def _reconcile_license_controls(self) -> str:
        if not hasattr(self, "publish_license_label_var"):
            return self.license_var.get() or "review"

        row = self.db.product(self.product_id)
        database_code = (row["commercial_status"] if row is not None else "review") or "review"
        quick_code = self.license_var.get() or database_code
        publish_code = LICENSE_LABEL_TO_CODE.get(
            self.publish_license_label_var.get(), database_code
        )

        if quick_code == publish_code:
            chosen = quick_code
        elif quick_code != database_code and publish_code == database_code:
            # User changed the quick-publish combobox.
            chosen = quick_code
        elif publish_code != database_code and quick_code == database_code:
            # User changed the dedicated Publish tab combobox.
            chosen = publish_code
        else:
            # Both controls were edited; the quick control is the last independent
            # value because Publish-tab changes already synchronize both controls.
            chosen = quick_code

        if chosen not in LICENSE_CODE_TO_LABEL:
            chosen = "review"
        self.license_var.set(chosen)
        self.publish_license_label_var.set(LICENSE_CODE_TO_LABEL[chosen])
        return chosen

    def save(self, silent=False):
        self._reconcile_license_controls()
        return super().save(silent=silent)
