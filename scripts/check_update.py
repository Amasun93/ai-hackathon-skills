"""Read-only update and package check. Python 3.9+, standard library only."""
import argparse
import hashlib
import json
import re
import subprocess
import urllib.request
from pathlib import Path, PurePosixPath

REPO = "Amasun93/ai-hackathon-skills"
VERSION = re.compile(r"\d+\.\d+\.\d+\Z")


def digest(path):
    # This package contains text only; Git can change CRLF/LF on checkout.
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest()


def version_of(root):
    text = (root / "SKILL.md").read_text(encoding="utf-8-sig")
    match = re.search(r'^\s+version:\s*["\']?(\d+\.\d+\.\d+)["\']?\s*$', text, re.M)
    if not match:
        raise ValueError("SKILL.md has no supported version")
    return match.group(1)


def validate_manifest(manifest):
    if (manifest.get("schema") != 1 or manifest.get("repository") != REPO
            or manifest.get("hash_mode") != "sha256-lf"
            or not VERSION.fullmatch(str(manifest.get("version", "")))):
        raise ValueError("Invalid manifest identity or version")
    files = manifest.get("files")
    if not isinstance(files, dict) or not {"SKILL.md", "CHANGELOG.md", "references/update.md"} <= files.keys():
        raise ValueError("Manifest is missing required entries")
    for name, value in files.items():
        p = PurePosixPath(name)
        if (not name or p.is_absolute() or ".." in p.parts or "\\" in name
                or ":" in name or str(p) != name or name == "update-manifest.json"
                or not re.fullmatch(r"[a-f0-9]{64}", str(value))):
            raise ValueError("Invalid manifest file entry")
    return manifest


def check_files(root, manifest):
    problems = []
    for name, expected in manifest["files"].items():
        path = root / name
        if not path.resolve().is_relative_to(root):
            problems.append({"file": name, "issue": "outside_skill"})
        elif not path.is_file():
            problems.append({"file": name, "issue": "missing"})
        elif digest(path) != expected:
            problems.append({"file": name, "issue": "modified"})
    for path in root.rglob("*"):
        rel = path.relative_to(root)
        if {".git", "__pycache__"} & set(rel.parts) or not path.is_file():
            continue
        if rel.as_posix() not in manifest["files"] and rel.as_posix() != "update-manifest.json":
            problems.append({"file": rel.as_posix(), "issue": "extra"})
    return problems


def git_state(root):
    def git(*args):
        return subprocess.run(["git", "--no-optional-locks", "-C", str(root), *args],
                              capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=8)
    try:
        top = git("rev-parse", "--show-toplevel")
        if top.returncode:
            return {"state": "not_git"}
        if Path(top.stdout.strip()).resolve() != root:
            return {"state": "source_checkout"}
        origin = git("remote", "get-url", "origin")
        url = origin.stdout.strip().removesuffix(".git").rstrip("/").lower()
        official = url in {f"https://github.com/{REPO}".lower(), f"git@github.com:{REPO}".lower()}
        status = git("status", "--porcelain", "--untracked-files=all")
        if status.returncode:
            return {"state": "unavailable"}
        return {"state": "modified" if status.stdout.strip() else "clean", "official_origin": official}
    except (OSError, subprocess.TimeoutExpired):
        return {"state": "unavailable"}


def fetch_json(url):
    request = urllib.request.Request(url, headers={"User-Agent": "AI-hackathon-update-check", "Accept": "application/json"})
    with urllib.request.urlopen(request, timeout=8) as response:
        return json.load(response)


def latest_release():
    release = fetch_json(f"https://api.github.com/repos/{REPO}/releases/latest")
    tag = str(release.get("tag_name", ""))
    if release.get("draft") or release.get("prerelease") or not re.fullmatch(r"v\d+\.\d+\.\d+", tag):
        raise ValueError("No supported stable release")
    manifest = validate_manifest(fetch_json(f"https://raw.githubusercontent.com/{REPO}/{tag}/update-manifest.json"))
    if tag != "v" + manifest["version"]:
        raise ValueError("Release and manifest versions differ")
    return manifest


def inspect(root, offline=False):
    root = Path(root).resolve()
    result = {"read_only": True, "local_version": version_of(root), "latest_version": None,
              "update_available": None, "integrity": "legacy_unverified", "file_issues": [],
              "git": git_state(root), "network": "not_checked"}
    path = root / "update-manifest.json"
    if path.is_file():
        try:
            manifest = validate_manifest(json.loads(path.read_text(encoding="utf-8-sig")))
            if manifest["version"] != result["local_version"]:
                raise ValueError("Local version and manifest differ")
            result["file_issues"] = check_files(root, manifest)
            log = (root / "CHANGELOG.md").read_text(encoding="utf-8-sig")
            if f'## [{result["local_version"]}]' not in log:
                result["file_issues"].append({"file": "CHANGELOG.md", "issue": "version_entry_missing"})
            result["integrity"] = "issues" if result["file_issues"] else "local_manifest_ok"
        except (ValueError, OSError) as error:
            result["integrity"] = "invalid_manifest"
            result["manifest_error"] = str(error)
    if not offline:
        try:
            remote = latest_release()
            result["latest_version"] = remote["version"]
            result["update_available"] = tuple(map(int, remote["version"].split("."))) > tuple(map(int, result["local_version"].split(".")))
            result["network"] = "ok"
            result["release_url"] = f'https://github.com/{REPO}/releases/tag/v{remote["version"]}'
            if remote["version"] == result["local_version"]:
                result["file_issues"] = check_files(root, remote)
                result["integrity"] = "issues" if result["file_issues"] else "release_manifest_ok"
        except (ValueError, OSError) as error:
            result["network"] = "unavailable"
            result["network_error"] = type(error).__name__
    state = result["git"]["state"]
    if state == "source_checkout":
        readiness = "maintain_source_repository"
    elif state == "modified":
        readiness = "review_local_changes"
    elif result["git"].get("official_origin") is False:
        readiness = "source_mismatch"
    elif result["integrity"] in {"issues", "invalid_manifest"}:
        readiness = "repair_or_compare_first"
    elif result["network"] != "ok":
        readiness = "latest_version_unknown"
    elif state != "clean" or result["integrity"] == "legacy_unverified":
        readiness = "manual_compare_required"
    elif result["update_available"]:
        readiness = "ready_for_authorized_update"
    else:
        readiness = "current" if result["local_version"] == result["latest_version"] else "local_ahead"
    result["update_readiness"] = readiness
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--path", type=Path, default=Path(__file__).resolve().parent.parent)
    parser.add_argument("--offline", action="store_true", help="Only inspect local files; do not use network")
    args = parser.parse_args()
    try:
        result = inspect(args.path, args.offline)
    except (ValueError, OSError) as error:
        print(json.dumps({"read_only": True, "error": str(error)}, ensure_ascii=False))
        return 2
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 2 if result["integrity"] in {"issues", "invalid_manifest"} else 0


if __name__ == "__main__":
    raise SystemExit(main())
