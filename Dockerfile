# Use the official Python image
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Install Poetry
ARG PIP_TRUSTED_HOST
RUN if [ -n "$PIP_TRUSTED_HOST" ]; then \
        pip install --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org poetry; \
    else \
        pip install poetry; \
    fi

# Copy poetry files
COPY pyproject.toml poetry.lock* ./

# Copy README for poetry package installation
COPY README.md ./

# Configure poetry: do not create virtual environment since we're in a container
RUN poetry config virtualenvs.create false

# Install dependencies
RUN if [ -n "$PIP_TRUSTED_HOST" ]; then \
        poetry config repositories.pypi https://pypi.org/simple/ && \
        poetry config certificates.pypi.cert false && \
        poetry install --only=main --no-root --no-interaction --no-ansi; \
    else \
        poetry install --only=main --no-root --no-interaction --no-ansi; \
    fi

# Copy source code
COPY src/ ./src/

# Expose Streamlit port
EXPOSE 8080

# Set environment variables for Streamlit
ENV STREAMLIT_SERVER_PORT=8080
ENV STREAMLIT_SERVER_ADDRESS=0.0.0.0

# Default command to run Streamlit app
CMD ["streamlit", "run", "src/Dashboard.py"]
