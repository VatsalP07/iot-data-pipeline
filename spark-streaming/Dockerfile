FROM apache/spark:3.5.0

USER root

RUN mkdir -p /home/spark/.ivy2/cache && \
    chmod -R 777 /home/spark/.ivy2

WORKDIR /app

COPY spark_job.py .

CMD ["/opt/spark/bin/spark-submit", \
     "--master", "local[*]", \
     "--packages", "org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.0,org.postgresql:postgresql:42.6.0", \
     "spark_job.py"]