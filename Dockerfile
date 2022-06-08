FROM public.ecr.aws/lambda/python:3.8

WORKDIR /var/task

ENV PYTHONUNBUFFERED=1
ENV FLASK_APP=run.py

COPY requirements.txt .
RUN pip3 install --upgrade pip && pip3 install wheel
RUN pip3 install -r requirements.txt

COPY . .
RUN rm requirements.txt

RUN cp $(python -c "from zappa import handler;print(handler.__file__)") .

CMD handler.lambda_handler
