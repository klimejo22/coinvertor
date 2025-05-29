# Imports
from typing import Union
from fastapi import FastAPI
from fastapi import Request
from fastapi import Query
from fastapi import HTTPException
from pydantic import BaseModel
import requests
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
import time
from starlette.responses import Response
from inspect import currentframe, getframeinfo


DATABASE_URL = "postgresql://postgres:postgres@postgres:5432/currencydata"
baseUrl = "https://open.er-api.com/v6/latest/"

engine = create_engine(DATABASE_URL)

# Prometheus metriky
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

update_time = requests.get(baseUrl + "EUR").json()["time_last_update_utc"]

app = FastAPI()

def opendata_fail(response):
    return response["result"] != "success"

def raise_db_error(e, line):
    return {
        "Result" : "Error: " + str(e),
        "Line" : line
    }

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
        "Result": "success",
        "c1_val": val,
        "c2_val": result * val
    }

@app.get("/update")
def update():
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
                connection.commit()
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
    return {"Last_Update": update_time}

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