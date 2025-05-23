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
                "Пользователь с таким именем уже существует", status.HTTP_409_CONFLICT
            )
        if not self.username or self.username == "":
            raise ValidateError(
                "Имя пользователя не может быть пустым",
                status.HTTP_422_UNPROCESSABLE_ENTITY,
            )
        if not (4 <= len(self.username) <= 20):
            raise ValidateError(
                "Имя пользователя должно быть от 4 до 20 символов",
                status.HTTP_422_UNPROCESSABLE_ENTITY,
            )
        if not re.match(r"^[A-Za-z0-9 ]+$", self.username):
            raise ValidateError(
                "Имя пользователя может содержать только латинские буквы, цифры и пробелы",
                status.HTTP_422_UNPROCESSABLE_ENTITY,
            )

    async def validate_password(self):
        if not self.password or self.password == "":
            raise ValidateError(
                "Пароль не может быть пустым", status.HTTP_422_UNPROCESSABLE_ENTITY
            )
        if not self.confirm_password or self.confirm_password == "":
            raise ValidateError(
                "Подтвердите пароль", status.HTTP_422_UNPROCESSABLE_ENTITY
            )
        if not (8 <= len(self.password) <= 20):
            raise ValidateError(
                "Пароль должен быть от 8 до 20 символов",
                status.HTTP_422_UNPROCESSABLE_ENTITY,
            )
        if not re.search(r"^[A-Za-z0-9!@#$%&_|?]*$", self.password):
            raise ValidateError(
                "Пароль должен содержать только латинские буквы, цифры и специальные символы: [!@#$%&_|?]",
                status.HTTP_400_BAD_REQUEST,
            )
        if not re.search("[a-z]", self.password):
            raise ValidateError(
                "Пароль должен содержать хотя бы одну строчную букву",
                status.HTTP_422_UNPROCESSABLE_ENTITY,
            )
        if not re.search("[A-Z]", self.password):
            raise ValidateError(
                "Пароль должен содержать хотя бы одну заглавную букву",
                status.HTTP_422_UNPROCESSABLE_ENTITY,
            )
        if not re.search("[0-9]", self.password):
            raise ValidateError(
                "Пароль должен содержать хотя бы одну цифру",
                status.HTTP_422_UNPROCESSABLE_ENTITY,
            )
        if not re.search("[!@#$%&_|?]", self.password):
            raise ValidateError(
                "Пароль должен содержать хотя бы один специальный символ",
                status.HTTP_422_UNPROCESSABLE_ENTITY,
            )
        if self.password != self.confirm_password:
            raise ValidateError("Пароли не совпадают", status.HTTP_400_BAD_REQUEST)

    async def validate_full_name(self):
        if not self.full_name or self.full_name == "":
            raise ValidateError(
                "Полное имя не может быть пустым", status.HTTP_422_UNPROCESSABLE_ENTITY
            )
        if not (15 <= len(self.full_name) <= 50):
            raise ValidateError(
                "Полное имя должно быть от 15 до 50 символов",
                status.HTTP_422_UNPROCESSABLE_ENTITY,
            )
        if not re.match(r"^[а-яА-ЯёЁ]+\s[а-яА-ЯёЁ]+\s[а-яА-ЯёЁ]+$", self.full_name):
            raise ValidateError(
                "Полное имя должно состоять из трёх слов, написанных только русскими буквами",
                status.HTTP_422_UNPROCESSABLE_ENTITY,
            )
