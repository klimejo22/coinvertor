### --- Imports --- ###
# FastAPI
from typing import Union
from fastapi import FastAPI
from fastapi import Request
from fastapi import Query
from fastapi import HTTPException
from pydantic import BaseModel
# Requests pro Opendata
import requests
# SQLalchemy pro db
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError
# Metriky prometheus
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
import time
from starlette.responses import Response
# Inspect
from inspect import currentframe, getframeinfo
# Sentry
import sentry_sdk
from sentry_sdk.integrations.asgi import SentryAsgiMiddleware
# .env
import os
### --- SENTRY --- ###
# Bezi na localhost:9000
dsn = f"http://{os.environ['SENTRY_KEY']}@{os.environ['SENTRY_HOST']}:{os.environ['SENTRY_PORT']}/{os.environ['SENTRY_PROJECT_ID']}"
sentry_sdk.init(
    dsn=dsn,
    # Add data like request headers and IP for users,
    # see https://docs.sentry.io/platforms/python/data-management/data-collected/ for more info
    send_default_pii=True,
    traces_sample_rate=1,
)

### --- Start fast api --- ###
app = FastAPI()
# app = SentryAsgiMiddleware(app)

### --- Postgres --- ###
DATABASE_URL = f"postgresql://{os.environ['POSTGRES_USER']}:{os.environ['POSTGRES_PASSWORD']}@{os.environ['POSTGRES_HOST']}:{os.environ['POSTGRES_PORT']}/{os.environ['POSTGRES_DB']}"

engine = create_engine(DATABASE_URL)

### --- Prometheus metriky --- ###
REQUEST_COUNT = Counter(
    "http_requests_total", "Počet HTTP requestů", ["method", "endpoint"]
)
REQUEST_LATENCY = Histogram(
    "http_request_duration_seconds", "Doba trvání HTTP requestů", ["method", "endpoint"]
)
HTTP_ERRORS = Counter(
    "http_errors_total", 
    "Počet HTTP chyb podle status kódu", 
    ["method", "endpoint", "status_code"]
)

### --- Opendata --- ###

baseUrl = "https://open.er-api.com/v6/latest/"

time_data = requests.get(baseUrl + "EUR").json()

update_time = (
    time_data["time_last_update_utc"],
    time_data["time_last_update_unix"]
)

### --- Zbytek --- ###


def opendata_fail(response):
    return response["result"] != "success"

def raise_db_error(e, line):
    return {
        "Result" : "Error: " + str(e),
        "Line" : line
    }

@app.get("/testSentry")
async def test():
    12 / 0
     
@app.get("/convert")
def convert_currency(
    c1: str = Query(..., description="Puvodni mena"),
    c2: str = Query(..., description="Cilova mena"),
    val: float = Query(..., description="Hodnota k prevodu")
):
    # c1: Puvodni mena z ktery se prevadi na druhou
    # c2: Druha mena
    # val: Pocet meny

    with engine.connect() as connection:
        query = text("""
            SELECT 
                er.rate
            FROM exchange_rates er
            JOIN currencies c1 ON er.base_currency_id = c1.id
            JOIN currencies c2 ON er.target_currency_id = c2.id
            WHERE c1.name = :base_currency_name
            AND c2.name = :target_currency_name;
        """)
        try:
            result = connection.execute(query, {"base_currency_name": c1, "target_currency_name": c2}).scalar()
        except SQLAlchemyError as e:
            return raise_db_error(e, getframeinfo(currentframe()).lineno)

    return {
        "Result": "Success",
        "c1_val": val,
        "c2_val": result * val
    }

@app.get("/update")
def update():
    if time.time() >= update_time[1]:
    
        with engine.connect() as connection:
            query = text("SELECT * FROM currencies")
            response = connection.execute(query).fetchall()
            for row in response:
                opendata = requests.get(baseUrl + row[1]).json()
                query = text("SELECT COUNT(*) FROM exchange_rates WHERE base_currency_id = :id")
                entries = connection.execute(query, {"id": row[0]}).scalar()
                target_query = text("SELECT id FROM currencies WHERE name = :name")
                if entries == 0:
                    insert_query = text("INSERT INTO exchange_rates (base_currency_id, target_currency_id, rate) VALUES (:base_id, :target_id, :rate)")
                    for key, value in opendata["rates"].items():
                        try:
                            target_id = connection.execute(
                                target_query,
                                {"name": key}
                            ).scalar()
                            connection.execute(
                                insert_query,
                                {
                                    "base_id": row[0],
                                    "target_id": target_id,
                                    "rate": value
                                }
                            )
                        except SQLAlchemyError as e:
                            return raise_db_error(e, getframeinfo(currentframe()).lineno)
                else:
                    update_query = text("""
                        UPDATE exchange_rates
                        SET rate = :new_rate
                        WHERE base_currency_id = :base_id
                        AND target_currency_id = :target_id
                    """)

                    for key, value in opendata["rates"].items():
                        try:
                            target_id = connection.execute(
                                target_query,
                                {"name": key}
                            ).scalar()
                            connection.execute(update_query, {
                                "new_rate": value,
                                "base_id": row[0],
                                "target_id": target_id
                            })
                        except SQLAlchemyError as e:
                            return raise_db_error(e, getframeinfo(currentframe()).lineno)
                        
            connection.commit()

    return {"Result": "Success"}

@app.get("/lastUpdate")
def lastUptade():
    return {
        "Last_Update": update_time[0],
        "Timestamp" : update_time[1]
    }

@app.get("/healthCheck")
def healthCheck():
    return {"Status": "API bezi"}

# Prometheus metriky

@app.middleware("http")
async def metrics_middleware(request: Request, call_next):
    method = request.method
    path = request.url.path

    start_time = time.time()
    response = await call_next(request)  # zavolá další vrstvu (tvůj endpoint)
    duration = time.time() - start_time

    REQUEST_COUNT.labels(method=method, endpoint=path).inc()
    REQUEST_LATENCY.labels(method=method, endpoint=path).observe(duration)

    if response.status_code >= 400:
        HTTP_ERRORS.labels(method=method, endpoint=path, status_code=str(response.status_code)).inc()
        
    return response

@app.get("/metrics")
def metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)