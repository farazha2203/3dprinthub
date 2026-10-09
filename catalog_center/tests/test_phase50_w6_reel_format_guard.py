"""W6 after-acceptance Reel MIME-extension safety regression (no Buffer calls)."""
import unittest
from unittest.mock import patch

from app.buffer_publish import (
    BufferConfig,
    build_reel_handoff_input,
    prepare_reel_preview,
)


class ReelMediaFormatGuardTests(unittest.TestCase):
    def setUp(self):
        self.provider = patch(
            "app.buffer_publish.canonical_site_payload",
            return_value={
                "product_url": "https://3dprinthub.ir/store/product/little-ballerina/",
                "caption": "Preview only; not published.",
            },
        )
        self.mock_provider = self.provider.start()
        self.addCleanup(self.provider.stop)
        self.product = {"id": 536}
        self.channel = BufferConfig(channel_id="offline-fixture")

    def preview(self, url):
        return prepare_reel_preview(
            self.product, video_url=url, site_url="https://3dprinthub.ir"
        )

    def test_real_site_gif_cannot_be_prepared_as_reel(self):
        url = "https://3dprinthub.ir/media/store/products/videos/147/6f980225578d6afc.gif"
        with self.assertRaisesRegex(ValueError, "MP4 or MOV"):
            self.preview(url)
        self.mock_provider.assert_not_called()

    def test_webm_m4v_and_renamed_query_gif_fail_closed(self):
        for uri in (
            "https://3dprinthub.ir/media/clip.webm",
            "https://3dprinthub.ir/media/clip.m4v",
            "https://3dprinthub.ir/media/clip.gif?download=clip.mp4",
        ):
            with self.subTest(uri=uri):
                with self.assertRaisesRegex(ValueError, "MP4 or MOV"):
                    self.preview(uri)

    def test_draft_handoff_must_revalidate_and_reject_gif(self):
        crafted = {
            "status": "preview",
            "caption": "Safe preview",
            "video_url": "https://3dprinthub.ir/media/clip.gif",
        }
        with self.assertRaisesRegex(RuntimeError, "MP4 or MOV"):
            build_reel_handoff_input(crafted, self.channel, approved=True)

    def test_approved_signed_mp4_url_remains_supported(self):
        signed = "https://3dprinthub.ir/media/clip.MP4?signature=offlinefixture"
        draft = self.preview(signed)
        self.assertTrue(draft["requires_operator_approval"])
        self.assertEqual(draft["video_url"], signed)
        payload = build_reel_handoff_input(draft, self.channel, approved=True)
        self.assertEqual(payload["assets"][0]["video"]["url"], signed)
        self.assertTrue(payload["saveToDraft"])
        self.assertTrue(payload["needsApproval"])

    def test_mov_and_uppercase_suffix_remain_supported(self):
        for name in ("clip.mov", "clip.MOV"):
            draft = self.preview("https://3dprinthub.ir/media/" + name)
            self.assertEqual(draft["type"], "reel")
            self.assertEqual(
                build_reel_handoff_input(draft, self.channel, approved=True)
                ["metadata"]["instagram"]["type"], "reel",
            )

    def test_non_https_and_fake_host_stay_rejected(self):
        for url in ("C:/private/clip.mp4", "http://localhost/clip.mp4", "https:///clip.mp4"):
            with self.subTest(url=url):
                with self.assertRaisesRegex(ValueError, "public HTTPS"):
                    self.preview(url)

    def test_manual_approval_gate_still_takes_precedence(self):
        with self.assertRaisesRegex(RuntimeError, "explicit operator approval"):
            build_reel_handoff_input(
                {"status": "preview", "video_url": "https://site/clip.gif"},
                self.channel,
            )


if __name__ == "__main__":
    unittest.main()
