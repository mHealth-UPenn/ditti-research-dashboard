# Use the AWS Lambda Python base image
FROM public.ecr.aws/lambda/python:3.12

# Install OS-level dependencies and PostgreSQL client
RUN yum install -y \
    postgresql-libs \
    && yum clean all

# Install Python dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy the Lambda function code
COPY . .

# Set the CMD to your Lambda handler function
CMD ["lambda_function.handler"]
