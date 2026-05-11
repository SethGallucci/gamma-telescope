#!/bin/bash
source ./.env

echo "=========================================="
echo " Part 1: AWS Infrastructure Setup"
echo "=========================================="

echo "1. Creating S3 bucket: $BUCKET_NAME..."
aws s3 mb s3://$BUCKET_NAME

echo "2. Blocking all public access for security..."
aws s3api put-public-access-block \
    --bucket $BUCKET_NAME \
    --public-access-block-configuration "BlockPublicAcls=true,IgnorePublicAcls=true,BlockPublicPolicy=true,RestrictPublicBuckets=true"

echo "3. Fetching your AWS Account ID..."
MY_AWS_ACCOUNT=$(aws sts get-caller-identity --query Account --output text)

echo "4. Creating temporary Trust Policy (with internal placeholder)..."
cat <<EOF > temp-trust-policy.json
{
 "Version": "2012-10-17",
 "Statement": [
  {
   "Effect": "Allow",
   "Principal": {
    "AWS": [
     "$DATABRICKS_UC_ROLE_ARN",
     "arn:aws:iam::${MY_AWS_ACCOUNT}:root"
    ]
   },
   "Action": "sts:AssumeRole",
   "Condition": {
    "StringEquals": {
     "sts:ExternalId": "0000"
    }
   }
  }
 ]
}
EOF

echo "5. Creating the IAM Role ($ROLE_NAME)..."
ROLE_ARN=$(aws iam create-role \
    --role-name $ROLE_NAME \
    --assume-role-policy-document file://temp-trust-policy.json \
    --query 'Role.Arn' --output text)

echo "6. Creating the S3 Access Policy..."
cat <<EOF > s3-permission-policy.json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "s3:GetObject",
                "s3:PutObject",
                "s3:DeleteObject",
                "s3:ListBucket",
                "s3:GetBucketLocation"
            ],
            "Resource": [
                "arn:aws:s3:::$BUCKET_NAME",
                "arn:aws:s3:::$BUCKET_NAME/*"
            ]
        }
    ]
}
EOF

echo "7. Attaching S3 Policy to the Role..."
aws iam put-role-policy \
    --role-name $ROLE_NAME \
    --policy-name S3-Telescope-Access \
    --policy-document file://s3-permission-policy.json

echo "8. Cleaning up temporary JSON files..."
rm temp-trust-policy.json s3-permission-policy.json

echo "=========================================="
echo " PART 1 COMPLETE!"
echo " Bucket Name: $BUCKET_NAME"
echo " Role ARN: $ROLE_ARN"
echo "=========================================="
echo "NEXT STEPS:"
echo "1. Go to Databricks and create a Storage Credential using the Role ARN above."
echo "2. Copy the generated External ID from Databricks."
echo "3. Open your .env file and set DATABRICKS_EXTERNAL_ID to that new value."
echo "4. Run ./2_apply_databricks_trust.sh"
