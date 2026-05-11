# Data Batch Simulator

This script simulates a streaming data source by reading rows from a CSV file in batches and uploading each batch as a timestamped `.csv` file to your S3 bucket. It is designed to mimic telescope sensor data arriving over time for downstream ingestion/testing workflows.

## What this Script Does

- Loads a source CSV dataset (`data/magic04.data`)
- Splits the data into randomly sized chunks
- Writes each chunk to a temporary CSV file
- Uploads each file to `s3://<BUCKET_NAME>/dump/`
- Waits between uploads to simulate real-time streaming
- Repeats until all rows are sent

## Prerequisites

- AWS credentials configured locally (`aws configure`) or via environment variables
- The `BUCKET_NAME` variable in your aws `.env` file should be specified prior to running this script.

```
.
├── aws
│   └── .env
└── mock_data_source
    ├── data/
    └── data_batch_simulator.py
```

## Run with uv

```bash
uv run data_batch_simulator.py
```