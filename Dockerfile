# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set the working directory inside the container
WORKDIR /app

# Install Poetry
RUN pip install --no-cache-dir poetry

# Copy pyproject.toml and poetry.lock files to the working directory
COPY pyproject.toml poetry.lock* ./

# Install dependencies via Poetry
RUN poetry install --no-root --no-interaction --no-ansi

# Copy the entire application to the working directory
COPY . .

# Expose the port that your application will run on
EXPOSE 8000

# Specify the command to run your application using uvicorn
CMD ["poetry", "run", "uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]