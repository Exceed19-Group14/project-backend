from fastapi import APIRouter, status, HTTPException
from pydantic import BaseModel
from app.routes.board import BoardModel
from app.db.mongo import db, plant_collection, board_collection
from enum import IntEnum
from typing import List, Union


PLANT_COLLECTION = "plant"


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
    board: Union[BoardModel, int, None] = None
    name: str
    mode: ModeEnum
    moisture: int
    temperature: int
    light: int
    targeted_temperature: int
    targeted_moisture: int
    targeted_light: int
    force_water: ForceWaterEnum
    watering_time: int  # in secs

    def find_board(self):
        self.board = board_collection.find_one({
            "board": self.board
        })


@plant_router.get('/')
def show_plants():
    return {"msg": "there are 3 plants"}


@plant_router.post('/plant', status_code=status.HTTP_201_CREATED)
def create_plant(dbo: PlantModel):
    """add new plant into the database"""
    plant_collection.insert_one({
        dbo.dict()
    })


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
