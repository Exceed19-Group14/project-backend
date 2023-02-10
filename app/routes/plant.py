from fastapi import APIRouter, status
from pydantic import BaseModel, Field
from app.routes.board import BoardModel
from app.db.mongo import db, plant_collection, board_collection
from app.utils.objectid import PydanticObjectId
from bson.objectid import ObjectId
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
    board: Union[None, int]
    name: str
    mode: ModeEnum
    moisture: Union[int, None] = None
    temperature: Union[int, None] = None
    light: Union[int, None] = None
    targeted_temperature: Union[int, None] = None
    targeted_moisture: Union[int, None] = None
    targeted_light: Union[int, None] = None
    force_water: ForceWaterEnum = ForceWaterEnum.inactive


class CreatePlant(BaseModel):
    board: int
    name: str
    date: datetime
    mode: ModeEnum
    targeted_temperature: Union[int, None] = None
    targeted_moisture: Union[int, None] = None
    targeted_light: Union[int, None] = None

    
@router.get('/', response_model=List[PlantModel])
def show_plants():
    return list(plant_collection.find({}))


@router.post('/', status_code=status.HTTP_201_CREATED)
def create_plant(dbo: CreatePlant):
    """add new plant into the database"""
    plant_collection.insert_one(dbo.dict())