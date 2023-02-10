from fastapi import APIRouter, status, HTTPException
from pydantic import BaseModel, Field, validator
from app.routes.board import BoardModel
from app.db.mongo import db, plant_collection, board_collection
from app.utils.objectid import PydanticObjectId
from bson.objectid import ObjectId
from enum import IntEnum
from datetime import datetime
from typing import List, Union, Optional

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

    @validator('targeted_light')
    def validateLight(cls, v):
        if v is None:
            return v
        if v < 0 or v > 4095:
            raise ValueError('Light must be between 0 and 4095')
        return v


class UpdateModeManual(BaseModel):
    mode: ModeEnum
    watering_time: int  # in miliseconds


class WaterStatusResponse(BaseModel):
    water_status: ForceWaterEnum
    duration: Union[int, None]  # in miliseconds


class PlantModel(BaseModel):
    plant_id: int
    id: PydanticObjectId = Field(default_factory=PydanticObjectId, alias='_id')
    board: Union[None, int]
    plant_date: datetime
    name: str
    mode: ModeEnum
    moisture: Union[int, None] = None
    temperature: Union[float, None] = None
    light: Union[int, None] = None
    targeted_temperature: Union[int, None] = None
    targeted_moisture: Union[int, None] = None
    targeted_light: Union[int, None] = None
    force_water: ForceWaterEnum = ForceWaterEnum.inactive
    watering_time: Optional[int] = 30000  # in millisec

    def find_board(self):
        return BoardModel(**board_collection.find_one({
            "board": self.board
        }))


class CreatePlant(BaseModel):
    board: Union[int, None] = None
    plant_id: int
    name: str
    plant_date: datetime
    mode: ModeEnum
    # in secs


@router.get('/', response_model=List[PlantModel], tags=["frontend"])
def show_plants():
    return list(plant_collection.find({}))


@router.post('/', status_code=status.HTTP_201_CREATED, tags=["frontend"])
def create_plant(dbo: CreatePlant):
    """add new plant into the database"""
    doc = PlantModel(**dbo.dict()).dict()
    plant_collection.insert_one(doc)


@router.get('/{id}', status_code=status.HTTP_200_OK,
            response_model=PlantModel, tags=["frontend"])
def get_plant(id: int):
    """get a specify plant info by board id"""
    plant = plant_collection.find_one({"plant_id": id})
    if plant is not None:
        return plant
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Plant with ID {id} not found"
    )


@router.put('/{id}/moisture', tags=["hardware"])
def update_moisture(id: int, dbo: UpdateMoisture):
    plant_collection.update_one(
        {"plant_id": id}, {"$set": {"moisture": dbo.dict().get('moisture')}}
    )


@router.put('/{id}/temperature', tags=["hardware"])
def update_temperature(id: int, dbo: UpdateTemperature):
    plant_collection.update_one(
        {"plant_id": id}, {"$set": {"temperature": dbo.dict().get('temperature')}}
    )


@router.put('/{id}/light', tags=["hardware"])
def update_light(id: int, dbo: UpdateLight):
    plant_collection.update_one(
        {"plant_id": id}, {"$set": {"light": dbo.dict().get('light')}}
    )


@router.put('/{id}/mode/auto', tags=["frontend"])
def update_mode(id: int, dbo: UpdateModeAuto):
    plant_collection.update_one(
        {"plant_id": id}, {"$set": dbo.dict()}
    )


@router.put('/{id}/mode/manual', tags=["frontend"])
def update_mode(id: int, dbo: UpdateModeManual):
    plant_collection.update_one(
        {"plant_id": id}, {"$set": {"mode": dbo.dict().get("mode")}})


@router.put('/{id}/unregister', tags=["frontend"])
def unregister_plant(id: int):
    plant_collection.update_one(
        {"plant_id": id}, {"$set": {"board": None}})


@router.get('/{id}/water', tags=["frontend", "hardware"])
def get_water_command(id: int) -> WaterStatusResponse:
    doc = plant_collection.find_one({
        "board": id
    })

    if doc is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, {
            "error": {
                "details": "Not found"
            }
        })
    dto = WaterStatusResponse(
        water_status=ForceWaterEnum.active, duration=doc['watering_time'])
    if doc['mode'] == ModeEnum.auto:
        if doc['targeted_temperature'] > doc['temperature']:
            return dto
        if doc['targeted_moisture'] > doc['moisture']:
            return dto
        if doc['targeted_light'] > doc['light']:
            return dto
    else:
        if doc['force_water'] == ForceWaterEnum.active:
            return dto
    return WaterStatusResponse(water_status=ForceWaterEnum.inactive, duration=None)
