from fastapi import APIRouter, status
from pydantic import BaseModel
from app.db.mongo import db
from enum import IntEnum
from typing import List


COLLECTION_NAME = "plant"


plant_router = APIRouter(
    prefix='/plant'
)


class ModeEnum(IntEnum):
    auto = 1
    manual = 0


class ForceWaterEnum(IntEnum):
    active = 1
    inactive = 0
    
    
class PlantModel(BaseModel):
    name: str
    mode: ModeEnum
    moisture: int
    temperature: int
    light: int
    targeted_temperature: int
    targeted_moisture: int
    targeted_light: int
    force_water: ForceWaterEnum
    

@plant_router.get('/')
def show_plants():
    return {"msg": "there are 3 plants"}