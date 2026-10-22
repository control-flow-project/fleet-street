import os
import subprocess
import tempfile
import tomllib
import unittest
from pathlib import Path

from tools.fleet_street.configuration import TEMPLATE, configure, render_roster


ROOT = Path(__file__).resolve().parents[1]


class ConfigurationTests(unittest.TestCase):
    def setUp(self) -> None:
        (ROOT / ".temp").mkdir(exist_ok=True)
        self.temporary = tempfile.TemporaryDirectory(dir=ROOT / ".temp")
        self.addCleanup(self.temporary.cleanup)
        self.target = Path(self.temporary.name) / "working-fleet"

    def test_roster_roles_and_directory_have_the_same_ten_keys(self) -> None:
        roster = tomllib.loads((TEMPLATE / "runtime.toml").read_text())
        instances = roster["instances"]
        keys = {item["key"] for item in instances}
        self.assertEqual(len(instances), 10)
        self.assertEqual(len(keys), 10)
        self.assertEqual(keys, {item.name for item in (TEMPLATE / "agents").iterdir() if item.is_dir()})
        self.assertEqual(len({item["name"] for item in instances}), 10)
        self.assertEqual(len({item["workarea"] for item in instances}), 10)
        for item in instances:
            self.assertIn(f'| {item["key"]} |', (TEMPLATE / "directory.md").read_text())
            self.assertEqual(item["definition"], item["key"])
            self.assertEqual(item["listener_options"], {"history_mode": "shared"})
            role = tomllib.loads((TEMPLATE / "agents" / item["definition"] / "agent.toml").read_text())
            self.assertEqual(role["runtime"], "codex")
            self.assertEqual(role["runtime_options"]["approval_policy"], "on-request")
            self.assertNotIn("model", role["runtime_options"])
            self.assertEqual(role["runtime_options"]["model_reasoning_effort"], "medium" if item["key"] == "stage-manager" else "high")
            policy = role["coordination_options"]
            self.assertEqual(policy["wake_mode"], "selected")
            self.assertEqual(policy["wake_senders"], [{"backend_user_id": "@owner:example.test", "include_agents": True}])
            self.assertEqual(policy["permissions"], ["room.agent.invite"] if item["key"] == "stage-manager" else [])

    def test_private_generation_sets_every_owner_and_registered_name(self) -> None:
        result = configure("https://chat.example.org/", "@alice:chat.example.org", "alice-fs", destination=self.target)
        self.assertFalse(result["enrollment_performed"])
        self.assertNotIn("enrolled", result)
        roster = tomllib.loads((self.target / "runtime.toml").read_text())
        self.assertEqual(roster["coordination"]["server"], "https://chat.example.org")
        for item in roster["instances"]:
            self.assertEqual(item["name"], "alice-fs-" + item["key"])
            role = tomllib.loads((self.target / "agents" / item["definition"] / "agent.toml").read_text())
            self.assertEqual(role["coordination_options"]["wake_senders"][0]["backend_user_id"], "@alice:chat.example.org")
        if os.name == "posix":
            for item in [self.target, *self.target.rglob("*")]:
                self.assertEqual(item.stat().st_mode & 0o777, 0o700 if item.is_dir() else 0o600)

    def test_same_configuration_reuses_without_recopying_history_or_edits(self) -> None:
        configure("https://chat.example.org", "@alice:chat.example.org", "alice-fs", destination=self.target)
        history = self.target / "agents/stage-manager/workarea/stage-manager/.codex/history.jsonl"
        history.parent.mkdir(parents=True)
        history.write_text("retained native history")
        instructions = self.target / "agents/stage-manager/AGENTS.md"
        instructions.write_text("Operator's revised instructions")
        result = configure("https://chat.example.org", "@alice:chat.example.org", "alice-fs", destination=self.target)
        self.assertTrue(result["existing"])
        self.assertFalse(result["enrollment_performed"])
        self.assertNotIn("enrolled", result)
        self.assertEqual(history.read_text(), "retained native history")
        self.assertEqual(instructions.read_text(), "Operator's revised instructions")

    def test_changed_owner_prefix_or_model_never_replaces_an_existing_fleet(self) -> None:
        configure("https://chat.example.org", "@alice:chat.example.org", "alice-fs", "exact-model", destination=self.target)
        original = (self.target / "runtime.toml").read_bytes()
        for owner, prefix, model in [("@other:chat.example.org", "alice-fs", "exact-model"), ("@alice:chat.example.org", "other-fs", "exact-model"), ("@alice:chat.example.org", "alice-fs", "different-model")]:
            with self.assertRaises(ValueError):
                configure("https://chat.example.org", owner, prefix, model, destination=self.target)
        self.assertEqual((self.target / "runtime.toml").read_bytes(), original)

    def test_explicit_model_is_preserved_in_all_definitions(self) -> None:
        configure("https://chat.example.org", "@alice:chat.example.org", "alice-fs", "provider-model", destination=self.target)
        for filename in self.target.glob("agents/*/agent.toml"):
            self.assertEqual(tomllib.loads(filename.read_text())["runtime_options"]["model"], "provider-model")

    def test_bad_origin_owner_prefix_and_long_names_fail_without_a_fleet(self) -> None:
        source = (TEMPLATE / "runtime.toml").read_text()
        for server, owner, prefix in [("http://chat.example.org", "@alice:chat.example.org", "ok"), ("https://user:secret@chat.example.org", "@alice:chat.example.org", "ok"), ("https://chat.example.org/path", "@alice:chat.example.org", "ok"), ("https://chat.example.org?key=x", "@alice:chat.example.org", "ok"), ("https://chat.example.org", "Alice", "ok"), ("https://chat.example.org", "@alice:chat.example.org", "Bad Prefix"), ("https://chat.example.org", "@alice:chat.example.org", "a" * 40)]:
            with self.subTest(server=server, prefix=prefix):
                with self.assertRaises(ValueError):
                    render_roster(source, server, owner, prefix)
        self.assertFalse(self.target.exists())

    def test_local_development_origins_follow_the_native_fleet_contract(self) -> None:
        source = (TEMPLATE / "runtime.toml").read_text()
        for origin in ["http://localhost:8080", "http://127.0.0.1:8080", "http://[::1]:8080"]:
            generated = render_roster(source, origin, "@owner:example.test", "local-fs")
            self.assertEqual(tomllib.loads(generated)["coordination"]["server"], origin)

    def test_symlink_destination_cannot_be_followed(self) -> None:
        real = Path(self.temporary.name) / "real"
        real.mkdir()
        self.target.symlink_to(real, target_is_directory=True)
        with self.assertRaises(ValueError):
            configure("https://chat.example.org", "@alice:chat.example.org", "alice-fs", destination=self.target)
        self.assertEqual(list(real.iterdir()), [])

    def test_operating_paths_are_ignored_and_templates_are_trackable(self) -> None:
        for filename in [".local/fleet/runtime.toml", "fleet/.fleet/binding.json", "fleet/agents/stage-manager/workarea/stage-manager/.codex/auth.json", ".temp/test/data.json"]:
            self.assertEqual(subprocess.run(["git", "check-ignore", "--no-index", "-q", filename], cwd=ROOT).returncode, 0, filename)
        self.assertNotEqual(subprocess.run(["git", "check-ignore", "--no-index", "-q", "fleet/runtime.toml"], cwd=ROOT).returncode, 0)

    def test_existing_role_links_and_incomplete_settings_are_not_repaired_silently(self) -> None:
        configure("https://chat.example.org", "@alice:chat.example.org", "alice-fs", destination=self.target)
        role = self.target / "agents/stage-manager/agent.toml"
        role.write_text('name = "Incomplete"\n')
        with self.assertRaisesRegex(ValueError, "incomplete"):
            configure("https://chat.example.org", "@alice:chat.example.org", "alice-fs", destination=self.target)
        self.assertEqual(role.read_text(), 'name = "Incomplete"\n')
        role.unlink()
        role.symlink_to(TEMPLATE / "agents/stage-manager/agent.toml")
        with self.assertRaisesRegex(ValueError, "symbolic"):
            configure("https://chat.example.org", "@alice:chat.example.org", "alice-fs", destination=self.target)
