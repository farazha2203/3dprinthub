from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

from app.buffer_media_host import _ensure_worktree, _github_identity, rehost_buffer_assets


class _DB:
    def __init__(self, settings=None):
        self.settings = settings or {}

    def setting(self, key, default=""):
        return self.settings.get(key, default)

    def product(self, product_id):
        return {
            "id": int(product_id),
            "server_product_id": 39,
            "server_product_revision": 8,
        }


class BufferMediaHostTests(unittest.TestCase):
    def test_github_identity_accepts_https_and_ssh(self):
        self.assertEqual(
            _github_identity("https://github.com/farazha2203/3dprinthub.git"),
            ("farazha2203", "3dprinthub"),
        )
        self.assertEqual(
            _github_identity("git@github.com:farazha2203/3dprinthub.git"),
            ("farazha2203", "3dprinthub"),
        )

    def test_site_mode_preserves_generated_site_urls(self):
        db = _DB({"buffer_media_host": "site"})
        result = rehost_buffer_assets(
            db,
            625,
            {
                "urls": ["https://3dprinthub.ir/media/instagram/feed/a.png"],
                "source_urls": ["https://3dprinthub.ir/media/p/source.webp"],
            },
            {"url": "https://3dprinthub.ir/media/instagram/stories/a.png"},
        )
        self.assertEqual(result["host"], "site")
        self.assertEqual(
            result["feed_urls"],
            ["https://3dprinthub.ir/media/instagram/feed/a.png"],
        )

    @patch("app.buffer_media_host._run_git")
    def test_existing_registered_social_branch_worktree_is_reused(self, run_git):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "repo"
            preferred = Path(tmp) / "new-social-assets"
            registered = Path(tmp) / "existing-social-assets"
            root.mkdir()
            registered.mkdir()

            def git_result(repo, args, **kwargs):
                result = MagicMock()
                result.returncode = 0
                result.stderr = ""
                if args == ["worktree", "list", "--porcelain"]:
                    result.stdout = (
                        f"worktree {registered}\n"
                        "HEAD abc123\n"
                        "branch refs/heads/social-assets-buffer\n\n"
                    )
                elif args == ["rev-parse", "--is-inside-work-tree"]:
                    result.stdout = "true\n"
                elif args == ["branch", "--show-current"]:
                    result.stdout = "social-assets-buffer\n"
                else:
                    result.stdout = ""
                return result

            run_git.side_effect = git_result
            resolved = _ensure_worktree(
                root,
                preferred,
                "social-assets-buffer",
            )
            self.assertEqual(resolved, registered.resolve())
            self.assertFalse(
                any(
                    call.args[1][:2] == ["worktree", "add"]
                    for call in run_git.call_args_list
                )
            )

    @patch("app.buffer_media_host._verify_public_image")
    @patch("app.buffer_media_host._run_git")
    @patch("app.buffer_media_host._ensure_worktree")
    def test_github_raw_mode_uses_dedicated_branch_and_keeps_source_audit(
        self, ensure_worktree, run_git, verify_public
    ):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "repo"
            worktree = Path(tmp) / "repo-social-assets"
            root.mkdir()
            (root / ".git").mkdir()
            worktree.mkdir()
            ensure_worktree.return_value = worktree
            feed = Path(tmp) / "01.png"
            story = Path(tmp) / "story.png"
            feed.write_bytes(b"png-feed")
            story.write_bytes(b"png-story")
            db = _DB({
                "buffer_media_host": "github_raw",
                "buffer_github_repo_root": str(root),
                "buffer_github_media_worktree": str(worktree),
                "buffer_github_media_branch": "social-assets-buffer",
            })

            def git_result(repo, args, **kwargs):
                result = MagicMock()
                result.returncode = 0
                result.stderr = ""
                if args[:3] == ["remote", "get-url", "origin"]:
                    result.stdout = "https://github.com/farazha2203/3dprinthub.git\n"
                elif args[:2] == ["status", "--porcelain"]:
                    result.stdout = ""
                elif args[:3] == ["diff", "--cached", "--quiet"]:
                    result.returncode = 1
                    result.stdout = ""
                elif args[:2] == ["rev-parse", "HEAD"]:
                    result.stdout = "abc123\n"
                elif args[:2] == ["ls-remote", "origin"]:
                    result.stdout = "abc123\trefs/heads/social-assets-buffer\n"
                else:
                    result.stdout = ""
                return result

            run_git.side_effect = git_result
            result = rehost_buffer_assets(
                db,
                625,
                {
                    "urls": ["https://3dprinthub.ir/media/instagram/feed/a.png"],
                    "local_paths": [str(feed)],
                    "source_urls": ["https://3dprinthub.ir/media/p/source.webp"],
                    "revision": "rev12345",
                },
                {
                    "url": "https://3dprinthub.ir/media/instagram/stories/a.png",
                    "local_path": str(story),
                    "revision": "rev12345",
                },
            )

            self.assertEqual(result["host"], "github_raw")
            self.assertEqual(result["commit_sha"], "abc123")
            self.assertTrue(result["feed_urls"][0].startswith(
                "https://raw.githubusercontent.com/farazha2203/3dprinthub/social-assets-buffer/"
            ))
            self.assertTrue(result["story_url"].endswith("/story.png"))
            self.assertEqual(
                result["source_feed_urls"],
                ["https://3dprinthub.ir/media/p/source.webp"],
            )
            ensure_worktree.assert_called_once()
            self.assertGreaterEqual(verify_public.call_count, 2)
            self.assertTrue((worktree / "social_media/instagram/625/rev12345/feed-01.png").is_file())


if __name__ == "__main__":
    unittest.main()
