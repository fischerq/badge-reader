import yaml
import os

ADDON_DIR = "badgereader_addon" # Relative to repo root

def test_addon_config_valid():
    """Check if the addon config.yaml is valid YAML and has required keys."""
    config_path = os.path.join(ADDON_DIR, "config.yaml")
    assert os.path.exists(config_path), "config.yaml not found"

    with open(config_path, 'r') as f:
        try:
            config = yaml.safe_load(f)
        except yaml.YAMLError as e:
            assert False, f"config.yaml is not valid YAML: {e}"

    assert isinstance(config, dict), "config.yaml should be a dictionary"
    required_keys = ["name", "version", "slug", "arch"]
    for key in required_keys:
        assert key in config, f"Required key '{key}' missing in config.yaml"

    assert isinstance(config.get("arch"), list) and len(config["arch"]) > 0, "'arch' must be a non-empty list"

def test_dockerfile_exists():
    """Check if the Dockerfile exists."""
    dockerfile_path = os.path.join(ADDON_DIR, "Dockerfile")
    assert os.path.exists(dockerfile_path), "Dockerfile not found"

def test_run_sh_exists():
    """Check if the run.sh script exists."""
    run_sh_path = os.path.join(ADDON_DIR, "run.sh")
    assert os.path.exists(run_sh_path), "run.sh not found"

def test_conceptual_addon_build_and_run():
    """
    This is a conceptual test. In a full CI setup, you would:
    1. Build the Docker image from badgereader_addon/Dockerfile.
       (e.g., using 'docker build badgereader_addon/')
    2. Run the container.
       (e.g., using 'docker run <image_id>')
    3. Check container logs for successful startup messages from run.sh.
    4. If the addon exposes any network ports or services, try to connect to them.
    5. In a Home Assistant development environment, deploy and check if the integration loads.
    """
    print("Conceptual test: Addon build and run would be performed here.")
    assert True # Placeholder for actual build/run verification

# Example of how to run these tests (e.g., with pytest):
# If you have pytest installed, you can run 'pytest tests/addon/test_addon_packaging.py'
