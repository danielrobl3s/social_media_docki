# Lightweight Python base image (multi-arch)
FROM python:3.11-slim

# Install system dependencies: Chromium, ChromeDriver, Xvfb, wget, unzip
RUN apt-get update && apt-get install -y \
    wget \
    unzip \
    xvfb \
    chromium \
    chromium-driver \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Create output folder
RUN mkdir /output_logs

# Copy Python requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy your scraper scripts
COPY social_media_files ./social_media_files

# Copy parameter JSON files
COPY params.json ./params.json
COPY params_ig.json ./params_ig.json

# Create entrypoint script to run Xvfb and your scraper
RUN echo '#!/bin/bash\n\
Xvfb :99 -ac -screen 0 1920x1080x24 &\n\
export DISPLAY=:99\n\
sleep 2\n\
python3 social_media_files/instagram.py' > /app/entrypoint.sh && chmod +x /app/entrypoint.sh

# Set the entrypoint
CMD ["/app/entrypoint.sh"]
