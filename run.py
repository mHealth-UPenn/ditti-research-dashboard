import os

# if the app is running in a production environment
if os.getenv("FLASK_CONFIG") == "Production":
    import json
    import boto3

    # get the secret"s values
    client = boto3.client("secretsmanager")
    secret_id = os.getenv("AWS_SECRET_NAME")
    res = client.get_secret_value(SecretId=secret_id)
    secret = json.loads(res["SecretString"])

    # export the secret"s values as envirnoment variables
    for k, v in secret.items():
        os.environ[k] = v

# import the app after the environment variables are exported
from aws_portal.app import create_app

app = create_app()

if __name__ == "__main__":
    app.run()
