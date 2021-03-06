#!/usr/bin/env python

import telebot
import logging
import flask
import configparser
import pixiv

config = configparser.ConfigParser()
config.sections()
config.read('pixbot.conf')
requests_kwargs = None

API_TOKEN = config['init']['bot_token']

WEBHOOK_HOST = config['init']['url']
WEBHOOK_PORT = int(config['init']['server_port'])
WEBHOOK_PORT_PROXY = int(config['init']['proxy_port'])
WEBHOOK_LISTEN = '0.0.0.0'

pixiv.pixiv_username = config['init']['pixiv_username']
pixiv.pixiv_password = config['init']['pixiv_password']

if config.has_option('init', 'requests_kwargs'):
    requests_kwargs = config['init']['requests_kwargs'].replace('\n', '')
    requests_kwargs = eval(requests_kwargs)

p = pixiv.pixiv_crewler(**requests_kwargs)

WEBHOOK_URL_BASE = 'https://%s:%s' % (WEBHOOK_HOST, WEBHOOK_PORT)
WEBHOOK_URL_PATH = '/%s/' % (API_TOKEN)

logger = telebot.logger
telebot.logger.setLevel(logging.INFO)

bot = telebot.TeleBot(API_TOKEN)
app = flask.Flask(__name__)

def help(message):
    print('help')
    bot.reply_to(message, '/pixbot [keyword list] - find image from pixiv using keywords.')

def get_image(message):
    global p
    keywords = message.text.split(' ')[1:]
    image = p.get_image(keywords)
    bot.reply_to(message, image['origin'])

# Empty webserver index, return nothing, just http 200
@app.route('/', methods=['GET', 'HEAD'])
def index():
    return ''

# Process webhook calls
@app.route(WEBHOOK_URL_PATH, methods=['POST'])
def webhook():
    if flask.request.headers.get('content-type') == 'application/json':
        json_string = flask.request.get_data()
        try:
            json_string = json_string.decode('utf-8')
            update = telebot.types.Update.de_json(json_string)
        except:
            print('get except')
            print(json_string)
            return ''
        bot.process_new_messages([update.message])
        return ''
    else:
        flask.abort(403)

# Handle '/pixbot'
@bot.message_handler(commands=['pixbot'])
def parse_command(message):
    print('get command ' + message.text)
    func_dict = {
        'help': lambda message: help(message),
        'pixiv': lambda message: get_image(message)
    }
    m = message.text.split(' ')
    if len(m) >= 2:
        if m[1].lower() in func_dict:
            func_dict[m[1]](message)
        else:
            func_dict['pixiv'](message)

@bot.message_handler(func=lambda message: True)
def echo_message(message):
    print('>>echo_message: ' + message.text)
    bot.reply_to(message, message.text)

# Remove webhook, it fails sometimes the set if there is a previous webhook
bot.remove_webhook()

# Set webhook
bot.set_webhook(url = WEBHOOK_URL_BASE + WEBHOOK_URL_PATH)
# start flask server

app.run(host=WEBHOOK_LISTEN,
        port=WEBHOOK_PORT_PROXY,
        debug=True)
