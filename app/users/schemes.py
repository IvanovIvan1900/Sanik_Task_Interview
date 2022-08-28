from pydantic import BaseModel, Field

class LoginInput(BaseModel):
    login:str
    password:str = Field("", min_length=0)

class LoginResponse(BaseModel):
    info:str
    token:str