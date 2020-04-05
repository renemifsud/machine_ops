FROM python:3.7.7-alpine3.11

LABEL MAINTAINER="René Mifsud <rm1421@live.mdx.ac.uk>"

RUN apk update
RUN apk add postgresql-dev gcc python3-dev musl-dev

COPY app.py /app/app.py
COPY routes /app/routes
COPY static /app/static
COPY req.txt /app/requirements.txt

RUN pip install -r /app/requirements.txt

WORKDIR /app

EXPOSE 5000

CMD [ "gunicorn", "-w", "1", "run:app", "-b", ":5000", "--reload" ]

