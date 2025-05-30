import json
import os

def test_manifest_exists_and_is_valid():
    """Tests that the manifest.json file exists and has required keys."""
    manifest_path = os.path.join(os.path.dirname(__file__), "..", "custom_components", "badgereader", "manifest.json")
    assert os.path.exists(manifest_path)

    with open(manifest_path, "r") as f:
        manifest = json.load(f)

    required_keys = ["domain", "name", "documentation", "dependencies", "codeowners", "issue_tracker"]
    for key in required_keys:
        assert key in manifest, f"Manifest file is missing key: {key}"

    # Add checks for expected values if needed
    assert manifest["domain"] == "badgereader"
    assert isinstance(manifest["dependencies"], list)
    assert isinstance(manifest["codeowners"], list)