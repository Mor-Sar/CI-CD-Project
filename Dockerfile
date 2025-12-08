FROM python:3.10-slim

# הגדרת התיקייה שבתוך הקונטיינר
WORKDIR /app

# העתקת כל הפרויקט לתוך הקונטיינר
COPY . /app

# התקנת כל הספריות
RUN pip install --no-cache-dir -r requirements.txt

# הרצת האפליקציה
CMD ["python", "app.py"]