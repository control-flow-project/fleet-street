import io
import json
import os
import subprocess
import sys
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

from tools.fleet_street.cli import main
from tools.fleet_street.files import read_json, write_new


ROOT = Path(__file__).resolve().parents[1]


class FileAndCliTests(unittest.TestCase):
    def setUp(self) -> None:
        (ROOT / ".temp").mkdir(exist_ok=True)
        self.temporary = tempfile.TemporaryDirectory(dir=ROOT / ".temp")
        self.addCleanup(self.temporary.cleanup)
        self.directory = Path(self.temporary.name)

    def test_budget_cli_outputs_actual_json_and_refuses_to_overwrite(self) -> None:
        target = self.directory / "budget.json"
        arguments = ["budget", "--input", str(ROOT / "examples/budget.json"), "--output", str(target)]
        with redirect_stdout(io.StringIO()) as output:
            self.assertEqual(main(arguments), 0)
        self.assertEqual(json.loads(output.getvalue()), json.loads(target.read_text()))
        original = target.read_bytes()
        with redirect_stderr(io.StringIO()) as error:
            self.assertEqual(main(arguments), 2)
        self.assertIn("fleet-street:", error.getvalue())
        self.assertEqual(target.read_bytes(), original)

    def test_invalid_json_duplicates_and_constants_fail(self) -> None:
        target = self.directory / "input.json"
        for content in ['{"key":1,"key":2}', '{"value":NaN}', '{"value":Infinity}', "{invalid}"]:
            target.write_text(content)
            with self.assertRaises(ValueError):
                read_json(target)

    def test_nonregular_oversized_and_linked_inputs_fail(self) -> None:
        with self.assertRaises(ValueError):
            read_json(self.directory)
        target = self.directory / "large.json"
        target.write_bytes(b" " * (1024 * 1024 + 1))
        with self.assertRaisesRegex(ValueError, "1 MiB"):
            read_json(target)
        linked = self.directory / "linked.json"
        linked.symlink_to(ROOT / "examples/brief.json")
        with self.assertRaisesRegex(ValueError, "symbolic"):
            read_json(linked)

    def test_output_link_cannot_redirect_private_data(self) -> None:
        real = self.directory / "real"
        real.mkdir()
        linked = self.directory / "link"
        linked.symlink_to(real, target_is_directory=True)
        with self.assertRaises(ValueError):
            write_new(linked / "unexpected.json", "secret")
        self.assertEqual(list(real.iterdir()), [])

    def test_handoff_passes_exact_native_flags_without_shell_evaluation(self) -> None:
        executable = self.directory / "node"
        executable.write_text(f'#!{sys.executable}\nimport json,sys\nprint(json.dumps(sys.argv[1:]))\n')
        executable.chmod(0o700)
        project = str(self.directory / "a project; not a command")
        profile = "stage-manager; echo not-executed"
        arguments = ["!room:example.org", "@specialist:example.org", "stable-id", "a file with `backticks`.md"]
        result = subprocess.run(["sh", str(ROOT / "examples/send-handoff.sh"), *arguments], env={**os.environ, "PATH": str(self.directory) + os.pathsep + os.environ["PATH"], "CROSSFIRE_PROJECT": project, "CROSSFIRE_AGENT_NAME": profile}, text=True, capture_output=True, check=True)
        self.assertEqual(json.loads(result.stdout), [project + "/.crossfire/client.mjs", "--project", project, "--profile", profile, "matrix", "send-message", "--room-id", arguments[0], "--event-type", "m.room.message", "--mention-user", arguments[1], "--txn-id", arguments[2], "--markdown-file", arguments[3]])

    def test_handoff_requires_explicit_identity_and_destination(self) -> None:
        result = subprocess.run(["sh", str(ROOT / "examples/send-handoff.sh")], text=True, capture_output=True)
        self.assertEqual(result.returncode, 2)
        self.assertIn("Usage:", result.stderr)
