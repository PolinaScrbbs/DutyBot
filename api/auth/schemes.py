from fastapi import Form
from typing import Optional
from pydantic import BaseModel


class LoginForm(BaseModel):
    username: str
    password: str
    client_id: Optional[int] = None
    client_secret: Optional[str] = None

    @classmethod
    def as_form(
        cls,
        username: str = Form(...),
        password: str = Form(...),
        client_id: Optional[int] = Form(None),
        client_secret: Optional[str] = Form(None),
    ):
        return cls(
            username=username,
            password=password,
            client_id=client_id,
            client_secret=client_secret,
        )


class TokenResponse(BaseModel):
    message: str
    access_token: str
