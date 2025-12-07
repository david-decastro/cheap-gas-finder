FROM python:3.12-slim

# Environment variables to avoid buffering and disable pip cache
ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# Copy only requirements and config first
COPY ../requirements.txt ../_config.ini /app/

# Install dependencies
RUN pip install --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY ../ /app/

# Default command to run the bot
CMD ["python", "server.py"]
