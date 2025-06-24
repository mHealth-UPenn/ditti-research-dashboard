FROM public.ecr.aws/lambda/python:3.12

WORKDIR ${LAMBDA_TASK_ROOT}

COPY handler.py .
COPY requirements.txt .
RUN pip install -r requirements.txt

CMD [ "handler.lambda_handler" ] 