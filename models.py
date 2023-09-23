
from typing import Optional, Any, Callable, Annotated
from bson import ObjectId

from pydantic import BaseModel, ConfigDict, Field, GetJsonSchemaHandler
from pydantic.json_schema import JsonSchemaValue
from pydantic_core import core_schema


class _ObjectIdPydanticAnnotation:
    # Based on https://docs.pydantic.dev/latest/usage/types/custom/#handling-third-party-types.

    @classmethod
    def __get_pydantic_core_schema__(
        cls,
        _source_type: Any,
        _handler: Callable[[Any], core_schema.CoreSchema],
    ) -> core_schema.CoreSchema:
        def validate_from_str(input_value: str) -> ObjectId:
            return ObjectId(input_value)

        return core_schema.union_schema(
            [
                # check if it's an instance first before doing any further work
                core_schema.is_instance_schema(ObjectId),
                core_schema.no_info_plain_validator_function(validate_from_str),
            ],
            serialization=core_schema.to_string_ser_schema(),
        )

PydanticObjectId = Annotated[
    ObjectId, _ObjectIdPydanticAnnotation
]



class PlayerModel(BaseModel):
  
    PLAYER_NAME: str = Field(...)
    TEAM_ABBREVIATION: str = Field(...)
    PLAYER_ID: int = Field(...)
    GP: int = Field(...)
    AGE: int = Field(...)
    MIN: float = Field(...)
    REB: float = Field(...)
    AST: float = Field(...)
    PTS: float = Field(...)
    TOV: float = Field(...)
    BLK: float = Field(...)
    STL: float = Field(...)
    PF: float = Field(...)
    FG3A: float = Field(...)
    FTA: float = Field(...)
    sim1: str = Field(...)
    sim2: str = Field(...)
    sim3: str = Field(...)
    sim4: str = Field(...)


class UserModel(BaseModel):

    id: PydanticObjectId = Field(alias='_id')
    name: str = Field(...)
    user_id: str = Field(...)
    score: int = 0
    played: int = 0

    class Config:

        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}


class CreateUserModel(BaseModel):

    name: str = Field(...)
    user_id: str = Field(...)
    score: Optional[int] = 0
    played: Optional[int] = 0

    class Config:

        allow_population_by_field_name = True
        arbitrary_types_allowed = True



class UpdateUserModel(BaseModel):

    
    score: Optional[int]
    played: Optional[float]

    class Config:
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
