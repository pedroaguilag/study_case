FROM python:3.11-slim

WORKDIR /app
COPY pyproject.toml poetry.lock /app/

RUN pip install --no-cache poetry==1.8.2
RUN poetry config virtualenvs.create false \
  && poetry install --no-dev --no-interaction --no-ansi

COPY main.py config.yml requests.zip /app

# Install unzip
RUN apt-get update && apt-get install -y unzip
RUN unzip -oq "/app/requests.zip" -d "/app"

ENV requests_file_path="/app/requests"


CMD ["python", "main.py"]