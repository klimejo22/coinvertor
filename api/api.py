# Imports
from typing import Union
from fastapi import FastAPI
from pydantic import BaseModel
import requests

baseUrl = "https://open.er-api.com/v6/latest/"

app = FastAPI()


@app.get("/convert/{c1}/{c2}/{val}")
def convert_currency(c1: str, c2: str, val: float):
    # c1: Puvodni mena z ktery se prevadi na druhou
    # c2: Druha mena
    # val: Pocet meny

    #slo by zlepsit s db
    response = requests.get(baseUrl + c1).json()
    
    if response["result"] != "success":
        return {"Result": "Currency API failure"}
    else:
        return {
            "Result": "success",
            "c1_val": response["rates"][c1] * val,
            "c2_val": response["rates"][c2] * val
        }