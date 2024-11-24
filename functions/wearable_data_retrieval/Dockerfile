# Use the AWS Lambda Python base image
FROM public.ecr.aws/lambda/python:3.12

# Install OS-level dependencies and PostgreSQL client
RUN microdnf install -y \
    postgresql-libs \
    && microdnf clean all

# Install Python dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy the Lambda function code
COPY lambda_function.py /var/task/
COPY shared/ /var/task/shared/

# Set the CMD to your Lambda handler function
CMD ["lambda_function.handler"]
