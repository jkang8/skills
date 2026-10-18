"""improve.sh keeps credentials out of the builder's environment. Uses a fake `claude`, so no model is called.

The builder can run code it writes (through the allowlisted test commands), so a secret in its environment is a
secret it can send anywhere. The fake records the environment it was started with; the real script is run in
dry-run mode against a throwaway git repo.
"""
import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

IMPROVE = Path(__file__).resolve().parent / "improve.sh"

FAKE_CLAUDE = r"""#!/bin/sh
cat > "$FAKE_DIR/stdin.txt"
case " $* " in
  *" haiku "*) echo "summary: nothing urgent"; exit 0 ;;
esac
env > "$FAKE_DIR/builder.env"
printf '%s\n' "$*" > "$FAKE_DIR/builder.args"
r="$(grep -o '/[^ `]*/result.json' "$FAKE_DIR/stdin.txt" | head -1)"
printf '{"status": "nothing", "reason": "fake builder"}' > "$r"
"""


class ImproveScrubsTheBuilderEnvironment(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.tmp, True)
        self.repo = self.tmp / "repo"
        (self.repo / "scripts").mkdir(parents=True)
        (self.repo / "Makefile").write_text("gate:\n\ttrue\n")
        (self.repo / "IMPROVE.md").write_text("# what to improve\n")
        signals = self.repo / "scripts/signals"
        signals.write_text("#!/bin/sh\necho 'one weak spot'\n")
        signals.chmod(0o755)
        for args in (["init", "-q", "-b", "main"], ["config", "user.name", "Test Owner"],
                     ["config", "user.email", "owner@users.noreply.example"], ["add", "-A"], ["commit", "-qm", "init"]):
            subprocess.run(["git", "-C", str(self.repo), *args], check=True, capture_output=True)
        self.fake = self.tmp / "fake"
        (self.fake / "bin").mkdir(parents=True)
        claude = self.fake / "bin/claude"
        claude.write_text(FAKE_CLAUDE)
        claude.chmod(0o755)

    def run_improve(self, **extra):
        env = {k: v for k, v in os.environ.items() if not any(s in k.upper() for s in ("TOKEN", "SECRET", "KEY", "PASSW"))}
        env.update({
            "PATH": f"{self.fake / 'bin'}:{os.environ['PATH']}", "FAKE_DIR": str(self.fake),
            "IMPROVE_HOME": str(self.tmp / "home"), "IMPROVE_BASE": "main", "IMPROVE_DRY_RUN": "1",
            "GITHUB_TOKEN": "ghs_not_a_real_token", "MY_SERVICE_API_KEY": "k", "AWS_SECRET_ACCESS_KEY": "s",
            "SSH_AUTH_SOCK": str(self.tmp / "fake-agent.sock"), "ANTHROPIC_API_KEY": "needed-by-claude",
            "PLAIN_SETTING": "visible", **extra,
        })
        out = subprocess.run(["sh", str(IMPROVE), str(self.repo)], capture_output=True, text=True, env=env)
        self.assertIn("no PR (nothing)", out.stdout, out.stdout + out.stderr)

    def builder_env(self) -> dict:
        lines = (self.fake / "builder.env").read_text().splitlines()
        return dict(line.split("=", 1) for line in lines if "=" in line)

    def test_secrets_are_removed_and_needed_variables_kept(self):
        self.run_improve()
        e = self.builder_env()
        for name in ("GITHUB_TOKEN", "MY_SERVICE_API_KEY", "AWS_SECRET_ACCESS_KEY", "SSH_AUTH_SOCK"):
            self.assertNotIn(name, e)
        self.assertEqual(e["ANTHROPIC_API_KEY"], "needed-by-claude")
        self.assertEqual(e["PLAIN_SETTING"], "visible")

    def test_no_stored_git_or_gh_login_is_found(self):
        self.run_improve()
        e = self.builder_env()
        self.assertEqual(e["GIT_CONFIG_GLOBAL"], "/dev/null")
        self.assertEqual(e["GIT_CONFIG_NOSYSTEM"], "1")
        self.assertEqual(e["GIT_SSH_COMMAND"], "false")
        self.assertTrue(e["GH_CONFIG_DIR"].endswith("/empty-gh"))
        self.assertEqual((e["GIT_AUTHOR_NAME"], e["GIT_AUTHOR_EMAIL"]), ("Test Owner", "owner@users.noreply.example"))

    def test_keep_env_lets_a_named_variable_through(self):
        self.run_improve(IMPROVE_KEEP_ENV="MY_SERVICE_API_KEY")
        self.assertEqual(self.builder_env()["MY_SERVICE_API_KEY"], "k")
        self.assertNotIn("GITHUB_TOKEN", self.builder_env())

    def test_wrap_prefix_runs_the_builder_inside_it(self):
        wrap = self.tmp / "wrap.sh"
        wrap.write_text(f'#!/bin/sh\necho wrapped >> "{self.tmp}/wrap.log"\nexec "$@"\n')
        wrap.chmod(0o755)
        self.run_improve(IMPROVE_WRAP=str(wrap))
        self.assertEqual((self.tmp / "wrap.log").read_text().strip(), "wrapped")
        self.assertTrue((self.fake / "builder.env").exists())  # and the builder still ran


if __name__ == "__main__":
    unittest.main()
