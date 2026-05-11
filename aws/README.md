# AWS S3 and IAM Setup for Databricks Unity Catalog

This repository contains a streamlined set of bash scripts designed to quickly provision, configure, and tear down an AWS S3 bucket and an IAM role for secure access via Databricks Unity Catalog.

## Prerequisites

* **AWS CLI:** Ensure the AWS CLI is installed and configured with appropriate permissions (`aws configure`) to create S3 buckets, IAM roles, and IAM policies.

## Files Overview

* `1_setup_aws_infra.sh`: Creates the S3 bucket, enforces security, and bootstraps the IAM role with a temporary trust policy.
* `2_apply_databricks_trust.sh`: Applies the final secure trust policy to the IAM Role using your Databricks External ID.
* `teardown.sh`: A cleanup script that removes the attached IAM policies, deletes the IAM role, and forcefully deletes the S3 bucket and all its contents.
* `.env.example`: A template for the required environment variables.

## Setup Instructions

Databricks requires us to provide them with our AWS Role ARN before they will generate a secure External ID. Because of this, the setup is split into two scripts.

### Step 1: Configure Initial Environment

1. Copy the example file to create your local `.env` file:
   ```bash
   cp .env.example .env
   ```
2. Open `.env` and fill in your specific details:
   * `BUCKET_NAME`: The globally unique name for your new S3 bucket.
   * `ROLE_NAME`: The name for your new IAM role.
   * `DATABRICKS_UC_ROLE_ARN`: Use the standard Databricks ARN (already provided in the example).
   * `DATABRICKS_EXTERNAL_ID`: **Leave this blank for now!**

3. Make the scripts executable:
   ```bash
   chmod +x *.sh
   ```

### Step 2: Create AWS Infrastructure
Run the first script:
```bash
./1_setup_aws_infra.sh
```
Upon success, this script will output your new `ROLE_ARN`.

### Step 3: Grab Your External ID from Databricks
1. Log into your Databricks Workspace.
2. In the left sidebar, click **Catalog** to open the Catalog Explorer.
3. Click the **gear/settings icon** at the top next to the "Catalog" heading, and select **Credentials**.
4. Click **Create credential**.
5. Set the **Credential type** to **AWS IAM Role**.
6. Give it a name (e.g., `telescope-s3-credential`).
7. In the **IAM role (ARN)** field, paste the **`ROLE_ARN`** you got from Step 2.
8. Click **Create**.
9. A "Credential created" dialog will pop up. **Copy the External ID** shown here.
10. Click **Done**. 

*(Note: Do not click Validate yet! It will fail until we finish Step 4).*

### Step 4: Apply Final Trust Policy
1. Open your local `.env` file.
2. Paste the External ID you just copied into the `DATABRICKS_EXTERNAL_ID` variable and save (do not leave it blank anymore).
3. Run the second script:
   ```bash
   ./2_apply_databricks_trust.sh
   ```

Once this script completes, you can go back to Databricks, select your credential, and click **Validate Configuration**. It should now pass.

## Creating the External Location
The last thing you need to do is point Databricks to your S3 bucket.

1. Still in the Catalog Explorer, click that same **gear/settings icon** again.
2. Under the "Connect" section, click on **External locations**.
3. Click **Create location**.
4. Give it a name (e.g., `telescope-data`).
5. In the **URL** field, enter your S3 bucket path using the `s3://` prefix (e.g., `s3://your-bucket-name`).
6. In the **Storage credential** dropdown, select the credential you created in Step 3.
7. Click **Save**. 

*(Optional) To allow other users to access this data, go to the **Permissions** tab of your new External Location and grant `READ FILES`, `WRITE FILES`, or `CREATE EXTERNAL TABLE` privileges as needed.*

## Cleanup / Teardown
If you need to destroy the AWS infrastructure created by this repository, run the teardown script:
```bash
./teardown.sh
```
**Warning:** This will forcefully delete the S3 bucket and *all data inside it*, as well as the IAM role and policies.