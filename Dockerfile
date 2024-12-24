FROM python:3.12-slim

# Set environment variable to not buffer Python output (for logs)
ENV PYTHONUNBUFFERED 1

# Set the working directory
WORKDIR /app
HEALTHCHECK --interval=5s --timeout=3s --retries=3 CMD curl --fail http://localhost:8080/ || exit 1
# Create a non-root user
RUN useradd -ms /bin/bash myuser

# Copy the application files into the container
COPY sample.py /app
COPY requirements.txt /app

# Install system dependencies and Python dependencies in one step
RUN apt-get update \
    && apt-get install -y --no-install-recommends gcc libpq-dev \
    && apt install curl -y \
    && python -m venv /app/venv \
    && /app/venv/bin/pip install --no-cache-dir -r requirements.txt \
    && apt-get purge -y --auto-remove gcc libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Change ownership of files and switch to the non-root user
RUN chown -R myuser /app
USER myuser

# Expose port (if applicable)
EXPOSE 8080

LABEL maintainer="Maxwell"
# Set the entrypoint to run the application using the virtual environment's Python
ENTRYPOINT ["/app/venv/bin/python3", "sample.py"]
