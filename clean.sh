#!/usr/bin/env bash

aws s3 rm s3://montage-lambda-bucket/data --recursive

# Destroy terraform configuration
terraform destroy

rm *.tf
rm *.tfstate
rm lambda.zip
rm step-function.json
rm -r executor/node_modules
rm executor/package-lock.json

