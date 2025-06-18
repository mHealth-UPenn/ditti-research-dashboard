FROM python:3.12

# Install moto
RUN pip install \
    boto3 \
    flask \
    flask-cors \
    moto \
    multipart \
    openapi_spec_validator

ENTRYPOINT ["moto_proxy", "--host", "0.0.0.0"]
