import subprocess
import sys


def test_module_entrypoint():
    result = subprocess.run(
        [sys.executable, "-m", "python_template"], capture_output=True, text=True, check=True
    )
    assert result.stdout.strip() == "Hello from python-template!"
    assert not result.stderr
