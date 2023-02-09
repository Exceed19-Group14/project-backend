from fastapi import APIRouter, status
from pydantic import BaseModel, Field
from app.routes.board import BoardModel
from app.db.mongo import db, plant_collection
from app.utils.objectid import PydanticObjectId
from enum import IntEnum
from datetime import datetime
from typing import List, Union


PLANT_COLLECTION = "plant"


PLANT_COLLECTION = "plant"


router = APIRouter(
    prefix='/plant'
)


class ModeEnum(IntEnum):
    auto = 1
    manual = 0


class ForceWaterEnum(IntEnum):
    active = 1
    inactive = 0
    
    
class PlantModel(BaseModel):
    id: PydanticObjectId = Field(default_factory=PydanticObjectId, alias='_id')
    board: Union[BoardModel, None]
    name: str
    mode: ModeEnum
    moisture: int
    temperature: int
    light: int
    targeted_temperature: int
    targeted_moisture: int
    targeted_light: int
    force_water: ForceWaterEnum


class CreatePlant(BaseModel):
    name: str
    date: datetime
    mode: ModeEnum
    targeted_temperature: Union[int, None]
    targeted_moisture: Union[int, None]
    targeted_light: Union[int, None]

    
@router.get('/')
def show_plants():
    return {"msg": "there are 3 plants"}


@router.post('/')
def create_plant(dbo: CreatePlant):
    """add new plant into the database"""
    plant_collection.insert_one(
        dbo.dict()
    )

