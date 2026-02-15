FROM python:3.11-slim-bullseye

# set work directory
WORKDIR /app

# dependencies for psycopg2 - VERSIONES ACTUALIZADAS
RUN apt-get update && apt-get install -y --no-install-recommends \
    dnsutils \
    libpq-dev \
    python3-dev \
    gcc \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install dependencies
RUN python -m pip install --no-cache-dir --upgrade pip
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# copy project
COPY . /app/

# install pygoat
EXPOSE 8000

RUN python3 /app/manage.py migrate
WORKDIR /app
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "6", "pygoat.wsgi"]
