import os
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]


def test_importing_package_suppresses_pygame_banner():
    env = {k: v for k, v in os.environ.items() if k != "PYGAME_HIDE_SUPPORT_PROMPT"}
    proc = subprocess.run(
        [sys.executable, "-c", "import milkdrop; import milkdrop.app"],
        cwd=REPO,
        env=env,
        capture_output=True,
        text=True,
    )

    assert proc.returncode == 0, proc.stderr
    assert "Hello from the pygame community" not in (proc.stdout + proc.stderr)
