from __future__ import annotations

import importlib.util
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "kb_creator" / "scripts" / "normalize_publication_access.py"
SPEC = importlib.util.spec_from_file_location("normalize_publication_access", SCRIPT)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class _Result:
    returncode = 0
    stdout = ""
    stderr = ""


class _Failure:
    returncode = 5
    stdout = ""
    stderr = "Access is denied"


class PublicationAccessTests(unittest.TestCase):
    def test_isolated_consumer_resolves_enclosing_git_worktree(self):
        with TemporaryDirectory() as temporary:
            repo = Path(temporary) / "repo"
            module = repo / "kb_creator/working/consumer/kb_creator/scripts/normalize_publication_access.py"
            module.parent.mkdir(parents=True)
            module.touch()
            (repo / ".git").write_text("gitdir: elsewhere", encoding="utf-8")
            with patch.object(MODULE, "__file__", str(module)):
                self.assertEqual(MODULE._repo_root(), repo.resolve())
                outside = repo / "unmanaged"
                outside.mkdir()
                result = MODULE.normalize_publication_access_if_managed(outside)
                self.assertEqual(result["reason"], "outside_managed_working_tree")

    def test_non_checkout_fixture_keeps_module_root(self):
        with TemporaryDirectory() as temporary:
            repo = Path(temporary)
            module = repo / "kb_creator/scripts/normalize_publication_access.py"
            module.parent.mkdir(parents=True)
            module.touch()
            with patch.object(MODULE, "__file__", str(module)):
                self.assertEqual(MODULE._repo_root(), repo.resolve())

    def test_normalizer_is_confined_to_working_tree(self):
        with TemporaryDirectory() as temporary:
            root = Path(temporary)
            outside = root / "artifacts"
            outside.mkdir()
            working = root / "repo" / "kb_creator" / "working"
            working.mkdir(parents=True)

            with self.assertRaisesRegex(
                MODULE.PublicationAccessError, "inside kb_creator/working"
            ):
                MODULE.normalize_publication_access(outside, repo_root=root / "repo")

    def test_windows_normalizer_excludes_obsidian_and_processes_children(self):
        with TemporaryDirectory() as temporary:
            repo = Path(temporary) / "repo"
            artifacts = repo / "kb_creator" / "working" / "scenario" / "artifacts"
            (artifacts / ".obsidian").mkdir(parents=True)
            (artifacts / "assets").mkdir()
            (artifacts / "MASTER_RU.md").write_text("text", encoding="utf-8")
            calls = []

            def runner(command, **kwargs):
                calls.append((list(command), kwargs))
                return _Result()

            with patch.object(MODULE.os, "name", "nt"), patch.dict(
                MODULE.os.environ,
                {"USERDOMAIN": "WORKSTATION", "USERNAME": "reviewer"},
            ), patch.object(
                MODULE,
                "_icacls_path",
                return_value=Path("C:/Windows/System32/icacls.exe"),
            ):
                result = MODULE.normalize_publication_access(
                    artifacts, repo_root=repo, runner=runner
                )

            invoked = {Path(command[1]).name for command, _ in calls}
            self.assertEqual(invoked, {"artifacts", "assets", "MASTER_RU.md"})
            self.assertNotIn(".obsidian", invoked)
            root_command = next(
                command for command, _ in calls
                if Path(command[1]).name == "artifacts" and "/inheritance:e" in command
            )
            child_commands = [
                command for command, _ in calls if "/inheritance:e" in command and Path(command[1]).name != "artifacts"
            ]
            self.assertNotIn("/t", root_command)
            self.assertTrue(all("/t" in command for command in child_commands))
            grant_commands = [command for command, _ in calls if "/grant" in command]
            self.assertEqual(len(grant_commands), 3)
            self.assertTrue(
                all(any(value.startswith("WORKSTATION\\reviewer:") for value in command) for command in grant_commands)
            )
            self.assertTrue(all("/grant:r" not in command for command in grant_commands))
            root_grant = next(command for command in grant_commands if Path(command[1]).name == "artifacts")
            directory_grant = next(command for command in grant_commands if Path(command[1]).name == "assets")
            file_grant = next(command for command in grant_commands if Path(command[1]).name == "MASTER_RU.md")
            self.assertIn("WORKSTATION\\reviewer:(RX)", root_grant)
            self.assertNotIn("/t", root_grant)
            self.assertIn("WORKSTATION\\reviewer:(OI)(CI)(RX)", directory_grant)
            self.assertIn("/t", directory_grant)
            self.assertIn("WORKSTATION\\reviewer:(RX)", file_grant)
            self.assertNotIn("/t", file_grant)
            self.assertEqual(result["state"], "normalized")
            self.assertEqual(result["principal"], "WORKSTATION\\reviewer")
            self.assertEqual(result["excluded"], [".obsidian"])

    def test_windows_normalizer_fails_closed_without_desktop_principal(self):
        with TemporaryDirectory() as temporary:
            repo = Path(temporary) / "repo"
            artifacts = repo / "kb_creator" / "working" / "scenario" / "artifacts"
            artifacts.mkdir(parents=True)

            with patch.object(MODULE.os, "name", "nt"), patch.dict(
                MODULE.os.environ,
                {"USERDOMAIN": "", "USERNAME": "CodexSandboxOnline"},
            ), patch.object(
                MODULE,
                "_icacls_path",
                return_value=Path("C:/Windows/System32/icacls.exe"),
            ):
                with self.assertRaisesRegex(
                    MODULE.PublicationAccessError,
                    "desktop Windows user principal is unavailable",
                ):
                    MODULE.normalize_publication_access(artifacts, repo_root=repo)

    def test_windows_normalizer_rejects_ambiguous_domain(self):
        with TemporaryDirectory() as temporary:
            repo = Path(temporary) / "repo"
            artifacts = repo / "kb_creator" / "working" / "scenario" / "artifacts"
            artifacts.mkdir(parents=True)

            with patch.object(MODULE.os, "name", "nt"), patch.dict(
                MODULE.os.environ,
                {"USERDOMAIN": "BAD\\DOMAIN", "USERNAME": "reviewer"},
            ), patch.object(
                MODULE,
                "_icacls_path",
                return_value=Path("C:/Windows/System32/icacls.exe"),
            ):
                with self.assertRaisesRegex(
                    MODULE.PublicationAccessError,
                    "desktop Windows user principal is unavailable",
                ):
                    MODULE.normalize_publication_access(artifacts, repo_root=repo)

    def test_windows_normalizer_fails_closed_when_read_grant_fails(self):
        with TemporaryDirectory() as temporary:
            repo = Path(temporary) / "repo"
            artifacts = repo / "kb_creator" / "working" / "scenario" / "artifacts"
            artifacts.mkdir(parents=True)
            call_count = 0

            def runner(command, **kwargs):
                nonlocal call_count
                call_count += 1
                return _Failure() if "/grant" in command else _Result()

            with patch.object(MODULE.os, "name", "nt"), patch.dict(
                MODULE.os.environ,
                {"USERDOMAIN": "WORKSTATION", "USERNAME": "reviewer"},
            ), patch.object(
                MODULE,
                "_icacls_path",
                return_value=Path("C:/Windows/System32/icacls.exe"),
            ):
                with self.assertRaisesRegex(
                    MODULE.PublicationAccessError,
                    "desktop read access grant failed",
                ):
                    MODULE.normalize_publication_access(artifacts, repo_root=repo, runner=runner)

            self.assertGreaterEqual(call_count, 2)

    def test_non_windows_host_is_a_declared_skip(self):
        with TemporaryDirectory() as temporary:
            repo = Path(temporary) / "repo"
            artifacts = repo / "kb_creator" / "working" / "scenario" / "artifacts"
            artifacts.mkdir(parents=True)

            with patch.object(MODULE.os, "name", "posix"):
                result = MODULE.normalize_publication_access(artifacts, repo_root=repo)

            self.assertEqual(result["state"], "skipped")
            self.assertEqual(result["reason"], "non_windows_host")

    def test_managed_wrapper_skips_external_test_tree(self):
        with TemporaryDirectory() as temporary:
            repo = Path(temporary) / "repo"
            (repo / "kb_creator" / "working").mkdir(parents=True)
            external = Path(temporary) / "pytest-output"
            external.mkdir()

            result = MODULE.normalize_publication_access_if_managed(
                external,
                repo_root=repo,
            )

            self.assertEqual(result["state"], "skipped")
            self.assertEqual(result["reason"], "outside_managed_working_tree")


if __name__ == "__main__":
    unittest.main()
