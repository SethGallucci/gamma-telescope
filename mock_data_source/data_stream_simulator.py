import boto3
import pandas as pd
import os
import time
import random
from dotenv import load_dotenv
from datetime import datetime

load_dotenv("../aws/infrastructure.env")
bucket_name = os.getenv("BUCKET_NAME")

s3_client = boto3.client("s3")


def simulate_telescope_stream(
    source_csv,
    mean_size=500,
    std_dev=150,
    max_size=1000,
    delay_seconds=5,
):
    print(f"Initializing telescope feed to s3://{bucket_name}/dump/ ...")

    df = pd.read_csv(source_csv, header=None)
    total_rows = len(df)
    current_row = 0

    while current_row < total_rows:
        random_size = int(random.gauss(mean_size, std_dev))
        chunk_size = max(10, min(max_size, random_size))

        if current_row + chunk_size > total_rows:
            chunk_size = total_rows - current_row

        chunk = df.iloc[current_row: current_row + chunk_size]
        current_row += chunk_size

        now = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        chunk_filename = f"gamma_telescope_chunk_{now}.csv"

        chunk.to_csv(chunk_filename, index=False, header=False)

        s3_key = f"dump/{chunk_filename}"
        s3_client.upload_file(chunk_filename, bucket_name, s3_key)

        print(f"[SUCCESS] Beamed {chunk_filename} ({len(chunk)} rows) to S3.")

        os.remove(chunk_filename)
        time.sleep(delay_seconds)

    print("Stream complete. All data beamed to AWS.")

simulate_telescope_stream(source_csv="data/magic04.data")