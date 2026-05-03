import os
import subprocess
import pytest

APP_DIR = "/home/user/app"
SCRIPT_FILE = os.path.join(APP_DIR, "send_message.js")
OUTPUT_FILE = os.path.join(APP_DIR, "output.txt")

def test_script_exists():
    assert os.path.isfile(SCRIPT_FILE), f"Script not found at {SCRIPT_FILE}"

def test_script_runs_successfully():
    # Remove output file if it exists to ensure a fresh run
    if os.path.exists(OUTPUT_FILE):
        os.remove(OUTPUT_FILE)
        
    result = subprocess.run(
        ["node", "send_message.js"],
        cwd=APP_DIR,
        capture_output=True,
        text=True
    )
    assert result.returncode == 0, f"Script failed with error: {result.stderr}"

def test_output_file_content():
    assert os.path.isfile(OUTPUT_FILE), f"Output file not found at {OUTPUT_FILE}"
    with open(OUTPUT_FILE) as f:
        content = f.read().strip()
    assert content == "1", f"Expected output to be '1', got: {content}"
