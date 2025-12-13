"""Configuration loader for the QA framework."""

import os
from typing import Optional

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass


class Config:
    """Configuration settings loaded from environment variables."""

    BASE_URL: str = os.getenv("BASE_URL", "")
    AUTH_TOKEN: str = os.getenv("AUTH_TOKEN", "")
    CLIENT_MODE: str = os.getenv("CLIENT_MODE", "mock")
    REQUEST_TIMEOUT_SEC: int = int(os.getenv("REQUEST_TIMEOUT_SEC", "10"))

    @classmethod
    def get_base_url(cls) -> str:
        """Get the base URL for API requests."""
        return cls.BASE_URL

    @classmethod
    def get_auth_token(cls) -> str:
        """Get the authentication token."""
        return cls.AUTH_TOKEN

    @classmethod
    def get_client_mode(cls) -> str:
        """Get the client mode (e.g., 'mock', 'live')."""
        return cls.CLIENT_MODE

    @classmethod
    def get_request_timeout(cls) -> int:
        """Get the request timeout in seconds."""
        return cls.REQUEST_TIMEOUT_SEC


def get_config() -> Config:
    """Get the configuration instance."""
    return Config

