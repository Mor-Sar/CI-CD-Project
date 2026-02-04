FROM python:3.10-slim

WORKDIR /app

# קודם מעתיקים אך ורק את requirements.txt
COPY requirements.txt /app
RUN pip install --no-cache-dir -r requirements.txt

# עכשיו מעתיקים את שאר הפרויקט
COPY . /app

CMD ["python", "run.py"]
