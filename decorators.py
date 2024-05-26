import os
from functools import wraps

from aiogram.types import CallbackQuery, Message
from dotenv import load_dotenv
from icecream import ic

from database import UsersDatabase

load_dotenv()
admin_ids_str = os.getenv("ADMIN_IDS").split(',')
ADMIN_IDS = [int(i) for i in admin_ids_str]


def is_admin():
    def is_admin_decorator(func):
        @wraps(func)
        async def wrapper(message: Message, *args, **kwargs):
            user_id = message.from_user.id
            if user_id not in ADMIN_IDS:
                await message.answer('У Вас нет доступа к этой команде.')
                state = kwargs.get('state')
                if state:
                    await state.clear()
                return
            return await func(message, *args, **kwargs)
        return wrapper
    return is_admin_decorator


def is_user_or_admin():
    def is_user_or_admin_decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            if len(args) > 0:
                # Check if the first argument is Message or CallbackQuery
                if isinstance(args[0], (Message, CallbackQuery)):
                    message_or_query = args[0]
                    user_id = message_or_query.from_user.id
                    if isinstance(message_or_query, CallbackQuery):
                        user_id = message_or_query.message.chat.id

                    users_db = UsersDatabase()
                    users_ids = [user_id[0] for user_id in users_db.show_all_users()]
                    users_db.close()

                    # ic(user_id)
                    # ic(users_ids)
                    # ic(ADMIN_IDS)

                    if user_id not in users_ids and user_id not in ADMIN_IDS:
                        if isinstance(message_or_query, Message):
                            await message_or_query.answer('У Вас нет доступа к этой команде.')
                        elif isinstance(message_or_query, CallbackQuery):
                            await message_or_query.answer('У Вас нет доступа к этой команде.')

                        state = kwargs.get('state')
                        if state:
                            await state.clear()
                        return
            return await func(*args, **kwargs)
        return wrapper
    return is_user_or_admin_decorator
