#!/bin/bash
source ./.env

if [ -z "$DATABRICKS_EXTERNAL_ID" ] || [ "$DATABRICKS_EXTERNAL_ID" == "0000" ]; then
    echo "=========================================="
    echo " ERROR: Missing External ID"
    echo "=========================================="
    echo " Please copy the generated External ID from Databricks"
    echo " and paste it into DATABRICKS_EXTERNAL_ID in your .env file."
    exit 1
fi

echo "=========================================="
echo " Part 2: Applying Databricks Trust Policy"
echo "=========================================="

echo "1. Fetching your AWS Account ID..."
MY_AWS_ACCOUNT=$(aws sts get-caller-identity --query Account --output text)

echo "2. Generating the final Databricks Trust Policy..."
cat <<EOF > final-trust-policy.json
{
 "Version": "2012-10-17",
 "Statement": [
  {
   "Effect": "Allow",
   "Principal": {
    "AWS": [
     "$DATABRICKS_UC_ROLE_ARN",
     "arn:aws:iam::${MY_AWS_ACCOUNT}:role/$ROLE_NAME"
    ]
   },
   "Action": "sts:AssumeRole",
   "Condition": {
    "StringEquals": {
     "sts:ExternalId": "$DATABRICKS_EXTERNAL_ID"
    }
   }
  }
 ]
}
EOF

echo "3. Applying the final Trust Policy to IAM Role ($ROLE_NAME)..."
aws iam update-assume-role-policy \
    --role-name $ROLE_NAME \
    --policy-document file://final-trust-policy.json

echo "4. Cleaning up temporary JSON files..."
rm final-trust-policy.json

echo "=========================================="
echo " PART 2 COMPLETE!"
echo " You can now return to Databricks and click 'Validate'!"
echo "=========================================="
