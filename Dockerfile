FROM python:3.12.7

# Install dependencies for wkhtmltopdf
RUN apt-get update && apt-get install -y \
    wkhtmltopdf \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /code

# Install Poetry
RUN pip install poetry

# Copy dependencies and install
COPY pyproject.toml poetry.lock ./
RUN poetry config virtualenvs.create false && poetry install --no-interaction --no-ansi

# Copy application code
COPY ./fastapi_backend /code/fastapi_backend
COPY ./streamlit_frontend /code/streamlit_frontend
COPY ./logging_module /code/logging_module

ENV PYTHONPATH="/code:${PYTHONPATH}"

# Expose necessary ports
EXPOSE 8000 8501 8502 8503 8504 8505 8506 8507 8508 8509 8510 8511 8512 8513 8514 8516 8517 8518 8519 8520

CMD ["/bin/bash", "-c", "uvicorn fastapi_backend.fast_api.fast_api:app --host 0.0.0.0 --port 8000 --reload & streamlit run /code/streamlit_frontend/streamlit_app.py --server.port 8501"]