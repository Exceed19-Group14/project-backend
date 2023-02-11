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


class PatchPlant(BaseModel):
    moisture: int
    temperature: float
    light: int


class UpdateMode(BaseModel):
    mode: ModeEnum


class UpdateForceWater(BaseModel):
    mode: ForceWaterEnum


class WaterStatusResponse(BaseModel):
    water_status: ForceWaterEnum
    duration: Union[int, None]  # in miliseconds


class PlantModel(BaseModel):
    id: Optional[int] = Field(alias='_id')
    board: Union[None, int]
    plant_date: datetime
    name: str
    mode: Optional[ModeEnum] = ModeEnum.auto
    moisture: Union[int, None] = None
    temperature: Union[float, None] = None
    light: Union[int, None] = None
    targeted_temperature: Union[int, None] = 35.2
    targeted_moisture: Union[int, None] = 500
    targeted_light: Union[int, None] = 700
    force_water: ForceWaterEnum = ForceWaterEnum.inactive
    watering_time: Optional[int] = 5000  # in millisec
    plant_image: int

    def find_board(self):
        return BoardModel(**board_collection.find_one({
            "board": self.board
        }))


class CreatePlant(BaseModel):
    board: Union[int, None] = None
    name: str
    plant_date: datetime
    plant_image: Optional[int] = 1
    targeted_temperature: int
    targeted_moisture: int
    targeted_light: int
    watering_time: Optional[int] = 5000  # in millisec


class UpdatePlant(BaseModel):
    targeted_temperature: int
    targeted_moisture: int
    watering_time: int  # in millisec


@router.get('/', response_model=List[PlantModel], tags=["frontend"])
def show_plants():
    return list(plant_collection.find({}))


@router.post('/', status_code=status.HTTP_201_CREATED, tags=["frontend"])
def create_plant(dbo: CreatePlant):
    """add new plant into the database"""
    count = plant_collection.count_documents({})
    doc = PlantModel(**dbo.dict()).dict()
    doc.pop('id')
    doc['_id'] = count+1
    plant_collection.insert_one(doc)


@router.get('/{id}', status_code=status.HTTP_200_OK,
            response_model=PlantModel, tags=["frontend"])
def get_plant(id: int):
    """get a specify plant info by plant id"""
    plant = plant_collection.find_one({"_id": id})
    if plant is not None:
        return plant
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Plant with ID {id} not found"
    )


@router.patch('/{board_id}', tags=['hardware'], status_code=status.HTTP_204_NO_CONTENT)
def patch_hardware(board_id: int, dto: PatchPlant):
    plant_collection.update_one(
        {"board": board_id}, {"$set": dto.dict()}
    )


@router.patch('/{id}/mode', tags=["frontend"], status_code=status.HTTP_204_NO_CONTENT)
def update_mode(id: int, dto: UpdateMode):
    plant_collection.update_one({"_id": id}, {"$set": {"mode": dto.mode}})


@router.put('/{id}', tags=['frontend'], description='Update plant info', status_code=status.HTTP_204_NO_CONTENT)
def update_plant_info(id: int, dto: UpdatePlant):
    data = dto.dict(exclude_none=True)
    plant_collection.update_one({
        {"_id": id}
    }, {
        "$set": dto.dict()
    })


@router.patch('/{id}/water', tags=["frontend"], status_code=status.HTTP_204_NO_CONTENT)
def patch_water(id: int, dto: UpdateMode):
    plant_collection.update_one(
        {"_id": id}, {"$set": {"force_water": dto.mode}})


@router.put('/{id}/unregister', tags=["frontend"], status_code=status.HTTP_204_NO_CONTENT)
def unregister_plant(id: int):
    plant_collection.update_one(
        {"_id": id}, {"$set": {"board": None,
                               "moisture": None,
                               "temperature": None,
                               "light": None}})


@ router.get('/{board_id}/water', tags=["hardware"])
def get_water_command(board_id: int) -> WaterStatusResponse:
    doc = plant_collection.find_one({
        "board": board_id
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
        if not doc['temperature'] is None and doc['targeted_temperature'] < doc['temperature']:
            return dto
        if not doc['moisture'] is None and doc['targeted_moisture'] < doc['moisture']:
            return dto
    else:
        if doc['force_water'] == ForceWaterEnum.active:
            return dto
    return WaterStatusResponse(water_status=ForceWaterEnum.inactive, duration=None)


@ router.patch('/{board_id}/water/stop', tags=["hardware"], description="Stop watering when complete duration", status_code=status.HTTP_204_NO_CONTENT)
def patch_stop_water(board_id: int):
    plant_collection.update_one({
        "board": board_id
    }, {"$set": {
        "force_water": ForceWaterEnum.inactive
    }})


@router.delete('/{id}', tags=['frontend'], status_code=status.HTTP_204_NO_CONTENT)
def delete_plant(id: int):
    plant_collection.delete_one({"_id": id})
