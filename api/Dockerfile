FROM python:3.11

WORKDIR /api

RUN apt-get update && apt-get install -y gcc && \
    pip install --upgrade pip

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY . .

CMD ["fastapi", "dev", "api.py", "--host", "0.0.0.0"]
