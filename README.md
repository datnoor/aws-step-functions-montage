# Montage workflow execution with AWS Step Functions

Requirements :

- python >= 3.0
- npm
- terraform
- aws-cli (with configured credentials)

Running deployment script :
 
 ``` 
 ./deploy.sh 
 ```
 
 - converts a dag.json file (containing a Montage workflow definition) to the AWS Step Function definition
 - downloads all dependencies defined in `executor/package.json` required by AWS Lambda executor function (using `npm`)
 - creates an archive with the Montage steps executor and Montage executable binaries as AWS Lambda function
 - downloads terraform deployment scripts from [szwojtkowski/aws-step-functions-terraform](https://github.com/szwojtkowski/aws-step-functions-terraform)
 - configures and deploys the whole required AWS setup - policies, roles, buckets, lambdas and step functions
 - uploads Montage workflow input data to AWS S3 using aws-cli
 
 Running clean script :
 
 ``` 
 ./clean.sh 
 ```
 
 - destroys the AWS configuration created during the deployment
 - removes all temporary files