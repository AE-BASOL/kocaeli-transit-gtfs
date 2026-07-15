import os
import subprocess
import sys
from pathlib import Path

def test_generate_dashboard_html_valid():
    """
    Test that generate_dashboard.py outputs correct structure without syntax errors
    and data/index.html is successfully created.
    """
    project_root = Path(__file__).resolve().parent.parent
    src_file = project_root / "src" / "generate_dashboard.py"
    data_dir = project_root / "data"
    output_html = data_dir / "index.html"

    assert src_file.exists(), f"{src_file} does not exist"

    # Remove the file if it exists to be sure it's newly generated
    if output_html.exists():
        output_html.unlink()

    result = subprocess.run(
        [sys.executable, str(src_file)],
        cwd=project_root,
        capture_output=True,
        text=True
    )

    assert result.returncode == 0, f"Script failed with output:\nSTDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}"
    assert output_html.exists(), "data/index.html was not created"

    content = output_html.read_text()
    assert "<html" in content.lower() or "<!doctype" in content.lower(), "File does not look like HTML"
