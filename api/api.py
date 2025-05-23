# Imports
from typing import Union
from fastapi import FastAPI
from fastapi import HTTPException
from pydantic import BaseModel
import requests
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError


DATABASE_URL = "postgresql://postgres:postgres@postgres:5432/currencydata"
baseUrl = "https://open.er-api.com/v6/latest/"

engine = create_engine(DATABASE_URL)
app = FastAPI()

def opendata_fail(response):
    return response["result"] != "success"

def raise_db_error(e, line):
    return {
        "Result" : "Error: " + str(e),
        "Line" : line
    }

@app.get("/convert/{c1}/{c2}/{val}")
def convert_currency(c1: str, c2: str, val: float):
    # c1: Puvodni mena z ktery se prevadi na druhou
    # c2: Druha mena
    # val: Pocet meny

    with engine.connect() as connection:
        try:
            base_id = connection.execute(
                text("SELECT id FROM currencies WHERE name = :name"),
                {"name": c1}
            ).scalar()
            id_check_result = connection.execute(
                text("SELECT id FROM exchange_rates WHERE base_currency_id = :id"),
                {"id": base_id}
            )
        except SQLAlchemyError as e:
            return raise_db_error(e, 40)
        if id_check_result.first() is None:
            add_result = add_data(c1)
            if add_result["Result"] != "Success":
                return raise_db_error(add_result["Result"] + "na radku" + str(add_result["Line"]), 46)
        
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
            return raise_db_error(e, 58)

    return {
        "Result": "success",
        "c1_val": val,
        "c2_val": result * val
    }
    
@app.get("/addData/{input_currency}")
def add_data(input_currency: str):

    with engine.connect() as connection:

        response = requests.get(baseUrl + input_currency).json()
        if opendata_fail(response):
            return {"Result": "Currency API failure"}
        else:

            try:
                base_id = connection.execute(
                    text("SELECT id FROM currencies WHERE name = :name"),
                    {"name": input_currency}
                ).scalar()
            except SQLAlchemyError as e:
                return raise_db_error(e, 96)

            for key, value in response["rates"].items():
                try:
                    target_id = connection.execute(
                        text("SELECT id FROM currencies WHERE name = :name"),
                        {"name": key}
                    ).scalar()
                    connection.execute(
                        text("INSERT INTO exchange_rates (base_currency_id, target_currency_id, rate) VALUES (:base_id, :target_id, :rate)"),
                        {
                            "base_id": base_id,
                            "target_id": target_id,
                            "rate": value
                        }
                    )
                except SQLAlchemyError as e:
                    return raise_db_error(e, 107)
            connection.commit()

    return {"Result": "Success"}