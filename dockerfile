# Use an official Python runtime as a parent image
FROM python:3.10-slim

# Set the working directory in the container
WORKDIR /usr/src/app

# Install necessary packages
RUN apt-get update && apt-get install -y \
    firefox-esr \
    wget \
    libglib2.0-0 \
    libnss3 \
    libgconf-2-4 \
    libfontconfig1 \
    && rm -rf /var/lib/apt/lists/*

# Download and install Geckodriver for Linux ARM64
RUN wget https://github.com/mozilla/geckodriver/releases/download/v0.35.0/geckodriver-v0.35.0-linux-aarch64.tar.gz
RUN tar -xzf geckodriver-v0.35.0-linux-aarch64.tar.gz
RUN mv geckodriver /usr/local/bin/
RUN rm geckodriver-v0.35.0-linux-aarch64.tar.gz

# Ensure Firefox and Geckodriver are in the PATH
ENV PATH="/usr/local/bin:/usr/bin:${PATH}"

# Install Python dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Ensure geckodriver is executable
RUN chmod +x /usr/local/bin/geckodriver

# Run the script
CMD ["python", "./web_checker.py"]
