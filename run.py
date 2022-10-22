import os

if os.getenv('FLASK_CONFIG') == 'Production':
    import json
    import boto3

    client = boto3.client('secretsmanager')
    secret_id = os.getenv('AWS_SECRET_NAME')
    res = client.get_secret_value(SecretId=secret_id)
    secret = json.loads(res['SecretString'])

    for k, v in secret.items():
        os.environ[k] = v

from aws_portal.app import create_app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True)
