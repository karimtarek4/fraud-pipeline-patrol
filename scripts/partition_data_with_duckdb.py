"""
Data Partitioning Script using DuckDB.

This script reads parquet files from data/raw/ and partitions them
into processed directory structures using DuckDB's partitioning features.
"""
import os
from pathlib import Path

import duckdb


def ensure_dirs(dirs):
    """Create each directory in `dirs` if it doesn't already exist."""
    for d in dirs:
        os.makedirs(d, exist_ok=True)


def main():
    """Partition raw data files using DuckDB into processed directory structure."""
    cwd = Path.cwd()
    processed_dir = cwd / "data" / "processed"
    raw_dir = cwd / "data" / "raw"

    print(f"processed_dir: {processed_dir}")
    print(f"raw_dir: {raw_dir}")

    # Connect to duckdb in memory
    con = duckdb.connect(database=":memory:")

    # Dynamically get file types from raw directory
    file_types = []
    for file_path in raw_dir.glob("*.parquet"):
        # Extract filename without extension
        file_type = file_path.stem
        file_types.append(file_type)

    print(f"Found files: {file_types}")

    partition_statement = ""
    # Create processed directory if it doesn't exist
    ensure_dirs([processed_dir])

    for file_type in file_types:
        con.execute(
            f"""
        CREATE TABLE IF NOT EXISTS {file_type} AS
        SELECT
            *
        FROM read_parquet('{raw_dir}/{file_type}.parquet')
        """
        )
        # @TODO Change hardcoded partition statements to dynamic ones.
        if file_type == "customers":
            partition_statement = "PARTITION_BY (AccountCreationMonth)"
        if file_type == "merchants":
            partition_statement = "PARTITION_BY (ingestion_date)"
        if file_type == "transactions":
            partition_statement = "PARTITION_BY (TimestampMonth)"
        if file_type == "login_attempts":
            partition_statement = "PARTITION_BY (LoginTimestampMonth)"

        print(f"Writing data to {processed_dir}")
        # Write partitions
        con.execute(
            f"""
            COPY {file_type} TO '{processed_dir}/{file_type}'
            (FORMAT parquet, {partition_statement}, OVERWRITE_OR_IGNORE)
        """
        )

        # Read: SELECT * FROM read_parquet('/Users/tro/Desktop/fraud-pipeline-patrol/data/processed/customers/**/*.parquet')


if __name__ == "__main__":
    main()
