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
COPY ./fast_api /code/fast_api
COPY ./features /code/features
COPY ./auth /code/auth
COPY ./langgraph_graphs /code/langgraph_graphs
COPY ./utils /code/utils
COPY .env /code/.env
COPY ./streamlit_app.py /code/streamlit_app.py
COPY ./logging_module /code/logging_module


# Expose necessary ports
EXPOSE 8000 8501

# Start both FastAPI and Streamlit applications
CMD ["/bin/bash", "-c", "uvicorn fast_api.fast_api:app --host 0.0.0.0 --port 8000 --reload & streamlit run streamlit_app.py --server.port 8501"]