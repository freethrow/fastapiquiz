from random import shuffle
from typing import Dict, List

import pymongo
from fastapi import APIRouter, Body, HTTPException, Request, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse

from ..models import (
    CreateUserModel,
    PlayerModel,
    UpdateGameScore,
    UpdateUserModel,
    UserModel,
)

router = APIRouter()


def format_question(player):
    """Transform a question object into a JSON representation"""

    choices = []

    choices.append(player["sim1"])
    choices.append(player["sim2"])
    choices.append(player["sim3"])
    choices.append(player["sim4"])
    choices.append(player["PLAYER_NAME"])

    shuffle(choices)

    stats_1 = {
        "Points per game": player["PTS"],
        "Assists per game": player["AST"],
        "Rebounds per game": player["REB"],
    }

    stats_2 = {
        "Minutes per game": player["MIN"],
        "Turnovers per game": player["TOV"],
        "Steals per game": player["STL"],
        "Blocks per game": player["BLK"],
    }

    correct = choices.index(str(player["PLAYER_NAME"]))

    return {
        "choices": choices,
        "stats_1": stats_1,
        "stats_2": stats_2,
        "correct": correct,
        "name": player["PLAYER_NAME"],
    }


"""
Create a new user
"""


@router.post("/", response_description="Add new user", response_model=UserModel)
async def create_user(request: Request, user: CreateUserModel = Body(...)):
    user = jsonable_encoder(user)

    if (
        existing_user := await request.app.mongodb["users"].find_one(
            {"user_id": user["user_id"]}
        )
    ) is not None:
        print("Existing user:", existing_user)
        return existing_user

    new_user = await request.app.mongodb["users"].insert_one(user)
    created_user = await request.app.mongodb["users"].find_one(
        {"id": new_user.inserted_id}
    )
    return JSONResponse(status_code=status.HTTP_201_CREATED, content=created_user)


@router.post("/hook", response_description="Add new webhook", response_model=UserModel)
async def createwebhook(request: Request, data: Dict = Body(...)):
    new_username = data["data"]["username"]
    new_user_id = data["data"]["id"]

    if (
        existing_user := await request.app.mongodb["users"].find_one(
            {"user_id": new_user_id}
        )
    ) is not None:
        print("Existing user found:", existing_user)
        return existing_user

    new_user = CreateUserModel(username=new_username, user_id=new_user_id)
    new_user = jsonable_encoder(new_user)

    new_user = await request.app.mongodb["users"].insert_one(new_user)
    created_user = await request.app.mongodb["users"].find_one(
        {"_id": new_user.inserted_id}
    )

    return created_user


"""Get user score"""


@router.get(
    "/user/{user_id}",
    response_description="Get the player score",
    response_model=UserModel,
)
async def get_player_data(request: Request, user_id: str):
    if (
        existing_user := await request.app.mongodb["users"].find_one(
            {"user_id": user_id}
        )
    ) is not None:
        return existing_user

    raise HTTPException(status_code=404, detail=f"User {user_id} not found")


""" add point from a game """


@router.post(
    "/add-game", response_description="Update a player score", response_model=UserModel
)
async def add_game(request: Request, user: UpdateGameScore = Body(...)):
    user = user.dict()

    # find the player and increment the score and game
    player = await request.app.mongodb["users"].update_one(
        {"user_id": user["user_id"]}, {"$inc": {"played": 1, "score": user["addscore"]}}
    )

    if (
        existing_user := await request.app.mongodb["users"].find_one(
            {"user_id": user["user_id"]}
        )
    ) is not None:
        return existing_user

    return existing_user


@router.put(
    "/{user_id}", response_description="Update a player score", response_model=UserModel
)
async def update_score(
    request: Request, user_id: str, user: UpdateUserModel = Body(...)
):
    user = {k: v for k, v in user.dict().items() if v is not None}

    if len(user) >= 1:
        update_result = await request.app.mongodb["users"].update_one(
            {"user_id": user_id}, {"$set": user}
        )

        if update_result.modified_count == 1:
            if (
                updated_user := await request.app.mongodb["users"].find_one(
                    {"user_id": user_id}
                )
            ) is not None:
                return updated_user

    if (
        existing_user := await request.app.mongodb["users"].find_one(
            {"user_id": user_id}
        )
    ) is not None:
        return existing_user

    raise HTTPException(status_code=404, detail=f"User {user_id} not found")


@router.get("/sample", response_description="Get sample")
async def list_all_players(request: Request, num: int = 10):
    pipeline = [{"$match": {"PTS": {"$gte": 10}}}, {"$sample": {"size": num}}]

    full_query = request.app.mongodb["players"].aggregate(pipeline)

    results = [
        format_question(dict(PlayerModel(**raw_player)))
        async for raw_player in full_query
    ]

    return results
