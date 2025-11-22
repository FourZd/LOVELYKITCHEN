from pydantic import BaseModel, Field

from activities.entities import ActivityEntity


class CreateActivityRequest(BaseModel):
    type: str = Field(default="comment")
    payload: dict


class ActivityResponse(BaseModel):
    data: ActivityEntity


class ActivitiesListResponse(BaseModel):
    data: list[ActivityEntity]

