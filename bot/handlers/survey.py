from aiogram import Bot, F, Router
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from bot import db
from bot.keyboards import contact_request_keyboard, post2_keyboard, survey_keyboard, welcome_keyboard
from bot.notify import notify_admin
from bot.states import SurveyStates
from bot.texts import (
    CONTACT_REQUEST_TEXT,
    POST2_TEXT,
    SURVEY_CUSTOM_PROMPT,
    SURVEY_INTRO_TEXT,
    SURVEY_SAVED_TEXT,
    WELCOME_TEXT,
)

router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext) -> None:
    await state.clear()
    user = message.from_user
    await db.upsert_user(user.id, user.username, user.first_name, status="started")
    await db.log_event(user.id, "start")
    await state.set_state(SurveyStates.waiting_contact)
    await message.answer(CONTACT_REQUEST_TEXT, reply_markup=contact_request_keyboard())


@router.message(SurveyStates.waiting_contact, F.contact)
async def receive_contact(message: Message, state: FSMContext) -> None:
    user = message.from_user
    if message.contact.user_id != user.id:
        return

    await db.save_phone_number(user.id, message.contact.phone_number)
    await db.log_event(user.id, "contact_shared")
    await state.set_state(None)
    await message.answer(WELCOME_TEXT, reply_markup=welcome_keyboard())


@router.callback_query(F.data == "welcome_next")
async def welcome_next(callback: CallbackQuery) -> None:
    user = callback.from_user
    await db.log_event(user.id, "welcome_next_clicked")
    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.message.answer(SURVEY_INTRO_TEXT, reply_markup=survey_keyboard([]))
    await callback.answer()


@router.callback_query(F.data.startswith("survey_toggle:"))
async def toggle_option(callback: CallbackQuery, state: FSMContext) -> None:
    code = callback.data.split(":", 1)[1]
    data = await state.get_data()
    selected = list(data.get("selected", []))

    if code == "custom":
        if "custom" in selected:
            selected.remove("custom")
            await state.update_data(selected=selected, custom_text=None)
            await callback.message.edit_reply_markup(reply_markup=survey_keyboard(selected))
        else:
            await state.update_data(survey_message_id=callback.message.message_id)
            await state.set_state(SurveyStates.waiting_custom_text)
            await callback.message.answer(SURVEY_CUSTOM_PROMPT)
        await callback.answer()
        return

    if code in selected:
        selected.remove(code)
    else:
        selected.append(code)
    await state.update_data(selected=selected)
    await callback.message.edit_reply_markup(reply_markup=survey_keyboard(selected))
    await callback.answer()


@router.message(SurveyStates.waiting_custom_text)
async def receive_custom_text(message: Message, state: FSMContext, bot: Bot) -> None:
    data = await state.get_data()
    selected = list(data.get("selected", []))
    if "custom" not in selected:
        selected.append("custom")
    await state.update_data(selected=selected, custom_text=message.text)
    await state.set_state(None)

    survey_message_id = data.get("survey_message_id")
    if survey_message_id:
        await bot.edit_message_reply_markup(
            chat_id=message.chat.id,
            message_id=survey_message_id,
            reply_markup=survey_keyboard(selected),
        )
    await message.answer("Отлично, спасибо 🤍 Можешь выбрать ещё варианты и нажать «Готово»")


@router.callback_query(F.data == "survey_done")
async def survey_done(callback: CallbackQuery, state: FSMContext, bot: Bot) -> None:
    data = await state.get_data()
    selected = data.get("selected", [])
    if not selected:
        await callback.answer("Выбери хотя бы один вариант 🤍", show_alert=True)
        return

    custom_text = data.get("custom_text")
    user = callback.from_user
    await db.upsert_user(user.id, user.username, user.first_name, status="answered_survey")
    await db.save_survey_answer(user.id, selected, custom_text)
    await db.log_event(user.id, "survey_submitted", {"selected": selected})

    admin_text = f"Новый ответ на опрос от @{user.username or user.id}: {selected}"
    if custom_text:
        admin_text += f"\nСвой вариант: {custom_text}"
    await notify_admin(bot, admin_text)

    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.message.answer(SURVEY_SAVED_TEXT)
    await callback.message.answer(POST2_TEXT, reply_markup=post2_keyboard())
    await state.clear()
    await callback.answer()
