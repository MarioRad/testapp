FROM python:3.9-slim-buster

# evitar buffer
ENV PYTHONUNBUFFERED=1

WORKDIR /

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Puerto que usa Flask-SocketIO
EXPOSE 5000

#CMD ["gunicorn", "--worker-class", "eventlet", "-w", "1", "-b", "0.0.0.0:5000", "app:app"]
CMD ["flask", "run", "--host=0.0.0.0", "--port=5000"]