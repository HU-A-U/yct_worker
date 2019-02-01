FROM python:3.7
ADD requirements.txt /tmp/requirements.txt
RUN pip install -r /tmp/requirements.txt
RUN mkdir /code
WORKDIR /code
COPY . /code
COPY docker-entrypoint.sh docker-entrypoint.sh
RUN chmod +x docker-entrypoint.sh
RUN apt-get install libfontconfig

EXPOSE 8080

CMD /code/docker-entrypoint.sh
