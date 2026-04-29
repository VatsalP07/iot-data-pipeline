FROM python:3.8-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY mqtt-to-kafka.py .

CMD ["python", "mqtt-to-kafka.py"]