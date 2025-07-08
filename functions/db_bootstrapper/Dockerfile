FROM public.ecr.aws/lambda/python:3.12

WORKDIR /var/task

RUN pip3 install --upgrade pip && pip3 install wheel
RUN pip3 install boto3 \
    cfnresponse==1.1.5 \
    Flask==2.3.3 \
    Flask-Migrate \
    "Flask-SQLAlchemy>=3.0,<3.1" \
    psycopg2-binary \
    "SQLAlchemy>=2.0,<2.1"

COPY migrations/ migrations/
COPY shared/iam_sqlalchemy.py shared/iam_sqlalchemy.py
COPY functions/db_bootstrapper/backend backend/
COPY backend/models.py backend/models.py
COPY functions/db_bootstrapper/lambda_handler.py lambda_handler.py
COPY functions/db_bootstrapper/load_data.py load_data.py
COPY functions/db_bootstrapper/db_uri.py db_uri.py

CMD ["lambda_handler.lambda_handler"]
