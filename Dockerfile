FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV PORT 8080

# Set work directory
WORKDIR /app

# Install dependencies
COPY requirements.txt /app/
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy project including db.sqlite3
COPY . /app/

# Collect static files
RUN python manage.py collectstatic --noinput

# Run Migrations and Start Gunicorn  
CMD sh -c "python manage.py migrate && exec gunicorn edufuturo.wsgi:application --bind 0.0.0.0:$PORT"
