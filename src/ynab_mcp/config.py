"""
Configuration for the YNAB MCP server.
"""

import os

from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Config:
    """Configuration for the YNAB MCP server."""

    # YNAB API
    YNAB_API_TOKEN: str = os.getenv("YNAB_API_TOKEN", "")
    YNAB_API_BASE_URL: str = os.getenv("YNAB_API_BASE_URL", "https://api.ynab.com/v1")

    @classmethod
    def validate(cls) -> None:
        """Validate the configuration."""
        if not cls.YNAB_API_TOKEN:
            raise ValueError(
                "YNAB_API_TOKEN is required. "
                "Get your token from https://app.ynab.com/settings/developer"
            )


# Create a singleton instance
config = Config()
