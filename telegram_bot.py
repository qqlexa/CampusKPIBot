from telegram.ext import Updater
from telegram.ext import Dispatcher
from telegram.ext import CommandHandler
from telegram.ext import MessageHandler, Filters

import campus_parser
import asyncio


class DialogBot(object):

    def __init__(self, token):
        self.updater = Updater(token, use_context=True)

        self.updater.dispatcher.add_handler(CommandHandler('start', self.start_command))
        self.updater.dispatcher.add_handler(CommandHandler('login', self.login_command))

        self.updater.dispatcher.add_handler(MessageHandler(Filters.text & (~Filters.command), self.echo))

        self.campus = campus_parser.Campus()

    def start(self):
        self.updater.start_polling()

    @staticmethod
    def start_command(context, update):
        context.bot.send_message(chat_id=update.effective_chat.id, text="I'm a bot, please talk to me!")

    @staticmethod
    def help_command(context, update):
        context.bot.send_message(chat_id=update.effective_chat.id, text="I'm a bot, please talk to me!")

    @staticmethod
    def echo(update, context):
        context.bot.send_message(chat_id=update.effective_chat.id, text=update.message.text)

    def login_command(self, update, context):
        context.bot.send_message(chat_id=update.effective_chat.id, text="Hi")
        print("Hi")
        print(update.message.text)
        info = update.message.text.split()
        if len(info) == 3:
            print("OKAY")
            asyncio.run(self.get_marks([info[1], info[2]], update, context))

    async def get_marks(self, student_account, update, context):
        info, marks = await self.campus.get_campus_marks(student_account)

        faculty = info[0]
        group = info[1]
        form_studying = info[2]
        course_studying = info[3]
        speciality = info[4]
        is_studying = info[5]

        context.bot.send_message(chat_id=update.effective_chat.id, text=faculty)
        context.bot.send_message(chat_id=update.effective_chat.id, text=group)
        context.bot.send_message(chat_id=update.effective_chat.id, text=form_studying)
        context.bot.send_message(chat_id=update.effective_chat.id, text=course_studying)
        context.bot.send_message(chat_id=update.effective_chat.id, text=speciality)
        context.bot.send_message(chat_id=update.effective_chat.id, text=is_studying)

        context.bot.send_message(chat_id=update.effective_chat.id, text="Your marks:")

        for mark in marks:
            context.bot.send_message(chat_id=update.effective_chat.id, text=mark)


if __name__ == '__main__':
    bot = DialogBot(TOKEN)
    bot.start()


