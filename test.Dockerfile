FROM python:3.10-slim

WORKDIR /app
COPY test.py /app/test.py

RUN pip install --no-cache-dir requests

CMD ["python", "test.py"]
