"""Smoke tests to verify basic framework functionality."""

import pytest

from caqf.config import get_config, Config


@pytest.mark.unit
def test_config_loads():
    """Verify that configuration loads and returns defaults."""
    config = get_config()
    
    assert config is not None
    assert isinstance(config, type)
    assert issubclass(config, Config)


@pytest.mark.unit
def test_config_has_defaults():
    """Verify that configuration has expected default values."""
    config = get_config()
    
    assert config.CLIENT_MODE == "mock"
    assert config.REQUEST_TIMEOUT_SEC == 10
    assert isinstance(config.BASE_URL, str)
    assert isinstance(config.AUTH_TOKEN, str)


@pytest.mark.unit
def test_config_methods():
    """Verify that configuration methods work correctly."""
    config = get_config()
    
    assert config.get_client_mode() == "mock"
    assert config.get_request_timeout() == 10
    assert isinstance(config.get_base_url(), str)
    assert isinstance(config.get_auth_token(), str)

