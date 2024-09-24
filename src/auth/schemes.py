from typing import Any
from pydantic import BaseModel


class LoginForm(BaseModel):
    login: str
    password: str


class TokenResponse(BaseModel):
    message: str
    token: str
