# Testing

This directory contains automated tests and validation scripts for the Gamma Telescope project.

## Purpose

The primary goal of these tests is to verify that deployed systems are functioning correctly after code changes or new releases.

Current coverage includes:

- **End-to-end smoke test** for the live Databricks model serving endpoint
- Validation that authentication, request formatting, and prediction responses are working

## Files

- `test_end_to_end.py` — Sends a sample inference request to the production serving endpoint and checks for a valid response.
- `pyproject.toml` — Python dependencies for the testing environment.
- `uv.lock` — Locked dependency versions for reproducible runs.

## Local Usage

From the repository root:

```bash
uv sync --project testing
uv run --project testing python testing/test_end_to_end.py