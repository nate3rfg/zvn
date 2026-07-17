FROM python:3.12-slim

WORKDIR /app

COPY bots/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY bots/ ./bots/

CMD ["python3", "bots/main.py"]
