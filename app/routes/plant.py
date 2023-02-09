from fastapi import APIRouter, status
from pydantic import BaseModel
from app.db.mongo import db
from enum import IntEnum
from typing import List


plant_router = APIRouter(
    prefix='/plant'
)

@plant_router.get('/')
def show_plants():
    return {"msg": "there are 3 plants"}