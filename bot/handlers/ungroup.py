from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from .auth import router

import response as response
import keyboards as kb
import states as st
import utils as ut


@router.message(lambda message: message.text == "Создать группу")
async def group_create(message: Message, state: FSMContext):
    user_data = await state.get_data()
    token = await ut.get_user_token(user_data)

    if not token:
        await message.answer(
            "Токен не найден, зарегестрируйтесь или пройдите авторизацию",
            reply_markup=kb.ungroup_main,
        )
        return

    status, user = await response.get_user_by_username(
        message.from_user.username, token
    )

    # user_data["user_id"] = user["id"]
    # await state.update_data(user_data)

    if user["role"] != "Староста":
        await message.answer(
            f'Сначала необходимо стать "Старостой", подайте заявку, её рассмотрят в ближайшее время',
            reply_markup=kb.ungroup_main,
        )
        return

    elif user["group_id"] is not None:
        await message.answer(
            f'"Староста" может создать только 1 группу',
            reply_markup=kb.ungroup_main,
        )
        return

    await message.answer(f"Введите название группы (Не номер)")
    await state.set_state(st.GroupCreate.title)


@router.message(st.GroupCreate.title)
async def group_title(message: Message, state: FSMContext):
    title = message.text

    user_data = await state.get_data()
    user_data["title"] = title
    await state.update_data(user_data)

    token = await ut.get_user_token(user_data)
    status, specializations = await response.get_specializations(token)

    await message.answer(
        "Выберите свою специальность",
        reply_markup=await kb.create_specializations_keyboard(specializations),
    )


@router.callback_query(lambda query: query.data.startswith("spec_"))
async def group_specialization(callback: CallbackQuery, state: FSMContext):
    await callback.message.delete_reply_markup()

    specialization = callback.data.split("_")[1]

    user_data = await state.get_data()
    user_data["specialization"] = specialization
    await state.update_data(user_data)

    await callback.message.edit_text(
        f"Вы выбрали *{specialization}*", parse_mode="Markdown"
    )
    await callback.message.answer(
        "Выберите свой курс обучения", reply_markup=kb.course_number
    )


@router.callback_query(lambda query: query.data.startswith("course_number_"))
async def group_course_number(callback: CallbackQuery, state: FSMContext):
    await callback.message.delete_reply_markup()

    user_data = await state.get_data()
    title = user_data["title"]
    specialization = user_data["specialization"]
    course_number = int(callback.data.split("_")[2])
    await callback.message.edit_text(
        f"Вы выбрали *{course_number} курс*", parse_mode="Markdown"
    )

    token = await ut.get_user_token(user_data)

    status, json_response = await response.post_group(
        title, specialization, course_number, token
    )

    await ut.clear_user_data(state, token)
    if status == 201:
        await callback.message.answer(
            f"Группа {title} создана", reply_markup=kb.elder_main
        )
    else:
        await callback.message.answer(
            f"❌ *{json_response['detail'].upper()}*", "Markdown"
        )
