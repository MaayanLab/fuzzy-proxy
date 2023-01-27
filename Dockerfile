FROM python

ADD requirements.txt /requirements.txt
RUN pip install -r /requirements.txt

COPY . /app
WORKDIR /app

EXPOSE 8080

CMD gunicorn --bind 0.0.0.0:8080 -w 4 app:app
