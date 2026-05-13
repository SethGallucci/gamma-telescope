"""
Smoke test for the deployed Gamma Telescope model endpoint.

Purpose
-------
Validate that the live Databricks serving endpoint:

1. Is reachable
2. Authenticates successfully
3. Accepts a valid inference payload
4. Returns a non-empty predictions field

Exit Codes
----------
0 = Success
1 = Test failed

Required Environment Variables
------------------------------
DATABRICKS_URL
DATABRICKS_TOKEN

Usage
-----
python test_end_to_end.py
"""

from __future__ import annotations

import logging
import os
import sys
from dataclasses import dataclass
from typing import Any

import requests
from dotenv import load_dotenv

# Load local .env file if present
load_dotenv()

# ---------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------

logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s: %(message)s",
)

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------


@dataclass(frozen=True)
class Settings:
    """Runtime configuration loaded from environment."""
    url: str
    token: str
    timeout_seconds: int = 30


def load_settings() -> Settings:
    """Load required environment variables."""
    url = os.getenv("DATABRICKS_URL")
    token = os.getenv("DATABRICKS_TOKEN")

    missing = []

    if not url:
        missing.append("DATABRICKS_URL")

    if not token:
        missing.append("DATABRICKS_TOKEN")

    if missing:
        logger.error(
            "Missing required environment variables: %s",
            ", ".join(missing),
        )
        sys.exit(1)

    return Settings(
        url=url,
        token=token,
    )


# ---------------------------------------------------------------------
# Request Payload
# ---------------------------------------------------------------------


def build_payload() -> dict[str, Any]:
    """
    Build a minimal valid inference payload.

    Uses Databricks / MLflow dataframe_records format.
    """
    return {
        "dataframe_records": [
            {
                "f_length": 28.8,
                "f_size": 2.6,
                "f_conc1": 0.20,
                "f_m3long": 22.0,
                "f_alpha": 18.0,
            }
        ]
    }


# ---------------------------------------------------------------------
# HTTP Request
# ---------------------------------------------------------------------


def request_prediction(settings: Settings) -> dict[str, Any]:
    """Send request to endpoint and return parsed JSON."""
    headers = {
        "Authorization": f"Bearer {settings.token}",
        "Content-Type": "application/json",
    }

    logger.info("Sending smoke test request...")

    try:
        response = requests.post(
            url=settings.url,
            headers=headers,
            json=build_payload(),
            timeout=settings.timeout_seconds,
        )

    except requests.Timeout:
        logger.error(
            "Request timed out after %s seconds.",
            settings.timeout_seconds,
        )
        sys.exit(1)

    except requests.RequestException:
        logger.error("Network request failed.")
        sys.exit(1)

    if response.status_code != 200:
        logger.error(
            "Endpoint returned unexpected HTTP status: %s",
            response.status_code,
        )
        sys.exit(1)

    try:
        return response.json()

    except ValueError:
        logger.error("Endpoint returned non-JSON response.")
        sys.exit(1)


# ---------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------


def validate_result(result: dict[str, Any]) -> None:
    """Validate expected response structure."""
    predictions = result.get("predictions")

    if predictions is None:
        logger.error("Response missing predictions field.")
        sys.exit(1)

    if not isinstance(predictions, list):
        logger.error("Predictions field had unexpected type.")
        sys.exit(1)

    if len(predictions) == 0:
        logger.error("Predictions field was empty.")
        sys.exit(1)

    logger.info(
        "Smoke test succeeded. Received %d prediction(s).",
        len(predictions),
    )


# ---------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------


def main() -> None:
    """Run smoke test."""
    settings = load_settings()

    result = request_prediction(settings)

    validate_result(result)

    sys.exit(0)


if __name__ == "__main__":
    main()
