"""
Test Script for Gamma Telescope Classification MLOps Project
============================================================

Sends a sample gamma telescope event to the live Databricks Model Serving
endpoint and prints the prediction response.

This verifies the end-to-end deployed prediction path:
local script -> Databricks Serving Endpoint -> registered ML model -> prediction

Requirements:
    pip install requests pandas

Required environment variables:
    DATABRICKS_HOST      Databricks workspace URL
    DATABRICKS_TOKEN     Databricks personal access token
    

Example setup:
    export DATABRICKS_HOST="https://dbc-24fb6b05-9f8e.cloud.databricks.com"
    export DATABRICKS_TOKEN="your_token_here"
    

Usage:
    python test_project.py
"""

import os
import sys
import requests
import pandas as pd
from dotenv import load_dotenv

load_dotenv()


def get_env(name):
    value = os.getenv(name)
    if not value:
        print(f"FAIL: Missing required environment variable: {name}")
        sys.exit(1)
    return value


def main():
    url = get_env("DATABRICKS_HOST")
    token = get_env("DATABRICKS_TOKEN")

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }

    # Sample input matching the full pipeline model's expected raw features
    sample_df = pd.DataFrame([{
    "f_length": 28.8,
    "f_size": 2.6,
    "f_conc1": 0.20,
    "f_m3long": 22.0,
    "f_alpha": 18.0,
}])

    payload = {
        "dataframe_split": sample_df.to_dict(orient="split")
    }


    resp = requests.post(url, headers=headers, json=payload, timeout=60)

    if resp.status_code != 200:
        print(f"FAIL: Got status {resp.status_code}")
        print(resp.text)
        sys.exit(1)

    result = resp.json()

    print("\nPrediction response:")
    print(result)

    # Databricks usually returns predictions in a "predictions" key
    if "predictions" in result:
        print(f"\nPrediction: {result['predictions']}")
    else:
        print("\nPrediction key not found, but response was returned successfully.")

    print("\nPASS")
    sys.exit(0)


if __name__ == "__main__":
    main()