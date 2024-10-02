import re
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from ..user.utils import user_exists_by_username


class ValidateError(Exception):
    def __init__(
        self, detail: str, status_code: int = status.HTTP_400_BAD_REQUEST
    ) -> None:
        self.detail = detail
        self.status_code = status_code
        super().__init__(detail)


class RegistrationValidator:
    def __init__(
        self,
        username: str,
        password: str,
        confirm_password: str,
        full_name: str,
        session: AsyncSession,
    ) -> None:

        self.username = username
        self.password = password
        self.confirm_password = confirm_password
        self.full_name = full_name
        self.session = session

    async def validate(self):
        try:
            await self.validate_username()
            await self.validate_password()
            await self.validate_full_name()

        except ValidateError as e:
            raise HTTPException(status_code=e.status_code, detail=e.detail)

    async def validate_username(self):
        exists = await user_exists_by_username(self.session, self.username)
        if exists:
            raise ValidateError(
                "A user with this username already exists", status.HTTP_409_CONFLICT
            )
        if not self.username or self.username == "":
            raise ValidateError(
                "Username cannot be empty", status.HTTP_422_UNPROCESSABLE_ENTITY
            )
        if not (4 <= len(self.username) <= 20):
            raise ValidateError(
                "Username must be between 4 and 20 characters long",
                status.HTTP_422_UNPROCESSABLE_ENTITY,
            )
        if not re.match(r"^[A-Za-z0-9 ]+$", self.username):
            raise ValidateError(
                "Username must consist only of English letters, digits, and spaces",
                status.HTTP_422_UNPROCESSABLE_ENTITY,
            )

    async def validate_password(self):
        if not self.password or self.password == "":
            raise ValidateError(
                "Password cannot be empty", status.HTTP_422_UNPROCESSABLE_ENTITY
            )
        if not self.confirm_password or self.confirm_password == "":
            raise ValidateError(
                "Confirm your password", status.HTTP_422_UNPROCESSABLE_ENTITY
            )
        if not (8 <= len(self.password) <= 20):
            raise ValidateError(
                "Password must be between 8 and 20 characters long",
                status.HTTP_422_UNPROCESSABLE_ENTITY,
            )
        if not re.search(r"^[A-Za-z0-9!@#$%&_|?]*$", self.password):
            raise ValidateError(
                "The password must consist only of Latin letters, numbers and the following special characters: [!@#$%&_|?]",
                status.HTTP_400_BAD_REQUEST,
            )
        if not re.search("[a-z]", self.password):
            raise ValidateError(
                "The password must contain at least one lowercase letter.",
                status.HTTP_422_UNPROCESSABLE_ENTITY,
            )
        if not re.search("[A-Z]", self.password):
            raise ValidateError(
                "The password must contain at least one uppercase letter.",
                status.HTTP_422_UNPROCESSABLE_ENTITY,
            )
        if not re.search("[0-9]", self.password):
            raise ValidateError(
                "The password must contain at least one digit.",
                status.HTTP_422_UNPROCESSABLE_ENTITY,
            )
        if not re.search("[!@#$%&_|?]", self.password):
            raise ValidateError(
                "The password must contain at least one special character.",
                status.HTTP_422_UNPROCESSABLE_ENTITY,
            )
        if self.password != self.confirm_password:
            raise ValidateError("Passwords do not match", status.HTTP_400_BAD_REQUEST)

    async def validate_full_name(self):
        if not self.full_name or self.full_name == "":
            raise ValidateError(
                "Fullname cannot be empty", status.HTTP_422_UNPROCESSABLE_ENTITY
            )
        if not (15 <= len(self.full_name) <= 50):
            raise ValidateError(
                "Fullname must be between 15 and 50 characters long",
                status.HTTP_422_UNPROCESSABLE_ENTITY,
            )
        if not re.match(r"^[а-яА-ЯёЁ]+\s[а-яА-ЯёЁ]+\s[а-яА-ЯёЁ]+$", self.full_name):
            raise ValidateError(
                "The full name must consist of three words written in Russian letters only",
                status.HTTP_422_UNPROCESSABLE_ENTITY,
            )
