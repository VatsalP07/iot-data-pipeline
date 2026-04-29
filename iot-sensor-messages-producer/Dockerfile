FROM python:3.8-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY producer.py .

CMD ["python", "producer.py"]