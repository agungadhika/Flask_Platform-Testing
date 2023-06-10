FROM python:latest

WORKDIR  /app

# install python dependencies
COPY requirements.txt ./requirements.txt
RUN pip install -r requirements.txt

# copy file
COPY ./static/ ./static/
COPY ./templates/ ./templates/
COPY ./app.py .
COPY ./database.db .

EXPOSE 5000
ENV FLASK_RUN_HOST="0.0.0.0"
ENV FLASK_DEBUG=1
CMD [ "flask", "run" ]
