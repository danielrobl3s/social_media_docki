FROM python:3.11-slim

# Install Chromium, ChromeDriver, Xvfb, fonts, dependencies
RUN apt-get update && apt-get install -y \
    chromium \
    chromium-driver \
    xvfb \
    fonts-liberation \
    libnss3 \
    libx11-xcb1 \
    libxcomposite1 \
    libxcursor1 \
    libxdamage1 \
    libxrandr2 \
    libasound2 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libdrm2 \
    libgbm1 \
    libgtk-3-0 \
    libpango-1.0-0 \
    libpangocairo-1.0-0 \
    libxss1 \
    wget \
    unzip \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

RUN mkdir /output_logs

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY social_media_files ./social_media_files
COPY params.json ./params.json
COPY params_ig.json ./params_ig.json

# Entrypoint: start Xvfb, then scraper
RUN echo '#!/bin/bash\n\
Xvfb :99 -ac -screen 0 1920x1080x24 &\n\
export DISPLAY=:99\n\
sleep 5\n\
python3 social_media_files/instagram.py' > /app/entrypoint.sh && chmod +x /app/entrypoint.sh

CMD ["/app/entrypoint.sh"]
