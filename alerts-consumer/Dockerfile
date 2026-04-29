FROM python:3.8-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

# 🔥 COPY EVERYTHING (INCLUDING model.pkl)
COPY . .

CMD ["python", "consumer.py"]