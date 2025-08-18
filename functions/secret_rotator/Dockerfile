FROM public.ecr.aws/lambda/python:3.12

WORKDIR ${LAMBDA_TASK_ROOT}

COPY functions/secret_rotator/handler.py .
COPY functions/secret_rotator/requirements.txt .
RUN pip install -r requirements.txt

CMD [ "handler.lambda_handler" ] 
