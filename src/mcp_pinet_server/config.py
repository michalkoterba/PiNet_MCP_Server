"""
Configuration management for PiNet MCP Server
Loads and validates environment variables from .env file
"""

import os
from dataclasses import dataclass
from dotenv import load_dotenv


@dataclass
class Config:
    """Configuration container for PiNet MCP Server"""
    pinet_api_url: str
    pinet_api_key: str

    @classmethod
    def from_env(cls) -> "Config":
        """
        Load configuration from environment variables.

        Environment variables are loaded from .env file if present.

        Required environment variables:
            PINET_API_URL: Base URL of the PiNet API (e.g., http://192.168.1.50:5000)
            PINET_API_KEY: API key for authenticating with PiNet API

        Returns:
            Config: Configuration instance

        Raises:
            ValueError: If required environment variables are missing
        """
        # Load environment variables from .env file
        load_dotenv()

        # Get required configuration
        url = os.getenv('PINET_API_URL')
        key = os.getenv('PINET_API_KEY')

        # Validate required variables
        if not url:
            raise ValueError(
                "Missing required environment variable: PINET_API_URL\n"
                "Please set it in your .env file or environment."
            )

        if not key:
            raise ValueError(
                "Missing required environment variable: PINET_API_KEY\n"
                "Please set it in your .env file or environment."
            )

        # Strip whitespace and trailing slashes from URL
        url = url.strip().rstrip('/')
        key = key.strip()

        return cls(pinet_api_url=url, pinet_api_key=key)

    def __repr__(self) -> str:
        """String representation with masked API key"""
        masked_key = f"{self.pinet_api_key[:4]}...{self.pinet_api_key[-4:]}" if len(self.pinet_api_key) > 8 else "****"
        return f"Config(pinet_api_url='{self.pinet_api_url}', pinet_api_key='{masked_key}')"