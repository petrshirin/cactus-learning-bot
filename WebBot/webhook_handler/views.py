from django.http import HttpResponse
import json
import logging
from telebot import TeleBot, types
from django.conf import settings

# Create your views here.

bot = TeleBot(settings['BOT_TOKEN'])


def get_web_hook(request, token):
    global bot
    json_data = json.loads(request.body)
    if not bot.token:
        print('fail bot')
        return HttpResponse('fail bot', status=500)
    update = types.Update.de_json(json_data)
    bot.process_new_updates([update])
    return HttpResponse('ok', status=200)
