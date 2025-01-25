FROM public.ecr.aws/lambda/python:3.12

WORKDIR /var/task

ENV PYTHONUNBUFFERED=1
ENV FLASK_APP=run.py
ENV ZAPPA_RUNNING_IN_DOCKER=True

RUN pip3 install --upgrade pip && pip3 install wheel
RUN pip3 install boto3 \
    Flask==2.3.3 \
    Flask-APScheduler \
    Flask-Bcrypt \
    Flask-Caching \
    Flask-Cors \
    Flask-JWT-Extended \
    Flask-Migrate \
    Flask-SQLAlchemy==2.5.1 \
    html-sanitizer \
    oauthlib \
    pandas \
    psycopg2-binary \
    pydantic \
    requests \
    requests-aws4auth \
    SQLAlchemy==1.4.52 \
    zappa

COPY . ${LAMBDA_TASK_ROOT}

RUN cp $(python -c "from zappa import handler;print(handler.__file__)") .

CMD ["handler.lambda_handler"]
