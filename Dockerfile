# Use the official Python image
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Copy requirements and source code
COPY requirements.txt ./
COPY src/ ./src/

# Install dependencies
ARG PIP_TRUSTED_HOST
RUN if [ -n "$PIP_TRUSTED_HOST" ]; then \
        pip install --no-cache-dir --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org -r requirements.txt; \
    else \
        pip install --no-cache-dir -r requirements.txt; \
    fi

# Expose Streamlit port
EXPOSE 8080

# Set environment variables for Streamlit
ENV STREAMLIT_SERVER_PORT=8080
ENV STREAMLIT_SERVER_ADDRESS=0.0.0.0

# Default command to run Streamlit app
CMD ["streamlit", "run", "src/Dashboard.py"]
