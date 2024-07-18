# Use the official Python image from the Docker Hub
FROM python

# Set environment variables
ENV POSTGRE_USER=
ENV POSTGRE_PASSWORD=
ENV POSTGRE_HOST=
ENV POSTGRE_PORT=
ENV GITHUB_TOKEN=
ENV LANGSMITH_TOKEN=
ENV AWS_STORAGE_BUCKET_NAME=
ENV PYTHONUNBUFFERED=1

# Set the working directory
WORKDIR /app

# Copy the requirements file
COPY requirements.txt .

# Install the dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Create the .aws folder in the home directory
RUN mkdir -p /root/.aws

# Expose the port your application runs on
EXPOSE 8000

# Run the Django application
CMD ["python", "backend/manage.py", "runserver", "0.0.0.0:8000"]
