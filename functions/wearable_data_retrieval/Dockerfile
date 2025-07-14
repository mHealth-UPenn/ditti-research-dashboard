####################
# EXTENSION LAYER #
####################

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

##################
# FUNCTION LAYER #
##################

# Use the AWS Lambda Python base image
FROM public.ecr.aws/lambda/python:3.13 AS function-layer

# Copy the AWS Parameters and Secrets Lambda Extension
COPY --from=extension-layer \
    extensions/bootstrap \
    /opt/extensions/aws-parameters-and-secrets-lambda-extension

# Install OS-level dependencies and PostgreSQL client
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

#####################
# DEVELOPMENT LAYER #
#####################

# Add a final layer only for development that allows for role assumption
FROM function-layer AS dev

# Install AWS CLI for role assumption
RUN dnf install -y unzip
RUN curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip" && \
    unzip awscliv2.zip && \
    ./aws/install

# Copy the entrypoint script for role assumption
COPY functions/wearable_data_retrieval/entrypoint.sh /var/task/entrypoint.sh
RUN chmod +x /var/task/entrypoint.sh

# Copy the Lambda function code
COPY functions/wearable_data_retrieval/lambda_function.py /var/task/lambda_function.py
COPY functions/wearable_data_retrieval/config.py /var/task/config.py
COPY shared/ /var/task/shared/

# Set the entrypoint for role assumption
ENTRYPOINT ["/var/task/entrypoint.sh"]
CMD ["lambda_function.handler"]

####################
# PRODUCTION LAYER #
####################

FROM function-layer AS prod

# Copy the entrypoint script for role assumption
COPY functions/wearable_data_retrieval/entrypoint.sh /var/task/entrypoint.sh
RUN chmod +x /var/task/entrypoint.sh

# Copy the Lambda function code
COPY functions/wearable_data_retrieval/lambda_function.py /var/task/lambda_function.py
COPY functions/wearable_data_retrieval/config.py /var/task/config.py
COPY shared/ /var/task/shared/

# Set the entrypoint for role assumption
CMD ["lambda_function.handler"]
