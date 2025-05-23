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

def raise_db_error(e):
    return {"Result" : "Error" + str(e)}

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
            id_check_result = connection.execute("SELECT id FROM exchange_rates WHERE base_currency_id = :id", {"id" : base_id})
        except SQLAlchemyError as e:
            return raise_db_error(e)
        if id_check_result.first() is None:
            if not add_data(c1):
                return
        else:
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
                return raise_db_error(e)

            return {
                "Result": "success",
                "c1_val": val,
                "c2_val": result * val
            }
    
@app.get("/addData/{input_currency}")
def add_data(input_currency: str):
    
    query = text("""
    SELECT 
        c1.name AS base_currency, 
        c2.name AS target_currency, 
        er.rate
    FROM exchange_rates er
    JOIN currencies c1 ON er.base_currency_id = c1.id
    JOIN currencies c2 ON er.target_currency_id = c2.id
    WHERE c1.name = :input_currency;
    """)

    with engine.connect() as connection:

        try: 
            result = connection.execute(query, {"input_currency": input_currency})
        except SQLAlchemyError as e:
            return raise_db_error(e)
        
        if result.first() is None:
            response = requests.get(baseUrl + input_currency).json()
            if opendata_fail(response):
                return {"Result": "Currency API failure"}
            else:

                try:
                    base_id = connection.execute("SELECT id FROM currencies WHERE name = :name", {"name" : input_currency}).scalar()
                except SQLAlchemyError as e:
                    return raise_db_error(e)

                for key, value in response["rates"].items():
                    try:
                        target_id = connection.execute("SELECT id FROM currencies WHERE name = :name", {"name" : key}).scalar()
                        connection.execute("INSERT INTO exchange_rates (base_currency_id, target_currency_id, rate) VALUES (:base_id, :target_id, :rate)", {
                        "base_id": base_id,
                        "target_id": target_id,
                        "rate": value
                        })
                    except SQLAlchemyError as e:
                        return raise_db_error(e)
                connection.commit()
        #         add_data(input_currency)
        # else:

        #     data = []
        #     for row in result:
        #         data.append({
        #             "base_currency": row.base_currency,
        #             "target_currency": row.target_currency,
        #             "rate": row.rate
        #         })
    return True