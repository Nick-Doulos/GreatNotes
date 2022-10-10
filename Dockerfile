FROM python:3.7.8
RUN apt update -y
RUN apt upgrade -y
RUN mkdir /DigitalNotes

WORKDIR /DigitalNotes

COPY requirements.txt .
COPY app.py .
COPY users.json .
COPY notes.json .

ADD templates ./templates
ADD pys ./pys

RUN pip install -r requirements.txt

ENTRYPOINT [ "python", "-u", "app.py" ]
