FROM python:3.11

WORKDIR /api

COPY . /api

RUN apt-get update && apt-get install -y gcc && \
    python -m venv /opt/venv && \
    . /opt/venv/bin/activate && \
    pip install --upgrade pip && \
    pip install "fastapi[standard]" requests sqlalchemy psycopg2-binary

ENV PATH="/opt/venv/bin:$PATH"

EXPOSE 8000

CMD ["fastapi", "dev", "api.py", "--host", "0.0.0.0"]
