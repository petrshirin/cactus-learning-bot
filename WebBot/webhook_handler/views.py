from django.http import HttpResponse
import json
import logging
from telebot import TeleBot, types
from django.conf import settings

#from .bot.bot_logic import *

# Create your views here.
bot = TeleBot('686614144:AAEKIVMLl18RiNDGUlKHpFLZf9KoXTnRD98')


def get_web_hook(request, token):
    global bot
    json_data = json.loads(request.body)
    if not bot.token:
        logging.error('fail bot')
        return HttpResponse('fail bot', status=500)
    update = types.Update.de_json(json_data)
    bot.process_new_updates([update])
    return HttpResponse('ok', status=200)
