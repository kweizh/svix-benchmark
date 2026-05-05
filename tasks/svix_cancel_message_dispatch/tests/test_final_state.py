import os
import subprocess
import json
import pytest

PROJECT_DIR = "/home/user/svix-project"
OUTPUT_FILE = os.path.join(PROJECT_DIR, "output.json")

def test_output_file_exists_and_valid():
    """Priority 3: Verify the output file exists and contains valid IDs."""
    assert os.path.isfile(OUTPUT_FILE), f"Output file {OUTPUT_FILE} does not exist."
    
    with open(OUTPUT_FILE, "r") as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError:
            pytest.fail(f"File {OUTPUT_FILE} is not valid JSON.")
            
    assert "app_id" in data, f"'app_id' missing from {OUTPUT_FILE}."
    assert "endpoint_id" in data, f"'endpoint_id' missing from {OUTPUT_FILE}."

def test_transformation_logic():
    """Priority 1: Use a Node.js script to query the Svix API and verify the Transformation state."""
    # First, make sure the output file is valid
    if not os.path.isfile(OUTPUT_FILE):
        pytest.skip(f"Output file {OUTPUT_FILE} missing, cannot verify transformation.")
        
    with open(OUTPUT_FILE, "r") as f:
        data = json.load(f)
        
    app_id = data.get("app_id")
    endpoint_id = data.get("endpoint_id")
    
    if not app_id or not endpoint_id:
        pytest.skip("Missing app_id or endpoint_id, cannot verify transformation.")

    # We write a small Node.js script to fetch the transformation and print it as JSON
    verify_script = f"""
const {{ Svix }} = require('svix');
const svix = new Svix(process.env.SVIX_AUTH_TOKEN);

async function verify() {{
    try {{
        const transformation = await svix.endpoint.transformationGet('{app_id}', '{endpoint_id}');
        console.log(JSON.stringify(transformation));
    }} catch (err) {{
        console.error(err);
        process.exit(1);
    }}
}}

verify();
"""
    verify_script_path = os.path.join(PROJECT_DIR, "verify_transformation.js")
    with open(verify_script_path, "w") as f:
        f.write(verify_script)
        
    result = subprocess.run(
        ["node", "verify_transformation.js"],
        capture_output=True, text=True, cwd=PROJECT_DIR
    )
    
    assert result.returncode == 0, f"Failed to fetch transformation from Svix API: {result.stderr}"
    
    try:
        transformation = json.loads(result.stdout)
    except json.JSONDecodeError:
        pytest.fail(f"Failed to parse transformation JSON from Svix API: {result.stdout}")
        
    assert transformation.get("enabled") is True, "Transformation is not enabled."
    
    code = transformation.get("code", "")
    assert code, "Transformation code is empty or missing."
    
    # Simple heuristic to check if the code cancels the webhook when cancel_me is true
    assert "cancel" in code, "Transformation code does not contain 'cancel'."
    assert "cancel_me" in code, "Transformation code does not check for 'cancel_me'."
