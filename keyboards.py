from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup

ask_question_btn = KeyboardButton(text='/ask_question')

user_keyboard = [
    [ask_question_btn]
]
user_keyboard_markup = ReplyKeyboardMarkup(
    resize_keyboard=True,
    keyboard=user_keyboard
)

class CancelActionCallback(CallbackData, prefix='cancel_action'):
    foo: str


class AnswerCustomerCallback(CallbackData, prefix='answer_customer'):
    foo: str
    data: str


def disable_all_buttons(keyboard: InlineKeyboardMarkup) -> InlineKeyboardMarkup:
    new_buttons = []

    for row in keyboard.inline_keyboard:
        new_row = []
        for button in row:
            new_button = InlineKeyboardButton(text=button.text, callback_data="disabled")
            new_row.append(new_button)
        new_buttons.append(new_row)

    disabled_keyboard = InlineKeyboardMarkup(inline_keyboard=new_buttons)
    return disabled_keyboard


class UsersKeyboards:

    def reply_question_keyboard(self, customer_id, name):
        buttons = [
            [
                InlineKeyboardButton(
                    text=f'Ответить клиенту: {name}',
                    callback_data=AnswerCustomerCallback(
                        foo='answer_customer',
                        data=f'{customer_id}'
                    ).pack()
                )
            ]
        ]

        reply_keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
        return reply_keyboard

