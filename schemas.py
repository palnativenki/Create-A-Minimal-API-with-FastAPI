from pydantic import BaseModel, Field, validator

class AddressBase(BaseModel):
    name: str = Field(..., min_length=1)
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)

class AddressCreate(AddressBase):
    pass

class AddressUpdate(AddressBase):
    pass

class AddressOut(AddressBase):
    id: int

    class Config:
        orm_mode = True

