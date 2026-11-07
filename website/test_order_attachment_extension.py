from django.test import SimpleTestCase

from website.models import OrderAttachment


class OrderAttachmentExtensionTests(SimpleTestCase):
    def test_original_filename_extension_is_normalized_and_classified(self):
        image = OrderAttachment(original_name="Reference.PnG")
        pdf = OrderAttachment(original_name="drawing.PDF")
        unknown = OrderAttachment(original_name="model.STL")

        self.assertEqual(image.extension, ".png")
        self.assertTrue(image.is_image)
        self.assertTrue(image.is_previewable)

        self.assertEqual(pdf.extension, ".pdf")
        self.assertTrue(pdf.is_pdf)
        self.assertTrue(pdf.is_previewable)

        self.assertEqual(unknown.extension, ".stl")
        self.assertFalse(unknown.is_image)
        self.assertFalse(unknown.is_pdf)
        self.assertFalse(unknown.is_previewable)

    def test_stored_filename_is_used_when_original_name_is_empty(self):
        attachment = OrderAttachment(original_name="")
        attachment.file.name = "order-attachments/2026/11/reference.WEBP"

        self.assertEqual(attachment.extension, ".webp")
        self.assertTrue(attachment.is_image)
