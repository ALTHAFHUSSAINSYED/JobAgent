FROM python:3.12-slim

WORKDIR /app

# Install system utilities & curl for Playwright
RUN apt-get update && apt-get install -y \
    curl \
    git \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install Playwright and CLI dependencies
RUN playwright install-deps chromium
RUN playwright install chromium

COPY . .

# Expose port and launch server
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
