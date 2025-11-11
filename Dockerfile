# Use a lightweight base image
FROM python:3.11-slim

# Set working directory
WORKDIR /main

# Install system dependencies first (cached unless you change this layer)
RUN apt-get update && apt-get install -y --no-install-recommends \
    make build-essential \
 && rm -rf /var/lib/apt/lists/*

# Install Poetry globally (cached unless version changes)
RUN pip install --no-cache-dir poetry

# Copy dependency files first for better caching
COPY pyproject.toml poetry.lock* ./

# Install Python dependencies (cached unless dependencies change)
RUN poetry install --no-root --no-interaction --no-ansi

# Now copy the rest of your app code (this breaks cache only when code changes)
COPY . .

# Build and run app (custom make targets)
RUN make install

EXPOSE 8080
# Only run the app when the container starts
CMD ["poetry", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]
