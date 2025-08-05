import os
from typing import TypedDict

from shared.lambda_logger import LambdaLogger
from shared.lambda_secrets_provider import SecretProvider

LOCAL = os.getenv("LOCAL", "false") == "true"

required_env_vars = [
    "S3_BUCKET_NAME",
    "DB_URI",
]

missing_env_vars = [var for var in required_env_vars if var not in os.environ]
if missing_env_vars:
    raise ValueError(
        f"Missing required environment variables: {missing_env_vars}"
    )


nonlocal_required_env_vars = [
    "FITBIT_TOKENS_SECRET_NAME",
    "FITBIT_SECRET_NAME",
]

missing_nonlocal_env_vars = [
    var for var in nonlocal_required_env_vars if var not in os.environ
]
if missing_nonlocal_env_vars and not LOCAL:
    raise ValueError(
        f"Missing required environment variables: {missing_nonlocal_env_vars}"
    )


class FitbitConfig(TypedDict):
    client_id: str
    client_secret: str


class DBConfig(TypedDict):
    uri: str
    use_iam: bool


class S3Config(TypedDict):
    bucket_name: str


class Config(TypedDict):
    db: DBConfig
    fitbit: FitbitConfig | None
    s3: S3Config
    log_level: str
    local: bool
    fitbit_tokens_secret_name: str | None


def load_config(logger: LambdaLogger) -> Config:
    fitbit_secret = None
    if fitbit_secret_name := os.getenv("FITBIT_SECRET_NAME"):
        fitbit_secret = SecretProvider[FitbitConfig](
            secret_name=fitbit_secret_name
        ).get_secret()

    config = Config(
        db=DBConfig(
            uri=os.getenv("DB_URI"),
            use_iam=os.getenv("DB_USE_IAM", "false") == "true",
        ),
        s3=S3Config(
            bucket_name=os.getenv("S3_BUCKET_NAME"),
        ),
        fitbit=fitbit_secret.secret_dict if fitbit_secret else None,
        fitbit_tokens_secret_name=os.getenv("FITBIT_TOKENS_SECRET_NAME"),
        log_level=os.getenv("LOG_LEVEL", "INFO"),
        local=LOCAL,
    )

    logger.debug(
        "Config loaded:",
        extra={
            **config,
            "fitbit": {
                "client_id": config["fitbit"]["client_id"],
                "client_secret": "********",
            }
            if not LOCAL
            else None,
        },
    )

    return config
