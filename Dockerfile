FROM python:3.7
ADD requirements.txt /tmp/requirements.txt
RUN pip install -r /tmp/requirements.txt
RUN mkdir /code
WORKDIR /code
COPY . /code
COPY docker-entrypoint.sh docker-entrypoint.sh
RUN chmod +x docker-entrypoint.sh
RUN apt-get install libfontconfig

ENV P_QUEUE to_product
ENV A_QUEUE to_analysis
ENV C_QUEUE to_consume
ENV QUEUE to_product

CMD /code/docker-entrypoint.sh
#ENTRYPOINT ["celery", "-A", "handle_data", "worker", "-l", "info", "-Q"]  
