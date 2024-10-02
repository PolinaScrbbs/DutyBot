import re
from typing import List
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from ..auth.validators import ValidateError

from .utils import group_exists


class GroupValidator:
    def __init__(
        self,
        title: str,
        specialization: str,
        course_number: int,
        specializations: List[str],
        session: AsyncSession,
    ) -> None:

        self.title = title
        self.specialization = specialization
        self.course_number = course_number
        self.specializations = specializations
        self.session = session

    async def validate(self):
        try:
            await self.validate_title()
            await self.validate_specialization()
            await self.validate_course_number()

        except ValidateError as e:
            raise HTTPException(status_code=e.status_code, detail=e.detail)

    async def validate_title(self):
        await group_exists(self.session, self.title)
        if not self.title or self.title == "":
            raise ValidateError(
                "Title cannot be empty", status.HTTP_422_UNPROCESSABLE_ENTITY
            )
        if not (4 <= len(self.title) <= 20):
            raise ValidateError(
                "Group title must be between 4 and 20 characters long",
                status.HTTP_422_UNPROCESSABLE_ENTITY,
            )
        if not re.match(r"^[A-Za-z0-9 ]+$", self.title):
            raise ValidateError(
                "Group title must consist only of English letters, digits, and spaces",
                status.HTTP_422_UNPROCESSABLE_ENTITY,
            )

    async def validate_specialization(self):
        if not self.specialization or self.specialization == "":
            raise ValidateError(
                "Specialization cannot be empty", status.HTTP_422_UNPROCESSABLE_ENTITY
            )
        if self.specialization not in self.specializations:
            raise ValidateError(
                "Specialization is not valid", status.HTTP_400_BAD_REQUEST
            )

    async def validate_course_number(self):
        if not self.course_number or self.course_number == "":
            raise ValidateError(
                "Course number cannot be empty", status.HTTP_422_UNPROCESSABLE_ENTITY
            )
        if self.course_number not in [1, 2, 3, 4]:
            raise ValidateError(
                "The course number can be a number from 1 to 4",
                status.HTTP_422_UNPROCESSABLE_ENTITY,
            )
