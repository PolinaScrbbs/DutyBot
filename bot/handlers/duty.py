from aiogram import F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from .application import router

from .. import response
from .. import keyboards as kb
from .. import utils as ut


async def create_duties_msg(prefix: str, duties):
    msg = prefix
    for duty in duties:
        msg += (
            f"*@{duty['attendant']['username']}* ({duty['attendant']['full_name']})\n"
            f"Дежурил(а) *{duty['attendant']['duties_count']} раз(а)*\n"
            f"Последнее дежурство: *{duty['attendant']['last_duty']}*\n\n"
        )
    return msg


@router.message(lambda message: message.text == "Дежурства")
async def group_menu(message: Message, state: FSMContext):
    user_data = await state.get_data()
    token = await ut.get_user_token(message, user_data)

    if token:
        msg = "📋 Выберите нужный пункт из меню дежурств:"
        keyboard = kb.duty_menu

        await message.answer(msg, reply_markup=keyboard)


@router.message(lambda message: message.text == "Назначить дежурных")
async def get_attendant(message: Message, state: FSMContext):
    user_data = await state.get_data()
    token = await ut.get_user_token(message, user_data)

    if token:
        missed_students_id = user_data.get("missed_students_id", None)

        if not missed_students_id:
            missed_students_id = []
            user_data["missed_students_id"] = missed_students_id

        status, attendants = await response.get_attendants(token, missed_students_id)

        user_data["attendants_id"] = [attendants[0]["id"], attendants[1]["id"]]
        await state.update_data(user_data)

        if status == 200:
            try:
                try:
                    await message.edit_text(
                        f"👷🏿 Назначены дежурные:\n*{attendants[0]['full_name']}* и *{attendants[1]['full_name']}*",
                        reply_markup=kb.remap,
                        parse_mode="Markdown",
                    )
                except Exception:
                    await message.answer(
                        f"👷🏿 Назначены дежурные:\n*{attendants[0]['full_name']}* и *{attendants[1]['full_name']}*",
                        reply_markup=kb.remap,
                        parse_mode="Markdown",
                    )
            except Exception:
                await message.edit_text(
                    "❗ Ошибка при назначении дежурных. Попробуйте ещё раз.",
                    reply_markup=kb.remap,
                    parse_mode="Markdown",
                )


@router.message(lambda message: message.text == "Дежурные")
async def get_current_attendant(message: Message, state: FSMContext):
    user_data = await state.get_data()
    token = await ut.get_user_token(message, user_data)

    if token:
        status, attendants = await response.get_current_attendants(token)
        if status == 200:
            await message.answer(
                f"🛡️ *Текущие дежурные*:\n👷🏿 {attendants[0]['full_name']}\n👷🏿 {attendants[1]['full_name']}",
                parse_mode="Markdown",
            )


@router.callback_query(lambda query: query.data.startswith("remap_"))
async def remap(callback: CallbackQuery, state: FSMContext):
    remap_num = int(callback.data.split("_", 1)[1])

    user_data = await state.get_data()
    missed_students_id = user_data["missed_students_id"]
    attendants_id = user_data["attendants_id"][remap_num]
    missed_students_id.append(attendants_id)
    user_data["missed_students_id"] = missed_students_id

    await state.update_data(user_data)
    await get_attendant(callback.message, state)


@router.callback_query(F.data == "assign")
async def assign(callback: CallbackQuery, state: FSMContext):
    user_data = await state.get_data()
    token = await ut.get_user_token(callback.message, user_data)

    if token:
        attendants_id = user_data["attendants_id"]

        status = await response.post_duty(token, attendants_id)

        if status == 201:
            await callback.message.edit_text("✅ Дежурные успешно установлены.")
            await ut.clear_user_data(
                state, token, user_data["user"], user_data["group"]
            )
        else:
            await callback.message.edit_text(
                "❌ Произошла ошибка при установке дежурных."
            )


@router.message(lambda message: message.text == "Список дежурств")
async def duty_list(message: Message, state: FSMContext):
    user_data = await state.get_data()
    token = await ut.get_user_token(message, user_data)

    if token:
        offset = 0
        limit = 5

        status, duties = await response.get_duties(token, limit=limit, offset=offset)

        if status == 204:
            await message.answer("📭 Список дежурств пока пуст.", parse_mode="Markdown")
        else:
            msg = await ut.create_duties_msg("🧹 *Список дежурств:*\n\n", duties)
            await message.answer(
                msg,
                parse_mode="Markdown",
                reply_markup=kb.get_pagination_kb("duties_pagination", offset),
            )


@router.message(lambda message: message.text == "Количество дежурств")
async def duty_count(message: Message, state: FSMContext):
    user_data = await state.get_data()
    token = await ut.get_user_token(message, user_data)

    if token:
        limit = 3
        offset = 0

        status, duties_count = await response.get_duties(
            token, limit=limit, offset=offset
        )

        if status == 204:
            await message.answer("📭 Список дежурств пуст.", parse_mode="Markdown")
        else:
            msg = await create_duties_msg("📊 *Количество дежурств:*\n\n", duties_count)
            await message.answer(
                msg,
                parse_mode="Markdown",
                reply_markup=kb.get_pagination_kb("duties_count_pagination", offset),
            )


@router.callback_query(F.data.startswith("duties_pagination:"))
async def duties_pagination(callback: CallbackQuery, state: FSMContext):
    user_data = await state.get_data()
    token = await ut.get_user_token(callback, user_data)

    if token:
        if callback.data == "duties_pagination:close":
            await callback.message.delete()
            await callback.answer()

            await callback.message.bot.send_message(
                callback.message.chat.id, "✅ Меню закрыто.", reply_markup=kb.duty_menu
            )
            return

        _, action, offset_str = callback.data.split(":")
        offset = int(offset_str)
        limit = 5

        if action == "next":
            offset += limit
        elif action == "prev":
            if offset == 0:
                await callback.answer(
                    "⚠️ Вы на первой странице, назад уже некуда.", show_alert=True
                )
                return
            offset = max(0, offset - limit)

        status, duties = await response.get_duties(token, limit=limit, offset=offset)

        if status == 204 or not duties:
            await callback.answer("ℹ️ Дежурств больше нет.", show_alert=True)
            return

        msg = await ut.create_duties_msg("🧹 *Дежурства:*\n\n", duties)

        await callback.message.edit_text(
            msg,
            parse_mode="Markdown",
            reply_markup=kb.get_pagination_kb("duties_pagination", offset),
        )

        await callback.answer()


@router.callback_query(F.data.startswith("duties_count_pagination:"))
async def handle_duties_pagination(callback: CallbackQuery, state: FSMContext):
    user_data = await state.get_data()
    token = await ut.get_user_token(callback, user_data)

    if token:
        if callback.data == "duties_count_pagination:close":
            await callback.message.delete()
            await callback.answer()

            await callback.message.bot.send_message(
                callback.message.chat.id, "✅ Меню закрыто.", reply_markup=kb.duty_menu
            )
            return

        _, action, offset_str = callback.data.split(":")
        offset = int(offset_str)
        limit = 3

        if action == "next":
            offset += limit
        elif action == "prev":
            if offset == 0:
                await callback.answer(
                    "⚠️ Вы на первой странице, назад уже некуда.", show_alert=True
                )
                return
            offset = max(0, offset - limit)

        status, duties_count = await response.get_duties(
            token, limit=limit, offset=offset
        )

        if status == 204 or not duties_count:
            await callback.answer("ℹ️ Дежурств больше нет.", show_alert=True)
            return

        msg = await create_duties_msg("📊 *Количество дежурств:*\n\n", duties_count)

        await callback.message.edit_text(
            msg,
            parse_mode="Markdown",
            reply_markup=kb.get_pagination_kb("duties_count_pagination", offset),
        )

        await callback.answer()
