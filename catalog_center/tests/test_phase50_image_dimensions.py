import io

from PIL import Image

from app.phase49_3h_image_limits import install_workspace


class FakeLabel:
    def __init__(self):
        self.values = {}

    def configure(self, **kwargs):
        self.values.update(kwargs)


class FakeWorkspace:
    def _images_ui(self):
        return None

    def refetch(self):
        return None

    def reload(self):
        return None

    def _apply_thumbnail(self, label, raw):
        label.configure(image="thumbnail", text="")
        return "done"


def test_image_card_shows_original_pixel_dimensions():
    install_workspace(FakeWorkspace)
    image = Image.new("RGB", (1920, 1080), "white")
    buffer = io.BytesIO()
    image.save(buffer, format="PNG")

    label = FakeLabel()
    result = FakeWorkspace()._apply_thumbnail(label, buffer.getvalue())

    assert result == "done"
    assert label.values["text"] == "1920 × 1080 px"
    assert label.values["compound"] == "top"
