# Dockerfiles

All Lambda functions must use a multi-stage Docker build. Each Dockerfile assumes that its build context includes the root project folder to allow access to the `shared` folder to copy shared utils. Building an image requires the `-f functions/{function_name}/Dockerfile` command line option.

## Extension Layer

If using using any Lambda extensions, an `extension-layer` is used to prepare the extensions. For example, to include the AWS Parameters and Secrets Lambda Extension:

```dockerfile
FROM ubuntu:latest AS extension-layer

# Use us-east-1 as the default region
ARG AWS_DEFAULT_REGION="us-east-1"
ENV AWS_DEFAULT_REGION=${AWS_DEFAULT_REGION}

RUN apt-get update && apt-get install -y unzip curl

# Install AWS CLI
RUN curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip" && \
    unzip awscliv2.zip && \
    ./aws/install

# Download the AWS Parameters and Secrets Lambda Extension
RUN --mount=type=secret,id=aws,target=/root/.aws/credentials \
    EXTENSION_DOWNLOAD_ARN="arn:aws:lambda:us-east-1:177933569100:layer:AWS-Parameters-and-Secrets-Lambda-Extension:17" && \
    EXTENSION_DOWNLOAD_URL=$(aws lambda get-layer-version-by-arn \
        --arn $EXTENSION_DOWNLOAD_ARN \
        --query 'Content.Location' \
        --output text \
        --region $AWS_DEFAULT_REGION) && \
    curl -o aws-parameters-and-secrets-lambda-extension.zip $EXTENSION_DOWNLOAD_URL && \
    unzip -q aws-parameters-and-secrets-lambda-extension.zip
```

AWS credentials can be mounted as a secret at build time with `--secret id=aws,src=$HOME/.aws/credentials`.

## Function Layer

A function layer loads the base Lambda image, copies extensions, and installs dependencies. For example:

```dockerfile
FROM public.ecr.aws/lambda/python:3.13 AS function-layer

# Copy the AWS Parameters and Secrets Lambda Extension
COPY --from=extension-layer \
    extensions/bootstrap \
    /opt/extensions/aws-parameters-and-secrets-lambda-extension

# Install OS-level dependencies
RUN microdnf install -y \
    postgresql-libs \
    && microdnf clean all

# Install Python dependencies
RUN pip3 install --upgrade pip && pip3 install wheel
RUN pip3 install boto3==1.34.144 \
    oauthlib==3.2.2 \
    psycopg2-binary \
    requests==2.32.3 \
    "SQLAlchemy>=2.0,<2.1"
```

## Development and Production Layers

A production, and optionally development, layer can be used to copy source code.

```dockerfile
FROM function-layer AS prod

# Copy the Lambda function code
COPY functions/{function_name}/lambda_function.py
COPY shared/ /var/task/shared/

# Set the entrypoint
CMD ["lambda_function.handler"]
```
