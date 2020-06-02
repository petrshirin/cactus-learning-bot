from webhook_handler.models import *
from telebot import TeleBot, types, apihelper
from django.db.models import Q
from django.utils import timezone


class CommonAction:

    def __init__(self, bot, message, user):
        self.bot = bot
        self.message = message
        self.user = user

    def welcome_action(self):
        message_text = '''Доброго пожаловать!
        Этот бот поможет вам получать новые знания
        Если вы студент, выберите и впервые с нами:
            1. Возьмите у своего преподавателя код курса
            2. Активируйте его в боте
            3. Начинайте учиться
        Чтобы перейти в интерфейс преподавателя - /teacher
        Вернуться к интерфейсу студента - /student'''
        self.bot.send_message(chat_id=self.message.chat.id, text=message_text)

    def switch_to_student(self):
        message_text = '''Теперь вы студент! Чтобы начать учиться:
                    1. Возьмите у своего преподавателя код курса
                    2. Активируйте его в боте
                    3. Начинайте учиться
                Чтобы перейти в интерфейс преподавателя - /teacher
                Вернуться к интерфейсу студента - /student'''
        self.user.status = 1
        self.user.save()
        self.bot.send_message(chat_id=self.message.chat.id, text=message_text)

    def switch_to_teacher(self):
        message_text = '''Теперь вы Преподаватель!'''
        self.user.status = 2
        self.user.save()
        self.bot.send_message(chat_id=self.message.chat.id, text=message_text)








