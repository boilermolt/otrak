FROM python:3.12-slim

WORKDIR /app

# System deps
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# App deps
COPY app/requirements.txt /app/requirements.txt
# Install CPU-only torch explicitly
RUN pip install --no-cache-dir --index-url https://download.pytorch.org/whl/cpu torch==2.10.0+cpu
RUN pip install --no-cache-dir -r /app/requirements.txt

# App code
COPY app /app

EXPOSE 5000
CMD ["python", "app.py"]
