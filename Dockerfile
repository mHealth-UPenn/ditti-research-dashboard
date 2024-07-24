FROM public.ecr.aws/lambda/python:3.12

WORKDIR /var/task

ENV PYTHONUNBUFFERED=1
ENV FLASK_APP=run.py
ENV ZAPPA_RUNNING_IN_DOCKER=True

COPY requirements.txt ${LAMBDA_TASK_ROOT}
RUN pip3 install --upgrade pip && pip3 install wheel
RUN pip3 install -r requirements.txt

COPY . ${LAMBDA_TASK_ROOT}
RUN rm requirements.txt

RUN cp $(python -c "from zappa import handler;print(handler.__file__)") .

CMD ["handler.lambda_handler"]
