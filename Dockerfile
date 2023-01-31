FROM python:3.9.14-slim-buster

WORKDIR /home/project/

COPY . .

RUN pip install --no-cache -r requirements.txt;

CMD python main.py