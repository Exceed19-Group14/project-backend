from fastapi import APIRouter, status
from pydantic import BaseModel
from app.db.mongo import db
from enum import IntEnum
from typing import List


router = APIRouter(
    prefix='/plant'
)

