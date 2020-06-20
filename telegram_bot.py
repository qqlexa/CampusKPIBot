from telegram.ext import Updater
from telegram.ext import Dispatcher
from telegram.ext import CommandHandler
from telegram.ext import MessageHandler, Filters

import campus_parser
import asyncio

from datetime import datetime
from threading import Thread

import time

import saver


class Queue:
    def __init__(self):
        """
        [
            user_id : int
            student_account : list (login, password)
        ],
        """
        self.queue = list()

    @property
    def len(self):
        return len(self.queue)

    def get_position(self, position=0):
        return self.queue[position]

    def delete_position(self, position=0):
        return self.queue.pop(position)

    def add_to_queue(self, queue_id, student_account, root=False):
        if root:
            self.queue.append([queue_id, student_account])
            return

        if not self.is_in_queue(queue_id):
            self.queue.append([queue_id, student_account])
            return "You added to queue"
        else:
            return "You are already in queue"

    def is_in_queue(self, queue_id):
        for i in self.queue:
            if i[0] == queue_id:
                return True
        return False


class PersonalThread(Thread):
    def __init__(self, telegram_bot):
        Thread.__init__(self)
        self.telegram_bot = telegram_bot

    def run(self):
        while True:
            while self.telegram_bot.queue.len:
                position = self.telegram_bot.queue.get_position()
                print(position)
                info, marks, message = self.telegram_bot.campus.get_campus_marks([position[1][0], position[1][1]])
                if not isinstance(message, str):
                    if len(info):
                        message = ""
                        for i in info:
                            message += i + "\n"
                        message += "\n"
                        for mark in marks:
                            message += str(mark) + "\n"

                        average_mark = round(sum([int(mark) for mark in marks]) / len(marks), 2)

                        message += "\nAverage: "
                        message += str(average_mark)

                if isinstance(message, str):
                    self.telegram_bot.context.bot.send_message(chat_id=position[0], text=message)
                self.telegram_bot.queue.delete_position()


class TelegramThread(Thread):
    def __init__(self, telegram_bot):
        Thread.__init__(self)
        self.telegram_bot = telegram_bot
        self.info_list = list()

    def sort_info(self):
        for i in range(len(self.info_list)):
            for j in range(0, len(self.info_list) - 1):
                try:
                    if self.info_list[j][1] < self.info_list[j + 1][1]:
                        self.info_list[j], self.info_list[j + 1] = self.info_list[j + 1], self.info_list[j]
                except BaseException:
                    pass
                    # print("Error sorting")

    def count_students_speciality(self, speciality):
        count = 0
        for info in self.info_list:
            if info[0][5] == speciality:
                count += 1
        return count

    def run(self):
        while self.telegram_bot.all_queue.len:
            position = self.telegram_bot.all_queue.get_position()
            print(position)
            info, marks, message = self.telegram_bot.campus.get_campus_marks([position[1][0], position[1][1]])
            if not isinstance(message, str):
                if len(info):
                    message = ""
                    for i in info:
                        message += i + "\n"
                    message += "\n"
                    for mark in marks:
                        message += str(mark) + "\n"
                    average_mark = round(sum([int(mark) for mark in marks]) / len(marks), 2)

                    message += "\nAverage: "
                    message += str(average_mark)
                    print(average_mark)
                    self.info_list.append([info, average_mark])

            if isinstance(message, str):
                self.telegram_bot.context.bot.send_message(chat_id=position[0], text=message)
            try:
                self.telegram_bot.all_queue.delete_position()
            except BaseException:
                pass

        # sort_info
        self.sort_info()

        # save
        keeper = saver.Saver()
        for info in self.info_list:
            keeper.save_info([info[0], info[1]], len(info[0]))

        self.telegram_bot.thread_status = False


class TelegramBot(object):

    def __init__(self, token):
        self.updater = Updater(token, use_context=True)

        self.updater.dispatcher.add_handler(CommandHandler('start', self.start_command))
        self.updater.dispatcher.add_handler(CommandHandler('help', self.help_command))
        self.updater.dispatcher.add_handler(CommandHandler('login', self.login_command))
        self.updater.dispatcher.add_handler(CommandHandler('logins', self.logins_command))

        self.updater.dispatcher.add_handler(MessageHandler(Filters.text & (~Filters.command), self.echo))

        self.campus = campus_parser.Campus()
        self.queue = Queue()
        self.all_queue = Queue()

        self.context = None
        self.personal_status = False
        self.thread_status = False

        self.qqlexa_id = 440973597

    def start(self):
        self.updater.start_polling()

    @staticmethod
    def start_command(update, context):
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text="I'm a bot for getting information about your campus account")

    @staticmethod
    def help_command(update, context):
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text="/login $login $password")

    @staticmethod
    def echo(update, context):
        delta = datetime.utcnow().second - update.message["date"].second
        if abs(delta) < 2:
            context.bot.send_message(chat_id=update.effective_chat.id,
                                     text=update.message.text)

    def login_command(self, update, context):
        self.context = context
        delta = datetime.utcnow().second - update.message["date"].second
        if abs(delta) < 2:
            info = update.message.text.split()
            if len(info) == 3:
                add_answer = self.queue.add_to_queue(update.message.from_user.id, [info[1], info[2]])

                context.bot.send_message(chat_id=update.effective_chat.id,
                                         text=add_answer)
                if not self.personal_status:
                    self.personal_status = True
                    thread = PersonalThread(self)
                    thread.start()
            else:
                self.help_command(context, update)

    def logins_command(self, update, context):
        self.context = context
        delta = datetime.utcnow().second - update.message["date"].second
        if abs(delta) < 2:
            if not self.thread_status and update.message.from_user.id == self.qqlexa_id:
                context.bot.send_message(chat_id=update.effective_chat.id, text="It is running")

                self.thread_status = True

                self.campus.add_logs_passwords(path="E:\\STUDYING\\pass.txt")  # TM 91
                for student_account in self.campus.auth_info:
                    self.all_queue.add_to_queue(update.message.from_user.id, student_account, root=True)

                thread = TelegramThread(self)
                thread.start()
            else:
                context.bot.send_message(chat_id=update.effective_chat.id, text="It is already working")


if __name__ == '__main__':
    bot = TelegramBot('1283008038:AAGWriN3_a6ibRVkZuiZjehgL-rFLVkgDh8')
    bot.start()
