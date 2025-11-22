# Use ARM64 compatible base image
FROM --platform=linux/arm64 python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    unzip \
    xvfb \
    chromium \
    chromium-driver \
    && rm -rf /var/lib/apt/lists/*

# Set up working directory
WORKDIR ./app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the scraper script
COPY social_media_files ./social_media_files

# Copy parameters json
COPY params.json ./params.json

# Create entrypoint script for xvfb
RUN echo '#!/bin/bash\n\
Xvfb :99 -ac -screen 0 1920x1080x24 &\n\
export DISPLAY=:99\n\
sleep 2\n\
python social_media_files/facebook.py' > /app/entrypoint.sh && chmod +x /app/entrypoint.sh

# Run the entrypoint script
CMD ["/app/entrypoint.sh"]