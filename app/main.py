from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes.board import router as BoardRouter
from app.routes.plant import router as PlantRouter
from app.routes.plant import plant_router as PlantRouter



app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(PlantRouter) # add /plant path

app.include_router(BoardRouter)


@app.get("/")
async def root():
    return {"message": "Hello World"}
