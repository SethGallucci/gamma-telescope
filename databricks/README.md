# MAGIC Gamma Telescope Medallion Pipeline

This directory contains a set of Databricks notebooks that implement an end-to-end **Lakehouse Medallion Architecture** pipeline for the MAGIC Gamma Telescope dataset. The workflow moves raw observational data through progressively refined layers (**Bronze → Silver → Gold**) and finishes with model training and deployment.

The notebooks are designed for **Databricks + Unity Catalog + Delta Lake + MLflow**.

## Medallion Flow

```text
S3 Raw Files
   ↓
s3_to_bronze.ipynb
   ↓
Bronze Table
   ↓
bronze_to_silver.ipynb
   ↓
Silver Table
   ↓
silver_to_gold.ipynb
   ↓
Gold Table
   ↓
gold_to_model.ipynb
   ↓
MLflow Registered Model + Serving Endpoint
````

# Notebook Breakdown

## 1. s3_to_bronze.ipynb

### Purpose

Ingests raw CSV chunks from Amazon S3 into a Delta Bronze table using **Databricks Auto Loader** and checkpointed streaming ingestion.

### What It Does

- Defines schema for raw telescope observations
- Reads headerless CSV files from S3
- Uses Auto Loader (`cloudFiles`)
- Writes streaming output into:

```sql
workspace.medallion_data.bronze_telescope
```

### Why This Matters

- Reliable incremental ingestion
- Schema-controlled raw storage
- Replayable ingestion pipeline
- Foundation for downstream processing


## 2. bronze_to_silver.ipynb

### Purpose

Transforms raw Bronze data into a cleaned, trusted Silver dataset.

### What It Does

#### Data Cleaning

- Renames columns to standardized snake_case
- Casts numeric fields to proper types
- Converts labels:

  - `g` → `Gamma`
  - `h` → `Hadron`

#### Data Quality

- Checks row / column counts
- Missing value summaries
- Exact duplicate detection
- Duplicate group reporting

#### Enrichment

Adds:
- `row_id`
- `duplicate_count`
- `is_duplicate_group`

#### Output

```sql
workspace.medallion_data.silver_telescope
```

## 3. silver_to_gold.ipynb

### Purpose

Creates a curated feature table for machine learning.

### What It Does

Uses previously selected BIC/AIC statistical feature selection results and keeps only high-value predictors:

```text
f_length
f_size
f_conc1
f_m3long
f_alpha
```

#### Additional Steps

- Selects target column (`class`)
- Saves compact ML-ready Delta table

#### Output

```sql
workspace.medallion_data.gold_telescope
```

## 4. gold_to_model.ipynb

### Purpose

Trains, logs, registers, and optionally deploys a logistic regression classifier.

### What It Does

#### Model Pipeline

- Loads Gold table
- Builds Spark ML pipeline:
  - VectorAssembler
  - Logistic Regression

#### Model Selection

- Cross-validation
- Hyperparameter tuning

#### Tracking

- Logs metrics to MLflow

#### Registration

Registers model in Unity Catalog:

```sql
workspace.medallion_data.lr_telescope_model
```

#### Optional Deployment

Creates Databricks Model Serving endpoint:

```text
magic-telescope-endpoint
```