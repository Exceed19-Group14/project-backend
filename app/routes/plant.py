from fastapi import APIRouter, status, HTTPException
from pydantic import BaseModel, Field
from app.routes.board import BoardModel
from app.db.mongo import db, plant_collection, board_collection
from app.utils.objectid import PydanticObjectId
from bson.objectid import ObjectId
from enum import IntEnum
from datetime import datetime
from typing import List, Union


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
    

class UpdateMoisture(BaseModel):
    moisture: int


class UpdateTemperature(BaseModel):
    temperature: float
    

class UpdateLight(BaseModel):
    light: int


class UpdateModeAuto(BaseModel):
    mode: ModeEnum
    targeted_temperature: float
    targeted_moisture: int
    targeted_light: int
  

class UpdateModeManual(BaseModel):
    mode: ModeEnum
    

class PlantModel(BaseModel):
    plant_id: int
    id: PydanticObjectId = Field(default_factory=PydanticObjectId, alias='_id')
    board: Union[None, int]
    name: str
    mode: ModeEnum
    moisture: Union[int, None] = None
    temperature: Union[float, None] = None
    light: Union[int, None] = None
    targeted_temperature: Union[int, None] = None
    targeted_moisture: Union[int, None] = None
    targeted_light: Union[int, None] = None
    force_water: ForceWaterEnum = ForceWaterEnum.inactive
    watering_time: int # in secs
    
    def find_board(self):
        self.board = board_collection.find_one({
            "board": self.board
        })

class CreatePlant(BaseModel):
    board: int
    plant_id: int
    name: str
    date: datetime
    mode: ModeEnum
    targeted_temperature: Union[float, None] = None
    targeted_moisture: Union[int, None] = None
    targeted_light: Union[int, None] = None

    
@router.get('/', response_model=List[PlantModel])
def show_plants():
    return list(plant_collection.find({}))


@router.post('/', status_code=status.HTTP_201_CREATED)
def create_plant(dbo: CreatePlant):
    """add new plant into the database"""
    plant_collection.insert_one(dbo.dict())
    

@router.get('/{id}', status_code=status.HTTP_200_OK, response_model=PlantModel)
def get_plant(id: int):
    """get a specify plant info by board id"""
    plant = plant_collection.find_one({"plant_id": id})
    if plant is not None:
        return plant
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND, 
        detail=f"Plant with ID {id} not found"
    )
    

@router.put('/{id}/moisture')
def update_moisture(id: int, dbo: UpdateMoisture):
    plant_collection.update_one(
            {"plant_id": id}, {"$set": {"moisture": dbo.dict().get('moisture')}}
        )
    

@router.put('/{id}/temperature')
def update_temperature(id: int, dbo: UpdateTemperature):
    plant_collection.update_one(
            {"plant_id": id}, {"$set": {"temperature": dbo.dict().get('temperature')}}
        )


@router.put('/{id}/light')
def update_light(id: int, dbo: UpdateLight):
        plant_collection.update_one(
            {"plant_id": id}, {"$set": {"light": dbo.dict().get('light')}}
        )


@router.put('/{id}/mode/auto')
def update_mode(id: int, dbo: UpdateModeAuto):
    plant_collection.update_one(
            {"plant_id": id}, {"$set": dbo.dict()}
        )


@router.put('/{id}/mode/manual')
def update_mode(id: int, dbo: UpdateModeManual):
    plant_collection.update_one(
            {"plant_id": id}, {"$set": {"mode": dbo.dict().get("mode")}})


@router.put('/{id}/unregister')
def unregister_plant(id: int):
    plant_collection.update_one(
        {"plant_id": id}, {"$set": {"board": None}})


@plant_router.get('/{id}/water')
def get_water_command(id: int) -> int:
    doc = plant_collection.find_one({
        "board": id
    })

    if doc is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, {
            "error": {
                "details": "Not found"
            }
        })

    if doc['mode'] == ModeEnum.auto:
        # TODOS Condition to watering some plant
        pass
    else:
        if doc['force_water'] == ForceWaterEnum.active:
            return 1
        else:
            return 0
    return 0