FROM python:3.11

WORKDIR /api

COPY ../scripts/wait-for-it.sh /wait-for-it.sh

RUN chmod +x /wait-for-it.sh

RUN apt-get update && apt-get install -y gcc && \
    pip install --upgrade pip

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY . .

# CMD ["fastapi", "dev", "api.py", "--host", "0.0.0.0"]
CMD ["/wait-for-it.sh", "postgres:5432", "--", "fastapi", "dev", "api.py", "--host", "0.0.0.0"]
