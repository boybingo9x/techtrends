# set the base image. Since we're running 
# a Python application a Python base image is used
FROM python:3.8
LABEL maintainer="Quyet Trinh"
COPY . /app
WORKDIR /app/techtrends
RUN python ./init_db.py
RUN pip install -r ./requirements.txt
EXPOSE 3111
CMD [ "python", "./app.py" ]
