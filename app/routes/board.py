from fastapi import APIRouter, status, HTTPException
from pydantic import BaseModel, Field
from app.utils.objectid import PydanticObjectId
from app.db.mongo import board_collection
import pymongo
from typing import List


router = APIRouter(
    prefix='/board'
)


class BoardModel(BaseModel):
    id: PydanticObjectId = Field(default_factory=PydanticObjectId, alias='_id')
    board_id: int


class CreateBoardDto(BaseModel):
    board_id: int


@router.get('/', response_model=List[BoardModel], tags=["frontend"])
def get_boards():
    docs = list(board_collection.find({}))
    return docs


@router.post('/', status_code=status.HTTP_201_CREATED, tags=["frontend"])
def create_board(dto: CreateBoardDto):
    try:
        board_collection.insert_one(dto.dict())
    except pymongo.errors.DuplicateKeyError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Board with ID {dto.board_id} already exists"
        )
