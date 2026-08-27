from pydantic import BaseModel


class CameraCreate(BaseModel):
    name: str
    ip: str


class CameraResponse(BaseModel):
    id: int
    name: str
    ip: str

    model_config = {
        "from_attributes": True
    }