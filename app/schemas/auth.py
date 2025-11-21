from pydantic import BaseModel, ConfigDict,Field
from typing import Optional, List, Literal
from datetime import datetime
from pydantic import BaseModel
from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, ConfigDict
from enum import Enum
from pydantic import BaseModel, root_validator, validator
from pydantic import BaseModel, field_validator, model_validator
from typing import Optional

class UserCreate(BaseModel):
    username: str
    role_code: str

    class Config:
        from_attributes = True

class RoleResponse(BaseModel):
    role_code: str
    role_name: str

    class Config:
        from_attributes = True

class RoleListResponse(BaseModel):
    data: List[RoleResponse]

class LoginRequest(BaseModel):
    username: str
    password: str

    class Config:
        from_attributes = True 

class LoginResponse(BaseModel):
    access_token: str
    token_type: str
    username: str
    user_id: int
    role_name: str
    role_code: str


from pydantic import BaseModel
from typing import List, Optional

class RoleResponse(BaseModel):
    id: int
    role_code: str
    role_name: str


class UserResponse(BaseModel):
    id: int
    username: str
    is_active: bool
    role: RoleResponse

class PasswordUpdateRequest(BaseModel):
    new_password: str

class UserUpdateRequest(BaseModel):
    username: Optional[str] = Field(None, min_length=3)
    role_code: Optional[str]
    is_active: Optional[bool]