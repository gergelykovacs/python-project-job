# Infrastructure as Code (IaC) Placeholder

- Terraform
- CloudFormation
- Ansible
- Puppet
- Chef
- Etc.

Example structure for Terraform:

```text
infrastructure/
 `- terraform/
   |- backend/
   |  `- template.json
   |- modules/
   |- params/
   |  |- <account1>_<environment1>_<region1>.tfvars
   |  `- <account2>_<environment2>_<region2>.tfvars
   |- 00-variables.tf
   |- 01-outputs.tf
   |- 02-providers.tf
   |- 03-locals.tf
   |- 04-main.tf
   |- 10-iam.tf
   |- 20-vpc.tf
   |- 30-s3.tf
   |- 40-lambda.tf
   |- ... etc ...
   |- .gitignore
   |- Makefile
   `- README.md
   
   ACCOUNT_NAME=staging ENV=stg2 REGION=eu-west-2 make plan
   ACCOUNT_NAME=staging ENV=stg2 REGION=eu-west-2 make apply
   
   ACCOUNT_NAME=production ENV=prod1 REGION=eu-west-1 make plan
   ACCOUNT_NAME=production ENV=prod1 REGION=eu-west-1 make apply
```