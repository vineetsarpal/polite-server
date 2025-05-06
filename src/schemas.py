from typing import Annotated
from pydantic import BaseModel, EmailStr, Field, ConfigDict
from datetime import datetime

#Token Schemas
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: str | None = None
    role: str | None = None

# User Schemas
class UserCreate(BaseModel):
    username: str
    email: EmailStr | None = None
    password: str
    full_name: str | None = None
    role: str | None = None


class User(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    username: str
    email: EmailStr | None = None
    full_name: str | None = None
    role: str | None = None # "admin", "agent", "customer"
    is_active: bool | None = True

# class UserInDB(User):
#     password: str

class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: EmailStr
    created_at: datetime



# Policy Schemas
class PolicyBase(BaseModel):
    lob: str
    status: str | None = "active"

    # Premium
    base_premium: float
    net_premium: float
    tax: float  
    sum_insured: float
    
    # Data Capture
    license_plate: str
    vin: str

    start_date: datetime
    end_date: datetime

    policyholder_id: int
    

class PolicyCreate(PolicyBase):
    pass

class PolicyPublic(PolicyBase):
    model_config = ConfigDict(from_attributes=True)

    id: int