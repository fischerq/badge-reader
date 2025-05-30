"""Tests for the services.yaml file."""

import os

import pytest

from custom_components.badgereader.const import DOMAIN

# Path to the services.yaml file
SERVICES_FILE_PATH = os.path.join(
    os.path.dirname(__file__), "..", DOMAIN, "services.yaml"
)


def test_services_file_exists():
    """Test that the services.yaml file exists."""
    assert os.path.exists(SERVICES_FILE_PATH)


def test_services_file_content():
    """Test that the services.yaml file contains the expected service definitions."""
    # This test is basic and only checks for the presence of the expected service
    # and a minimal structure. More detailed validation of parameters might
    # require parsing the YAML.

    expected_service_name = "generate_monthly_report"

    with open(SERVICES_FILE_PATH, encoding="utf-8") as f:
        content = f.read()

    assert expected_service_name in content
    # Add more assertions here if you want to check for specific parameters
    # within the service definition, potentially by parsing the YAML.
    # For example:
    # import yaml
    # services = yaml.safe_load(content)
    # assert expected_service_name in services
    # assert 'description' in services[expected_service_name]
    # assert 'fields' in services[expected_service_name]
    # assert 'year' in services[expected_service_name]['fields']
    # assert 'month' in services[expected_service_name]['fields']