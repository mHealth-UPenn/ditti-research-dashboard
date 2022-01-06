# Getting Started

Make sure you have Docker installed and running. Create an empty postgres database using the development `postgres.env` file.

```sh
docker run -ditp 5432:5432 --name aws-pg --env-file postgres.env postgres
```

Save the following AWS credentials and variables in a file named `secret-aws.env`.

| Name                  | Value                                          |
| --------------------- |----------------------------------------------- |
| AWS_ACCESS_KEY_ID     | Your API access key ID                         |
| AWS_SECRET_ACCESS_KEY | Your API secret key                            |
| AWS_DEFAULT_REGION    | The region for targeting API calls (us-east-1) |
| AWS_TABLENAME_USER    | The DynamoDB User table name                   |
| AWS_TABLENAME_TAP     | The DynamoDB Tap table name                    |

Activate the Python virtual environment, install dependencies, and export credentials automatically with the deploy script.

```sh
source deploy.sh
```

Run the app.

```sh
flask run
```

# Testing

New changes must always be run through a set of unit tests. Unit tests have been written using `pytest`.
