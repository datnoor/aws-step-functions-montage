#!/usr/bin/env bash
set -e
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
MONTAGE_DATA_DIR="./data/0.25"

# If zip artefact already exists, back it up
if [ -f $SCRIPT_DIR/lambda.zip ]; then
    mv $SCRIPT_DIR/lambda.zip $SCRIPT_DIR/lambda.zip.backup
fi

python dag_to_step_functions.py $MONTAGE_DATA_DIR/workdir/dag.json step-function.json montage-lambda-bucket "\${lambda-arn}"

# Add lambda code in zip file
zip -jr $SCRIPT_DIR/lambda.zip $SCRIPT_DIR/executor/bin
zip -j $SCRIPT_DIR/lambda.zip $SCRIPT_DIR/executor/package.json
zip -j $SCRIPT_DIR/lambda.zip $SCRIPT_DIR/executor/MontageExecutor.js

cd executor
npm install
zip -r $SCRIPT_DIR/lambda.zip node_modules/*

cd $SCRIPT_DIR

# Download terraform scripts
wget https://raw.githubusercontent.com/szwojtkowski/aws-step-functions-terraform/master/executor.tf
wget https://raw.githubusercontent.com/szwojtkowski/aws-step-functions-terraform/master/variables.tf

# Run terraform
terraform init
terraform apply

# Upload montage input data to s3 bucket
aws s3 sync $MONTAGE_DATA_DIR/input s3://montage-lambda-bucket/data/input

