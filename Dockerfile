FROM python:3.13-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt \
    && pip install gunicorn

COPY . .

EXPOSE 5555

CMD ["gunicorn", "-b", "0.0.0.0:5555", "main:app"]