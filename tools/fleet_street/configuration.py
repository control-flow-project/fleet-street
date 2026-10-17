import json
import os
import re
import shutil
import tempfile
import tomllib
from pathlib import Path
from urllib.parse import urlsplit

from .files import canonical


REPOSITORY = Path(__file__).resolve().parents[2]
TEMPLATE = REPOSITORY / "fleet"


def server_origin(value: str) -> str:
    parsed = urlsplit(value)
    allowed = parsed.scheme == "https" or parsed.scheme == "http" and parsed.hostname in {"localhost", "127.0.0.1", "::1"}
    if not allowed or not parsed.hostname or parsed.username or parsed.password or parsed.path not in ("", "/") or parsed.query or parsed.fragment or any(character.isspace() or ord(character) < 32 for character in value):
        raise ValueError("Supply an HTTPS or loopback HTTP server origin without credentials, path or query")
    _ = parsed.port
    return value.removesuffix("/")


def render_roster(source: str, server: str, owner: str, prefix: str) -> str:
    origin = server_origin(server)
    if not re.fullmatch(r"@[^\s:]+:[^\s/]+", owner) or any(ord(character) < 32 for character in owner):
        raise ValueError("Supply the exact human Matrix owner ID")
    if not re.fullmatch(r"[a-z][a-z0-9-]*", prefix):
        raise ValueError("Prefix must start with a lowercase letter and contain lowercase letters, digits or hyphens")
    roster = tomllib.loads(source)
    result = [f'fleet = {json.dumps(roster["fleet"])}', "", "[coordination]", 'adapter = "crossfire"', f"server = {json.dumps(origin)}", f"owner = {json.dumps(owner)}"]
    for instance in roster["instances"]:
        name = prefix + "-" + instance["key"]
        if len(name) > 40:
            raise ValueError(f"Registered name exceeds 40 characters: {name}; choose a shorter prefix")
        result.extend(["", "[[instances]]", f'key = {json.dumps(instance["key"])}', f"name = {json.dumps(name)}", f'definition = {json.dumps(instance["definition"])}', f'workarea = {json.dumps(instance["workarea"])}', "", "[instances.listener_options]", f'history_mode = {json.dumps(instance["listener_options"]["history_mode"])}'])
    return "\n".join(result) + "\n"


def configure(server: str, owner: str, prefix: str, model: str | None = None, *, destination: Path | None = None) -> dict[str, object]:
    if model is not None and (not model.strip() or any(ord(character) < 32 for character in model)):
        raise ValueError("Model must be an exact native model ID without control characters")
    roster = render_roster((TEMPLATE / "runtime.toml").read_text(), server, owner, prefix)
    instances = tomllib.loads(roster)["instances"]
    target = canonical(destination if destination is not None else REPOSITORY / ".local/fleet")
    target.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    if target.exists():
        if not target.is_dir() or canonical(target / "runtime.toml").read_text() != roster:
            raise ValueError("An existing fleet has different configuration; it was not changed. Preserve its saved state and edit it only while stopped")
        for item in instances:
            role = tomllib.loads(canonical(target / "agents" / item["definition"] / "agent.toml").read_text())
            options = role.get("runtime_options")
            if not isinstance(options, dict):
                raise ValueError("Existing native configuration is incomplete; working files were not changed")
            if options.get("model") != model:
                raise ValueError("Existing native model selection differs; configuration and histories were not changed")
        return {"configuration": str(target / "runtime.toml"), "existing": True, "agents": len(instances), "enrollment_performed": False}
    with tempfile.TemporaryDirectory(prefix="configure-", dir=target.parent) as temporary:
        staging = Path(temporary) / "fleet"
        for source in TEMPLATE.rglob("*"):
            if source.is_symlink() or "workarea" in source.relative_to(TEMPLATE).parts or ".fleet" in source.relative_to(TEMPLATE).parts:
                raise ValueError("Template cannot contain links or native operating state")
        shutil.copytree(TEMPLATE, staging)
        (staging / "runtime.toml").write_text(roster)
        for filename in staging.glob("agents/*/agent.toml"):
            content = filename.read_text().replace('matrix_user_id = "@owner:example.test"', "matrix_user_id = " + json.dumps(owner))
            if model is not None:
                content = content.replace("[runtime_options]\n", "[runtime_options]\nmodel = " + json.dumps(model) + "\n")
            filename.write_text(content)
        for entry in staging.rglob("*"):
            os.chmod(entry, 0o700 if entry.is_dir() else 0o600)
        os.chmod(staging, 0o700)
        if target.exists() or target.is_symlink():
            raise ValueError("Fleet destination appeared during setup; it was not changed")
        staging.rename(target)
    return {"configuration": str(target / "runtime.toml"), "existing": False, "agents": len(instances), "enrollment_performed": False}
