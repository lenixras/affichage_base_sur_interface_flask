FROM python:3.9-slim

WORKDIR /app

COPY app.py . 

COPY templates/ templates/

RUN apt update && apt install -y vim && pip install flask mysql-connector-python pandas openpyxl flask-wtf

EXPOSE 5000

CMD ["python", "app.py"]
