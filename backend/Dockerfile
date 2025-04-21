# # Use an official Python runtime as a parent image
# FROM python:3.10-slim

# # Set environment variables
# ENV PYTHONDONTWRITEBYTECODE=1
# ENV PYTHONUNBUFFERED=1

# # Set the working directory
# WORKDIR /app

# # Copy requirements and install dependencies
# COPY requirements.txt /app/
# RUN pip install --upgrade pip && pip install -r requirements.txt

# # Copy the rest of the application code
# COPY . /app/

# # Expose the port FastAPI will run on
# EXPOSE 8000

# # Run Alembic migrations on container start (optional, see note below)
# # RUN alembic upgrade head

# Start the FastAPI app using Uvicorn

# CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

FROM python:3.10-slim

# Install required packages
RUN apt-get update && apt-get install -y libaio1 wget unzip

# Install Oracle Instant Client
RUN mkdir -p /opt/oracle && \
    cd /opt/oracle && \
    wget https://download.oracle.com/otn_software/linux/instantclient/2370000/instantclient-basiclite-linux.x64-23.7.0.25.01.zip && \
    unzip instantclient-basiclite-linux.x64-23.7.0.25.01.zip && \
    rm instantclient-basiclite-linux.x64-23.7.0.25.01.zip

# Set environment variables
ENV LD_LIBRARY_PATH=/opt/oracle/instantclient_23_7
ENV PATH=$PATH:/opt/oracle/instantclient_23_7

# Install dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt
RUN pip install alembic

# Copy your app code and run
COPY . /app
WORKDIR /app

# Add entrypoint script
COPY entrypoint.sh /app/
RUN chmod +x /app/entrypoint.sh
CMD ["/app/entrypoint.sh"]
