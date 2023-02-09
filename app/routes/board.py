from fastapi import APIRouter, status
from pydantic import BaseModel, Field
from utils.objectid import PydanticObjectId
from app.db.mongo import board_collection
import pymongo

router = APIRouter(
    prefix='/board'
)


class BoardModel(BaseModel):
    id: PydanticObjectId = Field(default_factory=PydanticObjectId, alias='_id')
    board_id: int


class CreateBoardDto(BaseModel):
    board_id: int


@router.get()
def get_boards():
    docs = list(board_collection.find({}))
    return docs


@router.post(status_code=status.HTTP_201_CREATED)
def create_board(dto: BoardModel):
    board_collection.insert_one(dto.dict())
