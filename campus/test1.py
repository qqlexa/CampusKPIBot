import asyncio

import time
from datetime import datetime
import os
from threading import Thread

from telegram.ext import Updater
from telegram.ext import Dispatcher
from telegram.ext import CommandHandler
from telegram.ext import MessageHandler, Filters

import campus_parser
import saver

import logging

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton, Update
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, CallbackContext

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)

"""def start(update: Update, context: CallbackContext) -> None:
    print("Started")
    keyboard = [
        [
            InlineKeyboardButton("Option 1", callback_data='1'),
            InlineKeyboardButton("Option 2", callback_data='2'),
        ],
        [
            InlineKeyboardButton("Option 3", callback_data='3')
        ],
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    update.message.reply_text('Please choose:', reply_markup=reply_markup)
"""


def start(update: Update, context: CallbackContext) -> None:
    print("Started")

    keyboard = [
        [
            InlineKeyboardButton("Повернутися до меню 'Сесія'", callback_data='3')
        ],

    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    update.message.reply_text(f"2020-12-24 10:00:00\n"
                              f"Екологічний моніторинг\n"
                              f"Залік: 98\n"
                              f"А Б В", reply_markup=reply_markup)


def certification_command(update: Update, context: CallbackContext) -> None:
    keyboard = [
        [
            InlineKeyboardButton("Семестр 1", callback_data='_')
        ],
        [
            InlineKeyboardButton("Атестація 1", callback_data='_'),
            InlineKeyboardButton("Атестація 2", callback_data='_'),
        ],

        [
            InlineKeyboardButton("НазваПредмету_1", callback_data='_')
        ],
        [
            InlineKeyboardButton("а", callback_data='_'),
            InlineKeyboardButton("а", callback_data='_'),
        ],

        [
            InlineKeyboardButton("НазваПредмету_2", callback_data='_')
        ],
        [
            InlineKeyboardButton("н/а", callback_data='_'),
            InlineKeyboardButton("н/а", callback_data='_'),
        ],

        [
            InlineKeyboardButton("ДужеДовгаНазваПредмету_1", callback_data='_')
        ],
        [
            InlineKeyboardButton("а", callback_data='_'),
            InlineKeyboardButton("а", callback_data='_'),
        ],

        [
            InlineKeyboardButton("ДужеДовгаНазваПредмету_2", callback_data='_')
        ],
        [
            InlineKeyboardButton("н/а", callback_data='_'),
            InlineKeyboardButton("н/а", callback_data='_'),
        ],

        [
            InlineKeyboardButton("Семестр 2", callback_data='_')
        ],
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text(f"@{update.effective_user.username}, атестація", reply_markup=reply_markup)


def session_command(update: Update, context: CallbackContext) -> None:
    keyboard = [
        [
            InlineKeyboardButton("НазваПредмету_1", callback_data='_')
        ],
        [
            InlineKeyboardButton("01.01.2021", callback_data='_'),
            InlineKeyboardButton("100", callback_data='_'),
        ],

        [
            InlineKeyboardButton("НазваПредмету_2", callback_data='_')
        ],
        [
            InlineKeyboardButton("02.01.2021", callback_data='_'),
            InlineKeyboardButton("_", callback_data='_'),
        ],

        [
            InlineKeyboardButton("ДужеДовгаНазваПредмету_1", callback_data='_')
        ],
        [
            InlineKeyboardButton("01.01.2021", callback_data='_'),
            InlineKeyboardButton("100", callback_data='_'),
        ],

        [
            InlineKeyboardButton("ДужеДовгаНазваПредмету_2", callback_data='_')
        ],
        [
            InlineKeyboardButton("02.01.2021", callback_data='_'),
            InlineKeyboardButton("_", callback_data='_'),
        ],

        [
            InlineKeyboardButton("Середній бал: 100", callback_data='3')
        ],
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text(f"@{update.effective_user.username}, сесія", reply_markup=reply_markup)


def button(update: Update, context: CallbackContext) -> None:
    print("Button")
    query = update.callback_query

    # CallbackQueries need to be answered, even if no notification to the user is needed
    # Some clients may have trouble otherwise. See https://core.telegram.org/bots/api#callbackquery
    query.answer()

    query.edit_message_text(text=f"Selected option: {query.data}")


def help_command(update: Update, context: CallbackContext) -> None:
    print("help")
    update.message.reply_text("Use /start to test this bot.")
    

def auth_command(update: Update, context: CallbackContext) -> None:
    print("auth")
    """Ask user to create a poll and display a preview of it"""
    # using this without a type lets the user chooses what he wants (quiz or poll)
    keyboard = [
        [
            KeyboardButton("Повернутися до меню 'Сесія'", callback_data='3')
        ]
    ]
    message = "Press the button to let the bot generate a preview for your poll"
    # using one_time_keyboard to hide the keyboard
    update.effective_message.reply_text(
        'Повернутися', reply_markup=ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)
    )


def main():
    # Create the Updater and pass it your bot's token.
    # Make sure to set use_context=True to use the new context based callbacks
    # Post version 12 this will no longer be necessary
    with open(os.path.dirname(__file__) + "/resources/TOKEN") as f:
        for read in f:
            token = read

    updater = Updater(token, use_context=True)

    updater.dispatcher.add_handler(CommandHandler('start', start))
    updater.dispatcher.add_handler(CallbackQueryHandler(button))
    updater.dispatcher.add_handler(CommandHandler('help', help_command))
    updater.dispatcher.add_handler(CommandHandler('auth', auth_command))
    updater.dispatcher.add_handler(CommandHandler('a', certification_command))
    updater.dispatcher.add_handler(CommandHandler('s', session_command))

    # Start the Bot
    updater.start_polling()

    # Run the bot until the user presses Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT
    updater.idle()


if __name__ == '__main__':
    main()
