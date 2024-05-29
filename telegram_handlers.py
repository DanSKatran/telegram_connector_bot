import logging
import os
from functools import wraps
from sqlite3 import IntegrityError

from aiogram import Bot, Dispatcher, F
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, CallbackQuery
from aiogram.utils.markdown import hbold
from dotenv import load_dotenv

from database import UsersDatabase
from decorators import is_user_or_admin, is_admin
from keyboards import user_keyboard_markup, UsersKeyboards, CancelActionCallback, disable_all_buttons, \
    AnswerCustomerCallback

load_dotenv()
TOKEN = os.getenv("TOKEN_DAN")
admin_ids_str = os.getenv("ADMIN_IDS").split(',')
ADMIN_IDS = [int(i) for i in admin_ids_str]

# Pythonanywhere free version
# from aiogram.client.session.aiohttp import AiohttpSession
# session = AiohttpSession(proxy="http://proxy.server:3128")
# bot = Bot(TOKEN, session=session, parse_mode=ParseMode.HTML)

# comment this if youse Pythonanywhere free version
bot = Bot(TOKEN, parse_mode=ParseMode.HTML)

dp = Dispatcher()


class Form(StatesGroup):
    add_user = State()
    delete_user = State()
    ask_question = State()
    replying_customer = State()


async def launch_bot() -> None:
    await dp.start_polling(bot)


@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    """
    This handler receives messages with `/start` command
    """
    await message.answer(
        text=f"Здравствуйте,\n"
             f"Сделайте заказ продукции. Мы подберем Вам поставщиков.",
        reply_markup=user_keyboard_markup
        )


@dp.callback_query(CancelActionCallback.filter(F.foo == 'cancel_action'))
async def command_cancel_action(
        query: CallbackQuery,
        callback_data: CancelActionCallback,
        state: FSMContext,
):
    await state.clear()
    if query.message.reply_markup:
        disabled_keyboard = disable_all_buttons(query.message.reply_markup)
        await query.message.edit_reply_markup(reply_markup=disabled_keyboard)

    await query.message.answer('Действие отменено')


@dp.message(Command('id'))
async def command_id(message: Message) -> None:
    """
    This handler receives messages with `/start` command
    """
    if message.chat.id == message.from_user.id:
        await message.answer(f"Ваш, id: {hbold(message.from_user.id)}")
    else:
        await message.answer(f"ID Группы: {hbold(message.chat.id)}\n"
                             f"Ваш, id: {hbold(message.from_user.id)}")


@dp.message(Command('help'))
async def command_help_handler(message: Message) -> None:
    users_db = UsersDatabase()
    users_ids = users_db.show_all_users()
    users_db.close()

    user_id = message.from_user.id

    if user_id not in users_ids and user_id not in ADMIN_IDS:
        await message.answer(
            f"/start - начать\n"
            f"/help - список доступных команд\n"
            f"/id - узнать мой id\n"
            f"/ask_question - спросить вопрос\n\n"
        )
        return

    await message.answer(
        f"/start - начать\n"
        f"/help - список доступных команд\n"
        f"/id - узнать мой id\n"
        f"/ask_question - спросить вопрос\n\n"
        
        f"/show_users - показать юзеров\n"
        f"/add_user - добавить юзера\n"
        f"/delete_user - удалить юзера\n\n"
    )


# MANAGE USERS
@dp.message(Command('show_users'))
@is_admin()
async def command_show_users(message: Message) -> None:
    users_db = UsersDatabase()
    users_ids = users_db.show_all_users()
    users_db.close()
    await message.answer(
        f'Список пользователей:\n'
        f'{hbold(users_ids)}'
    )

@dp.message(Command('add_user'))
@is_admin()
async def command_add_user(message: Message, state: FSMContext) -> None:
    await message.answer(
        'Введите id чтобы ДОБАВИТЬ в список:'
    )
    await state.set_state(Form.add_user)


@dp.message(Form.add_user)
@is_admin()
async def adding_user(message: Message, state: FSMContext) -> None:
    try:
        telegram_id: int = int(message.text)
    except ValueError as e:
        logging.error('ValueError: TELEGRAM_ID is not integer')
        await message.answer(
            'TELEGRAM_ID не число.'
        )
        await state.clear()
        return

    users_db = UsersDatabase()
    try:
        users_db.add_user(telegram_id)
        await message.answer(
            f'Пользователь {telegram_id} добавлен.'
        )

    except IntegrityError:
        await message.answer(
            f'Пользователь c ID: {telegram_id} уже существует.'
        )

    finally:
        users_db.close()
        await state.clear()


@dp.message(Command('delete_user'))
@is_admin()
async def command_delete_user(message: Message, state: FSMContext) -> None:
    await message.answer(
        'Введите id чтобы УДАЛИТЬ в юзера:'
    )
    await state.set_state(Form.delete_user)


@dp.message(Form.delete_user)
@is_admin()
async def deleting_user(message: Message, state: FSMContext) -> None:
    try:
        telegram_id: int = int(message.text)
    except ValueError as e:
        logging.error(f'ValueError: {message.text} is not integer')
        await message.answer(
            'TELEGRAM_ID is not integer'
        )
        await state.clear()
        return

    print('deleting user')
    users_db = UsersDatabase()
    users_db.delete_user(telegram_id)
    users_db.close()
    await state.clear()
    await message.answer(
        f'Пользователь {telegram_id} удален.'
    )


# MANAGE Communication
@dp.message(Command('ask_question'))
async def command_ask_question(message: Message, state: FSMContext) -> None:
    await message.answer(
        'Введите ваш вопрос в свободной форме:'
    )
    await state.set_state(Form.ask_question)


@dp.message(Form.ask_question)
async def asking_question(message: Message, state: FSMContext) -> None:
    question = message.text
    customer_id = message.from_user.id
    customer_name = message.from_user.full_name

    await send_question_to_users(question, customer_id, customer_name)
    await message.answer(
        'Ищем Вам поставщиков (займет около 1 часа)'
    )
    await state.clear()


async def send_question_to_users(question, customer_id, customer_name) -> None:
    users_db = UsersDatabase()
    users_ids: list[tuple[int]] = users_db.show_all_users()
    users_db.close()
    keyboard = UsersKeyboards().reply_question_keyboard(
        customer_id=customer_id,
        name=customer_name
    )
    for i in users_ids:
        try:
            message = (
                f'Клиент: {customer_name}\n'
                f'Оставил заявку:\n'
                f'{question}'
            )
            user_id = int(i[0])
            await bot.send_message(
                user_id,
                message,
                reply_markup=keyboard
            )
        except Exception as e:
            logging.error(f'{e}')


@dp.callback_query(AnswerCustomerCallback.filter(F.foo == 'answer_customer'))
@is_user_or_admin()
async def command_answer_customer(
        query: CallbackQuery,
        callback_data: AnswerCustomerCallback,
        state: FSMContext,
) -> None:
    user_id = callback_data.data
    await query.message.answer(
        f'Напишите Ваш ответ ({user_id}) в свободной форме:'
    )
    disabled_keyboard = disable_all_buttons(query.message.reply_markup)
    await query.message.edit_reply_markup(reply_markup=disabled_keyboard)
    await state.set_state(Form.replying_customer)
    await state.update_data(replying_customer=user_id)


@dp.message(Form.replying_customer)
@is_user_or_admin()
async def replying_customer(
        query: CallbackQuery,
        state: FSMContext,
) -> None:
    reply_message = query.message.text
    customer_id = (await state.get_data()).get("replying_customer")
    await query.message.answer(
        f'Ваш ответ был отправлен: {customer_id}\n'
        f'{reply_message}'
    )
    await bot.send_message(
        customer_id,
        reply_message,
    )
    await state.clear()
