FROM ubuntu:latest
RUN apt-get update \
  && apt-get install -y python3-pip python3-dev postgresql-client \
  && cd /usr/local/bin \
  && ln -s /usr/bin/python3 python \
  && pip3 install --upgrade pip

# Coping source in current directory into the image
# python:3-onbuild expects the source in /usr/src/app
COPY . /usr/src/app
WORKDIR /usr/src/app
RUN pip install -r requirements.txt
# Commands in a list
CMD ["python", "api.py"]
