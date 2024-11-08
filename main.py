from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
import databases
import sqlalchemy

DATABASE_URL = "sqlite:///./test.db"

database = databases.Database(DATABASE_URL)
metadata = sqlalchemy.MetaData()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow requests from Angular app
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)
@app.middleware("http") 
async def add_process_time_header(request: Request, call_next): 
    response = await call_next(request) 
    response.headers["X-Process-Time"] = str(request.url) 
    return response

class Room(BaseModel):
    id: int
    name: str
    door_closes: bool
    ac_works: bool
    coffee_maker_works: bool
    lights_work: bool
    status: str

rooms_table = sqlalchemy.Table(
    "rooms",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("name", sqlalchemy.String),
    sqlalchemy.Column("door_closes", sqlalchemy.Boolean),
    sqlalchemy.Column("ac_works", sqlalchemy.Boolean),
    sqlalchemy.Column("coffee_maker_works", sqlalchemy.Boolean),
    sqlalchemy.Column("lights_work", sqlalchemy.Boolean),
    sqlalchemy.Column("status", sqlalchemy.String),
)

engine = sqlalchemy.create_engine(DATABASE_URL)
metadata.create_all(engine)

@app.on_event("startup")
async def startup():
    await database.connect()

@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()

# Create Room
@app.post("/rooms/")
async def create_room(room: Room):
    query = rooms_table.insert().values(
        id=room.id,
        name=room.name,
        door_closes=room.door_closes,
        ac_works=room.ac_works,
        coffee_maker_works=room.coffee_maker_works,
        lights_work=room.lights_work,
        status=room.status
    )
    await database.execute(query)
    return room

# Update Room
@app.put("/rooms/{room_id}")
async def update_room(room_id: int, updated_room: Room):
    query = rooms_table.update().where(rooms_table.c.id == room_id).values(
        name=updated_room.name,
        door_closes=updated_room.door_closes,
        ac_works=updated_room.ac_works,
        coffee_maker_works=updated_room.coffee_maker_works,
        lights_work=updated_room.lights_work,
        status=updated_room.status
    )
    result = await database.execute(query)
    if result:
        return updated_room
    raise HTTPException(status_code=404, detail="Room not found")

# Get Room
@app.get("/rooms/{room_id}")
async def get_room(room_id: int):
    query = rooms_table.select().where(rooms_table.c.id == room_id)
    room = await database.fetch_one(query)
    if room:
        return room
    raise HTTPException(status_code=404, detail="Room not found")

# Get All Rooms
@app.get("/rooms/")
async def get_all_rooms():
    query = rooms_table.select()
    rooms = await database.fetch_all(query)
    return rooms
