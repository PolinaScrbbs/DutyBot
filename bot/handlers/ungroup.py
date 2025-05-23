from aiogram import F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from .auth import router

from .. import response
from .. import keyboards as kb
from .. import states as st
from .. import utils as ut


@router.message(lambda message: message.text == "Создать группу")
async def group_create(message: Message, state: FSMContext):
    user_data = await state.get_data()
    token = await ut.get_user_token(message, user_data)

    if token:
        status, user = await response.get_user_by_username(
            message.from_user.username, token
        )

        user_data["user_id"] = user["id"]
        await state.update_data(user_data)

        if user["role"] != "Староста":
            await message.answer(
                '❗ Чтобы создать группу, нужно стать "Старостой".\nПодайте заявку — её рассмотрят в ближайшее время 😊',
                reply_markup=kb.ungroup_main,
            )
            return

        elif user["group_id"] is not None:
            await message.answer(
                '⚠️ Вы уже создали группу! "Староста" может управлять только одной группой.',
                reply_markup=kb.ungroup_main,
            )
            return

        await message.answer("📝 Введите название вашей новой группы (не номер).")
        await state.set_state(st.GroupCreate.title)


@router.message(st.GroupCreate.title)
async def group_title(message: Message, state: FSMContext):
    title = message.text

    user_data = await state.get_data()
    user_data["title"] = title
    await state.update_data(user_data)

    token = await ut.get_user_token(message, user_data)
    status, specializations = await response.get_specializations(token)

    await message.answer(
        "✨ Отлично! Теперь выберите вашу специальность из списка ниже.",
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
        f"✅ Вы выбрали специальность *{specialization}*.", parse_mode="Markdown"
    )
    await callback.message.answer(
        "📚 Теперь выберите номер курса обучения.",
        reply_markup=await kb.course_number(),
    )


@router.callback_query(lambda query: query.data.startswith("course_number_"))
async def group_course_number(callback: CallbackQuery, state: FSMContext):
    await callback.message.delete_reply_markup()

    user_data = await state.get_data()
    title = user_data["title"]
    specialization = user_data["specialization"]
    course_number = int(callback.data.split("_")[2])
    await callback.message.edit_text(
        f"🎓 Вы выбрали *{course_number}* курс.", parse_mode="Markdown"
    )

    token = await ut.get_user_token(callback, user_data)
    if token:
        status, json_response = await response.post_group(
            title, specialization, course_number, token
        )

        user_data["user"]["group_id"] = json_response["group"]["id"]
        await ut.clear_user_data(state, token, user_data["user"])
        if status == 201:
            await callback.message.answer(
                f"🎉 Группа «{title}» успешно создана!", reply_markup=kb.elder_main
            )
        else:
            await callback.message.answer(
                f"❌ Ошибка: *{json_response['detail'].upper()}*", parse_mode="Markdown"
            )


@router.message(lambda message: message.text == "Вступить в группу")
async def group_join(message: Message, state: FSMContext):
    user_data = await state.get_data()
    status, groups = await response.get_groups(
        without_application=True, token=user_data["token"], limit=10, offset=0
    )
    if status == 204:
        await message.answer(
            "😔 Пока нет доступных групп для вступления.",
            parse_mode="Markdown",
            reply_markup=kb.ungroup_main,
        )
    else:
        await message.answer(
            "🔍 Выберите группу, в которую хотите вступить:",
            parse_mode="Markdown",
            reply_markup=await kb.inline_groups(groups, offset=0),
        )


@router.callback_query(lambda query: query.data.startswith("group_"))
async def group_application(callback: CallbackQuery, state: FSMContext):
    group_fields = callback.data.split("_")
    group_id = int(group_fields[1])
    group_title = group_fields[2]

    user_data = await state.get_data()
    await response.post_application(
        user_data["token"], "На вступление в группу", group_id
    )

    await callback.message.edit_text(
        f"📩 Ваша заявка на вступление в группу *{group_title}* успешно отправлена!",
        parse_mode="Markdown",
    )


@router.message(lambda message: message.text == "Стать старостой")
async def elder_application(message: Message, state: FSMContext):
    user_data = await state.get_data()
    status, json_response = await response.post_application(user_data["token"])

    if status == 201:
        await message.answer(
            '✅ Ваша заявка на роль "Староста" отправлена. Ожидайте решения.'
        )
    else:
        await message.answer(f"❌ Ошибка: {json_response['detail']}")


@router.callback_query(F.data.startswith("groups_pagination:"))
async def groups_pagination(callback: CallbackQuery, state: FSMContext):
    user_data = await state.get_data()
    token = await ut.get_user_token(callback, user_data)
    if token:
        if callback.data == "groups_pagination:close":
            await callback.message.delete()
            await callback.answer()

            await callback.message.bot.send_message(
                callback.message.chat.id,
                "❌ Окно выбора групп закрыто.",
                reply_markup=kb.ungroup_main,
            )
        else:
            _, action, offset_str = callback.data.split(":")
            offset = int(offset_str)
            limit = 10

            if action == "next":
                offset += limit
            elif action == "prev":
                if offset == 0:
                    await callback.answer("Вы на первой странице.", show_alert=True)
                else:
                    offset = max(0, offset - limit)
            status, groups = await response.get_groups(
                without_application=True, token=token, limit=limit, offset=offset
            )

            if status == 204:
                await callback.answer("Групп больше нет", show_alert=True)
            else:
                await callback.message.edit_text(
                    "Выберите группу",
                    parse_mode="Markdown",
                    reply_markup=await kb.inline_groups(groups, offset=offset),
                )

                await callback.answer()
