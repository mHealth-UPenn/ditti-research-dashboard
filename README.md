# aws-portal

This Flask/React single page application is a convenient dashboard that can be used to interact with data stored on AWS DynamoDB. In production, the React frontend is statically hosted on S3 and provisioned through a secure HTTPS connection with CloudFront. The Flask backend is deployed with Zappa as a Lambda function and interfaces with a PostgreSQL database that is hosted using RDS. To minimize running costs, `rds_stopper.py` includes a function that stops the RDS instance after the application has been inactive for two hours. `rds_stopper.py` is scheduled by Zappa to run hourly.

## Prerequisites

Four deployment scripts (`deploy-dev.sh`, `deploy-prod.sh`, `react-build-dev.sh`, and `react-build-prod.sh`) are included for convenience and must be run in a Linux OS, WSL, Git Bash, or other platforms that provide a bash shell. If using Windows, WSL is recommended. Ensure Node.js, Docker, and the AWS CLI are installed. If using Windows, Python must also be installed. Configure the AWS CLI (see: https://docs.aws.amazon.com/cli/latest/userguide/cli-chap-configure.html).

## Deploy Locally

Ensure Docker is installed and running. Create an empty PostgreSQL database using the development `postgres.env` file.

```sh
docker run -ditp 5432:5432 --name aws-pg --env-file postgres.env postgres
```

Initialize the database (only must be done once per postgres container)

```sh
docker exec -it aws-pg psql -U user -d postgres < default.sql
flask init-admin
```

Save the following AWS credentials and variables in a file named `secret-aws.env`.

| Name               | Value                        |
| ------------------ | ---------------------------- |
| APP_SYNC_API_KEY   | The AppSync API Key          |
| APP_SYNC_HOST      | The AppSync host             |
| AWS_TABLENAME_USER | The DynamoDB User table name |
| AWS_TABLENAME_TAP  | The DynamoDB Tap table name  |

Activate the Python virtual environment, install dependencies, and export credentials automatically with the development deploy script and run the app.

```sh
source deploy-dev.sh
flask run
```

Run the React frontend.

```sh
cd aws_portal/frontend
npm run start
```

The app can now be accessed at `localhost:3000`. `localhost` must be used for JWT token authentication to work properly in the development environment.

## Testing

New changes must always be run through a set of unit tests. Unit tests have been written using `pytest`.

## The Production Deploy Scripts

The Lambda deploy script `deploy-prod.sh` will run pytest, build and push the app's Docker image, and deploy the app as a Lambda function using Zappa. If the app is already deployed, the deploy script will instead update the existing deployment with any changes. Before running the script, ensure Docker is running, your AWS CLI is configured, and you are using a shell that supports bash (e.g., a Linux OS, WSL, or Git Bash). The script can be run with the following options:

| Option     | Description                                               |
| ---------- | --------------------------------------------------------- |
| --no-tests | Don't run pytest                                          |
| --no-build | Don't build or push the Docker image                      |
| --no-cache | Build the Docker image with the --no-cache option enabled |
| -t/--tag   | Use a different image tag (default: latest)               |

The React deploy script `react-build-prod.sh` will run `npm run build`, automatically copy frontend static files to your S3 bucket, and run an invalidation on your CloudFront distribution. The invalidation will update your distribution's cache with your latest build.

## Deploy for Production

Before completing the following steps, create a file named `secret-deploy.env` in the same folder as the four deploy scripts. While setting up the production environment with the following steps, save the following variables in this file.

| Name                           | Value                                                                                                                                                                       |
| ------------------------------ | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| AWS_REGION                     | The region in which all AWS resources will be deployed (e.g., us-east-1). **Note:** all resources must be deployed in this region                                           |
| AWS_ACCOUNT_ID                 | Your 12-digit account ID. This can be obtained by clicking your account name at the top right corner of the AWS console. Do not include dashes                              |
| AWS_BUCKET                     | The name of your S3 bucket                                                                                                                                                  |
| AWS_CLOUDFRONT_DISTRIBUTION_ID | The ID of your CloudFront distribution                                                                                                                                      |
| AWS_CLOUDFRONT_DOMAIN_NAME     | The endpoint URL of your CloudFront distribution, including https://. This can be obtained from your distribution's dashboard, under **Details > Distribution domain name** |
| AWS_ECR_REPO_NAME              | The name of your Elastic Container Registry repository                                                                                                                      |

It is recommended you tag all AWS resources while you create them. This will simplify management and tracking of all resources that are related to this app.

### Set Up Static Hosting with S3 and CloudFront

Create an S3 bucket.

1. Navigate to the S3 dashboard (https://s3.console.aws.amazon.com/s3) and click **Create bucket**.
2. Enter a bucket name and select your AWS region.
3. Under **Block Public Access settings for this bucket**, deselect **Block _all_ public access**.
4. Click **Create bucket**.

Enable static web hosting on the bucket you just created.

1. Open the bucket you just created.
2. Click **Properties**.
3. Scroll to **Static website hosting** and click **Edit**.
4. Under **Static website hosting**, click **Enable**.
5. For **Index document**, enter **index.html**.
6. Click **Save changes**.

Create a CloudFront distribution with your S3 bucket as its origin.

1. Navigate to the CloudFront dashboard (https://us-east-1.console.aws.amazon.com/cloudfront) and click **Create distribution**.
2. Click on the **Origin domain** field. Under **Amazon S3**, select the bucket you just created. It should appear as **bucket name**.s3.amazonaws.com.
3. Under **S3 bucket access**, select **Yes use OAI**.
4. Under **Origin access identity**, select **Create new OAI** and click **Create**.
5. Under **Default cache behavior > Viewer > Viewer protocol policy**, select **HTTPS only**.
6. Under **Settings > Price class**, select your preferred price class. Use only North America and Europe is recommended.
7. For **Default root object**, enter **index.html**.
8. Click **Create distribution**.

Create an access policy on your S3 bucket that allows your CloudFront distribution to get objects.

1. In the left navigation bar, under **Security**, click **Origin access identities**.
2. Copy the **ID** of the OAI that you just created.
3. Navigate to the S3 dashboard (https://s3.console.aws.amazon.com/s3) and open your bucket.
4. Click **Permissions**.
5. Scroll to **Bucket policy** and click **Edit**.
6. In the **Policy** field, paste the following text. Replace **ID** with the the OAI ID that you just copied and **Bucket Name** with the name of your bucket.

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "PublicReadGetObject",
      "Effect": "Allow",
      "Principal": {
        "AWS": "arn:aws:iam::cloudfront:user/CloudFront Origin Access Identity ID"
      },
      "Action": "s3:GetObject",
      "Resource": "arn:aws:s3:::Bucket Name/*"
    }
  ]
}
```

7. Click **Save changes**.

### Create an Elastic Container Registry repository

1. Navigate to the ECR dashboard (https://us-east-1.console.aws.amazon.com/ecr) and click **Create repository**.
2. Enter a name for your repository and click **Create repository**.

### Create a Relational Database Service Instance

The following steps will create a database with the cheapest configuration available, which is sufficient for small and intermittent workloads.

1. Navigate to the RDS dashboard (https://console.aws.amazon.com/rds) and click **Create database**.
2. Under **Engine options > Engine type**, select **PostgreSQL**.
3. Scroll to **Availability and durability**. Under **Deployment options**, select **Single DB instance**.
4. Scroll to **Settings**. Enter a database identifier and a master password. **Note:** This password will grant external access to your database. It is _strongly_ recommended you randomly generate and save this password using a password manager.
5. Scroll to **Instance configuration**. Under **DB instance class**, select **Burstable classes**. In the dropdown menu, select **db.t3.micro**.
6. Scroll to **Storage**. In the dropdown menu under **Storage type**, select **General Purpose SSD (gp2)**.
7. Under **Storage autoscaling**, deselect **Enable storage scaling**.
8. Scroll to **Connectivity**. Under **Public access**, select **Yes**.
9. Scroll to **Additional configuration** and open the additional configuration menu.
10. For **Database options > Initial database name**, enter **postgres**.
11. Under **Performance insights**, deselect **Turn on Performance Insights**.
12. Under **Monitoring**, deselect **Enable Enhanced monitoring**.
13. Under **Log exports**, select **PostgreSQL log**.
14. Click **Create database**.

Create an inbound rule on your database's VPC that allows inbound requests.

1. Open the database instance you just created.
2. Scroll to **Connectivity & security**. Click the link under **Security > VPC security groups**.
3. Click the **Actions** dropdown menu at the top of the screen and select **Edit inbound rules**.
4. Click **Add rule**.
5. In the **Type** dropdown menu of the rule that you just added, select **PostgreSQL**.
6. In the **Source** dropdown menu of the rule that you just added, select **Anywhere-IPv4**.
7. Click **Save rules**.

### Initialize the Database

:warning: **Only run these commands once**. Running any of these commands a second time can have unintended consequences.

Then, use a postgres docker container to initialize the remote database using the `default.sql` file. Replace **Password** with the master password that you created your database with. **Database Endpoint** can be retrieved from your database's dashboard under **Connectivity & Security > Endpoint & port > Endpoint**. Note that the database endpoint will only be available after the database finishes creating.

```sh
docker run -dit --env-file postgres.env -e PGPASSWORD=Password --name temp-db postgres
docker exec -i temp-db psql -U postgres -d postgres -h Database Endpoint < default.sql
```

Run the flask command to create an admin account. Replace **URI** with the SQLAlchemy database URI (postgresql://postgres:**Password**@**Database Endpoint**/postgres). Replace **Admin Email** and **Admin Password** with your desired admin login credentials.

```sh
flask init-admin --uri URI --email Admin Email --password Admin Password
```

### Deploy the Flask Backend to Lambda

Ensure Docker is running, your AWS CLI is configured, and all variables are saved in `secret-deploy.env`. From command line that supports bash, run a test database container, deploy the development environment, and run the deploy script. Do not open the deployment's URL until after the following steps are complete.

```sh
docker run -ditp 5432:5432 --name test-db --env-file postgres.env postgres
source deploy-dev.sh
./deploy-prod.sh
```

Optionally remove the test database when finished with deployment.

```sh
docker stop test-db
docker rm test-db
```

### Create a Secret Using Secrets Manager

1. Navigate to the Secrets Manager dashboard (https://us-east-1.console.aws.amazon.com/secretsmanager) and click **Store a new secret**.
2. Under **Secret type**, select **Other type of secret**.
3. Under **Key/value pairs**, enter the following rows. For the SQLAlchemy database URI, replace **Password** with the master password that you created your database with. **Database Endpoint** can be retrieved from your database's dashboard under **Connectivity & Security > Endpoint & port > Endpoint**.

| Key                        | Value                                                                                          |
| -------------------------- | ---------------------------------------------------------------------------------------------- |
| APP_SYNC_API_KEY           | The AppSync API Key                                                                            |
| APP_SYNC_HOST              | The AppSync host                                                                               |
| AWS_TABLENAME_USER         | The DynamoDB User table name                                                                   |
| AWS_TABLENAME_TAP          | The DynamoDB Tap table name                                                                    |
| AWS_DB_INSTANCE_IDENTIFIER | The DB identifier of your database instance                                                    |
| FLASK_DB                   | The SQLAlchemy database URI: postgresql://postgres:**Password**@**Database Endpoint**/postgres |

5. Click **Next**.
6. For **Secret name**, enter **secret-aws-portal** and click **Next**.
7. Click **Next** again, then click **Store**.

### Allow Your Lambda Function to Access Your Secret and Database

1. Navigate to the Lambda dashboard (https://us-east-1.console.aws.amazon.com/lambda) and under **Functions**, click **aws-portal-app**.
2. Click **Configuration** and in the left navigation bar click **Permissions**.
3. Click the link under **Execution role > Role name**.
4. In the **Add permissions** dropdown menu, select **Create inline policy**.
5. Click **JSON**.
6. In the text field, past the following text. Replace **Secret ARN** and **Database ARN** with the ARNs of your secret and database instance. Your secret's ARN can be retrieved from your secret's dashboard, under **Secret details > Secret ARN**. Your database instance's ARN can be retrieved from your database instance's dashboard (click **Configuration** and it can be found under **Configuration > Amazon Resource Name (ARN)**).

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": "secretsmanager:GetSecretValue",
      "Resource": "Secret ARN"
    },
    {
      "Effect": "Allow",
      "Action": "rds:*",
      "Resource": "Database ARN"
    }
  ]
}
```

7. Click **Review policy**.
8. Enter a name for your policy and click **Create policy**.

### Deploy the React Frontend to S3

1. Create an .env file named `secret-react.env` and save the following variables in the file. The app's API Gateway URL can be found by running `zappa status app | grep "API Gateway URL"`.

| Name                   | Value                     |
| ---------------------- | ------------------------- |
| REACT_APP_FLASK_SERVER | The app's API Gateway URL |

2. Run the React deploy script.

```sh
./react-build-prod.sh
```

### Updating and Undeploying

Any changes can be automatically applied to the deployed app using either of the production deployment scripts (`deploy-prod.sh` and `react-build-prod.sh`).

If you wish to undeploy the app from Lambda, run `zappa undeploy app`. **Note:** If you run the deploy script again after undeploying the app, the Flask backend must be accessed with a new URL. You must update the `secret-react.env` file with the new URL in Step 1 of "Deploy the React Frontend to S3" and rerun the React deploy script.
