#!/usr/bin/env python3
"""Refresh this repository's Codex plugin timestamp, preserving its release version."""

import json
from datetime import datetime, timezone
from pathlib import Path


def main():
    manifest_path = Path(__file__).resolve().parents[1] / ".codex-plugin" / "plugin.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    previous = manifest["version"]
    release = previous.split("+", 1)[0]
    if not release:
        raise ValueError("Plugin version must have a non-empty release version")
    timestamp = datetime.now(timezone.utc).strftime("%y%m%d%H%M%S")
    manifest["version"] = f"{release}+{timestamp}"
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(f"Updated plugin version: {previous} -> {manifest['version']}")


if __name__ == "__main__":
    main()
