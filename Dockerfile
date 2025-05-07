FROM public.ecr.aws/lambda/python:3.12

WORKDIR /var/task

ENV PYTHONUNBUFFERED=1
ENV FLASK_APP=run.py
ENV ZAPPA_RUNNING_IN_DOCKER=True

RUN pip3 install --upgrade pip && pip3 install wheel
RUN pip3 install boto3==1.38.10 \
    Authlib==1.5.2 \
    Flask==3.1.0 \
    Flask-Caching==2.3.1 \
    Flask-Cors==5.0.1 \
    Flask-JWT-Extended==4.7.1 \
    Flask-Migrate==4.1.0 \
    Flask-SQLAlchemy==3.1.0 \
    nh3==0.2.21 \
    oauthlib==3.2.2 \
    pandas==2.2.2 \
    psycopg2-binary==2.9.10 \
    pydantic==2.8.2 \
    python-dotenv==1.1.0 \
    requests-aws4auth==1.2.3 \
    SQLAlchemy==2.0.31 \
    XlsxWriter==3.2.3 \
    zappa==0.59.0

COPY . ${LAMBDA_TASK_ROOT}

RUN cp $(python -c "from zappa import handler;print(handler.__file__)") .

CMD ["handler.lambda_handler"]
