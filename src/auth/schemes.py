from pydantic import BaseModel

from ..user.schemes import BaseUser


class LoginForm(BaseModel):
    login: str
    password: str


class BaseToken(BaseModel):
    token: str
    user: BaseUser


class TokenResponse(BaseModel):
    message: str
    token: str
