from pydantic import BaseModel, Field

class LoginInput(BaseModel):
    login:str
    password:str = Field("", min_length=0)

class LoginResponse(BaseModel):
    info:str
    token:str

class RegisterNewUserResponse(BaseModel):
    info:str
    link_to_activate:str
    user_id:str

class UsersActivateRequest(BaseModel):
    key:str = Field(..., min_length=36)

class UsersInfoResponse(BaseModel):
    info:str