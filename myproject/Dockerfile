# Base image
FROM python:3.10

# Set working directory
WORKDIR /app

# Copy all files (including .pkl model files)
COPY . .

# Install dependencies
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Expose the port Cloud Run expects
EXPOSE 8080

# Start the app with gunicorn
CMD ["gunicorn", "-b", "0.0.0.0:8080", "app:app"]
