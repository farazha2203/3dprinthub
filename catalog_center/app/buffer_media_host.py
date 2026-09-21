from __future__ import annotations

import hashlib
import json
import re
import shutil
import subprocess
from pathlib import Path, PurePosixPath
from typing import Any
from urllib import request as urllib_request


DEFAULT_BRANCH = "social-assets-buffer"
DEFAULT_HOST = "github_raw"


def _setting(db, key: str, default: str) -> str:
    if not hasattr(db, "setting"):
        return default
    return str(db.setting(key, default) or default).strip()


def _run_git(repo: Path, args: list[str], *, check: bool = True, timeout: int = 60):
    result = subprocess.run(
        ["git", "-C", str(repo), *args],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=timeout,
    )
    if check and result.returncode != 0:
        detail = (result.stderr or result.stdout or "git command failed").strip()[-1200:]
        raise RuntimeError(f"Buffer media Git operation failed: {detail}")
    return result


def _github_identity(origin: str) -> tuple[str, str]:
    value = str(origin or "").strip()
    match = re.search(
        r"github\.com(?::|/)([^/]+)/([^/?#]+?)(?:\.git)?$",
        value,
        re.IGNORECASE,
    )
    if not match:
        raise RuntimeError("Buffer GitHub media host requires a GitHub origin.")
    owner = match.group(1).strip()
    repo = match.group(2).strip()
    if not owner or not repo:
        raise RuntimeError("Could not resolve GitHub repository identity.")
    return owner, repo


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _verify_public_image(url: str, timeout: int = 20) -> None:
    req = urllib_request.Request(
        url,
        method="HEAD",
        headers={"User-Agent": "3DPrintHub-BufferMedia/1.0"},
    )
    with urllib_request.urlopen(req, timeout=max(10, int(timeout))) as response:
        status = int(getattr(response, "status", 0) or 0)
        content_type = str(response.headers.get("Content-Type") or "").lower()
        if status not in {200, 206} or not content_type.startswith("image/"):
            raise RuntimeError(
                f"Buffer media host verification failed: HTTP {status} {content_type}"
            )


def _registered_worktree_for_branch(repo_root: Path, branch: str) -> Path | None:
    result = _run_git(
        repo_root,
        ["worktree", "list", "--porcelain"],
        check=False,
    )
    if result.returncode != 0:
        return None

    wanted = f"refs/heads/{branch}"
    current: Path | None = None
    for raw in str(result.stdout or "").splitlines():
        line = raw.strip()
        if line.startswith("worktree "):
            value = line.split(" ", 1)[1].strip()
            current = Path(value).expanduser().resolve() if value else None
            continue
        if line.startswith("branch ") and current is not None:
            ref = line.split(" ", 1)[1].strip()
            if ref == wanted and current.exists():
                return current
    return None


def _ensure_worktree(repo_root: Path, worktree: Path, branch: str) -> Path:
    def validate(candidate: Path) -> Path:
        probe = _run_git(candidate, ["rev-parse", "--is-inside-work-tree"])
        if probe.stdout.strip().lower() != "true":
            raise RuntimeError(f"Buffer media worktree is invalid: {candidate}")
        active = _run_git(candidate, ["branch", "--show-current"]).stdout.strip()
        if active != branch:
            raise RuntimeError(
                f"Buffer media worktree branch mismatch: expected {branch}, got {active or '(detached)'}"
            )
        return candidate

    if worktree.exists():
        return validate(worktree)

    registered = _registered_worktree_for_branch(repo_root, branch)
    if registered is not None:
        return validate(registered)

    worktree.parent.mkdir(parents=True, exist_ok=True)
    local = _run_git(
        repo_root,
        ["show-ref", "--verify", "--quiet", f"refs/heads/{branch}"],
        check=False,
    )
    if local.returncode == 0:
        _run_git(repo_root, ["worktree", "add", str(worktree), branch], timeout=90)
        return validate(worktree)

    remote = _run_git(
        repo_root,
        ["ls-remote", "--exit-code", "origin", f"refs/heads/{branch}"],
        check=False,
        timeout=45,
    )
    if remote.returncode == 0:
        _run_git(repo_root, ["fetch", "--no-tags", "origin", f"refs/heads/{branch}"], timeout=90)
        _run_git(repo_root, ["branch", branch, "FETCH_HEAD"])
        _run_git(repo_root, ["worktree", "add", str(worktree), branch], timeout=90)
        return validate(worktree)

    _run_git(repo_root, ["worktree", "add", "-b", branch, str(worktree), "HEAD"], timeout=90)
    return validate(worktree)


def rehost_buffer_assets(
    db,
    product_id: int,
    feed_meta: dict[str, Any],
    story_meta: dict[str, Any] | None = None,
    *,
    timeout: int = 25,
) -> dict[str, Any]:
    """Return provider-compatible media URLs without changing canonical Site media.

    Site mode keeps existing 3DPrintHub media URLs. github_raw mirrors only
    generated social derivatives into a dedicated public Git branch/worktree.
    Product media, SEO filenames and Site database rows remain untouched.
    """

    host = _setting(db, "buffer_media_host", DEFAULT_HOST).lower()
    feed_urls = [str(value or "").strip() for value in feed_meta.get("urls") or []]
    feed_local = [Path(str(value)).resolve() for value in feed_meta.get("local_paths") or []]
    story_url = str((story_meta or {}).get("url") or "").strip()
    story_local_value = str((story_meta or {}).get("local_path") or "").strip()

    if host == "site":
        return {
            "host": "site",
            "feed_urls": feed_urls,
            "story_url": story_url,
            "source_feed_urls": list(feed_meta.get("source_urls") or []),
            "commit_sha": "",
        }
    if host != "github_raw":
        raise RuntimeError(f"Unsupported Buffer media host: {host}")
    if not feed_local or len(feed_local) != len(feed_urls):
        raise RuntimeError("Buffer GitHub media host requires every generated feed file locally.")
    for path in feed_local:
        if not path.is_file() or path.suffix.lower() != ".png":
            raise RuntimeError(f"Buffer feed derivative is missing or not PNG: {path}")
    story_local = Path(story_local_value).resolve() if story_local_value else None
    if story_meta is not None and (story_local is None or not story_local.is_file()):
        raise RuntimeError("Buffer Story derivative is missing locally.")

    repo_root_value = _setting(db, "buffer_github_repo_root", "")
    repo_root = (
        Path(repo_root_value).expanduser().resolve()
        if repo_root_value
        else Path(__file__).resolve().parents[2]
    )
    if not (repo_root / ".git").exists():
        probe = _run_git(repo_root, ["rev-parse", "--show-toplevel"], check=False)
        if probe.returncode != 0:
            raise RuntimeError(f"Buffer GitHub repository root is invalid: {repo_root}")

    branch = _setting(db, "buffer_github_media_branch", DEFAULT_BRANCH)
    if not re.fullmatch(r"[A-Za-z0-9._/-]{1,120}", branch) or branch.startswith(("/", "-")):
        raise RuntimeError("Buffer GitHub media branch name is invalid.")

    origin = _run_git(repo_root, ["remote", "get-url", "origin"]).stdout.strip()
    owner, repo = _github_identity(origin)
    worktree_value = _setting(db, "buffer_github_media_worktree", "")
    worktree = (
        Path(worktree_value).expanduser().resolve()
        if worktree_value
        else (repo_root.parent / f"{repo_root.name}-social-assets").resolve()
    )
    worktree = _ensure_worktree(repo_root, worktree, branch)

    dirty = _run_git(worktree, ["status", "--porcelain", "--untracked-files=all"]).stdout.strip()
    if dirty:
        raise RuntimeError(
            "Buffer social-assets worktree is dirty; refusing to mix generated media with unrelated changes."
        )

    product_id = int(product_id)
    revision = str(feed_meta.get("revision") or (story_meta or {}).get("revision") or "").strip()
    if not revision or not re.fullmatch(r"[A-Za-z0-9._-]{4,80}", revision):
        raise RuntimeError("Buffer media revision key is missing or invalid.")

    relative_dir = PurePosixPath("social_media") / "instagram" / str(product_id) / revision
    target_dir = worktree / Path(*relative_dir.parts)
    target_dir.mkdir(parents=True, exist_ok=True)

    feed_names: list[str] = []
    for index, source in enumerate(feed_local, 1):
        name = f"feed-{index:02d}.png"
        shutil.copy2(source, target_dir / name)
        feed_names.append(name)
    if story_local is not None:
        shutil.copy2(story_local, target_dir / "story.png")

    row = dict(db.product(product_id) or {})
    manifest = {
        "product_id": product_id,
        "site_product_id": int(row.get("server_product_id") or 0),
        "site_revision": int(row.get("server_product_revision") or 0),
        "asset_revision": revision,
        "purpose": "Buffer public media compatibility",
        "source_media_urls": list(feed_meta.get("source_urls") or []),
        "feed_sha256": [_sha256(target_dir / name) for name in feed_names],
        "story_sha256": _sha256(target_dir / "story.png") if story_local is not None else "",
    }
    (target_dir / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    rel = relative_dir.as_posix()
    _run_git(worktree, ["add", "--", rel])
    changed = _run_git(worktree, ["diff", "--cached", "--quiet", "--", rel], check=False)
    if changed.returncode not in {0, 1}:
        raise RuntimeError("Could not inspect Buffer media staging state.")
    if changed.returncode == 1:
        _run_git(
            worktree,
            ["commit", "-m", f"assets: mirror product {product_id} revision {revision} for Buffer"],
            timeout=90,
        )
        _run_git(worktree, ["push", "origin", branch], timeout=120)

    head = _run_git(worktree, ["rev-parse", "HEAD"]).stdout.strip()
    remote = _run_git(
        worktree,
        ["ls-remote", "origin", f"refs/heads/{branch}"],
        timeout=45,
    ).stdout.strip().split()
    remote_sha = remote[0] if remote else ""
    if not head or remote_sha != head:
        raise RuntimeError("Buffer media branch is not synchronized with GitHub.")

    base = (
        f"https://raw.githubusercontent.com/{owner}/{repo}/{branch}/"
        f"{relative_dir.as_posix()}"
    )
    provider_feed = [f"{base}/{name}" for name in feed_names]
    provider_story = f"{base}/story.png" if story_local is not None else story_url
    for url in [*provider_feed, *([provider_story] if provider_story else [])]:
        _verify_public_image(url, timeout=timeout)

    return {
        "host": "github_raw",
        "branch": branch,
        "commit_sha": head,
        "feed_urls": provider_feed,
        "story_url": provider_story,
        "source_feed_urls": list(feed_meta.get("source_urls") or []),
    }
