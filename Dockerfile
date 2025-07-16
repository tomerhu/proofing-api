# Dockerfile
# 1. Base image: includes Python 3.10 and pip
FROM python:3.10-slim

# 2. Set a working directory in the container
WORKDIR /app

# 3. Copy requirements.txt first (for Docker layer caching),
#    then install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 4. Copy the rest of your app code into /app
COPY . .

# 5. Expose port 8000 (the port Uvicorn will listen on)
EXPOSE 8000

# 6. Define the default command: run Uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
