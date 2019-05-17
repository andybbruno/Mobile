#!/usr/bin/env python
# -*- coding: utf-8 -*-
# This program is dedicated to the public domain under the CC0 license.
#
# THIS EXAMPLE HAS BEEN UPDATED TO WORK WITH THE BETA VERSION 12 OF PYTHON-TELEGRAM-BOT.
# If you're still using version 11.1.0, please see the examples at
# https://github.com/python-telegram-bot/python-telegram-bot/tree/v11.1.0/examples

"""
Simple Bot to reply to Telegram messages.
First, a few handler functions are defined. Then, those functions are passed to
the Dispatcher and registered at their respective places.
Then, the bot is started and runs until we press Ctrl-C on the command line.
Usage:
Basic Echobot example, repeats messages.
Press Ctrl-C on the command line or send a signal to the process to stop the
bot.
"""

import logging
import os

import pymongo

_mongoDB = pymongo.MongoClient("mongodb://ec2-18-212-110-170.compute-1.amazonaws.com:27017/")
_mobile_db = _mongoDB["test_db"]

machineTable = _mobile_db["testTable"]
detectionTable = _mobile_db["testDetection"]

from telegram.ext import Updater, CommandHandler, MessageHandler, Filters

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)


# Define a few command handlers. These usually take the two arguments bot and
# update. Error handlers also receive the raised TelegramError object in error.
def start(context, update):
    """Send a message when the command /start is issued."""
    update.message.reply_text("I'm a bot, please talk to me! I sooo sad and lonely 😭")

def help(context, update):
    """Send a message when the command /help is issued."""
    update.message.reply_text('Bot di prova che simula sia le richeste per i clienti che per gli operatori.\n /coffee -> per richiedere la lista delle macchine vicine con la relativa lista\n /schedule -> lista delle macchinette da rifornire o sistemare.')

def echo(context, update):
    """Echo the user message."""
    update.message.reply_text(update.message.text)


def coff(context, update):
    """Echo the user message."""
    cursor = detectionTable.aggregate([{
        "$group": {
            "_id": "$machineID",
            "time": { "$max": "$timestamp" }
        }
    }])
    res = ""
    from datetime import datetime as time
    for ele in cursor:
        numP = detectionTable.find_one({"timestamp": ele["time"]})["people_detected"]
        if abs((time.now() - time.fromtimestamp(ele["time"])).seconds) > 5*60:
            res += "\n" + str(ele["_id"]) + " -> N.p 0"
        else:
            res += "\n" + str(ele["_id"]) + " -> N.p " + str(numP)

    update.message.reply_text("Ecco la liste delle macchinette più vicine a te:" + res)

def macc(context, update):
    """Echo the user message."""
    cursor = machineTable.find()
    res = ""
    for ele in cursor:
        if ele["working"] == False:
            res += "\n" + str(ele["ID"]) + " not work"
        if any([e < 20 for e in ele["maintenance"]["consumable_list"].values()]):
            res += "\n" + str(ele["ID"]) + " to refill"
    update.message.reply_text("Le macchine che hanno bisogno di un abbraccio sono: " + res)


def error(context, update):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)


def main():
    """Start the bot."""
    # Create the Updater and pass it your bot's token.
    # Make sure to set use_context=True to use the new context based callbacks
    # Post version 12 this will no longer be necessary
    TOKEN = "843232086:AAGPulZowOM60Sp_gTClV6YTw5uVC7ryLRo"
    PORT = int(os.environ.get('PORT', '8443'))
    updater = Updater(TOKEN)
    
    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help))
    dp.add_handler(CommandHandler("coffee", coff))
    dp.add_handler(CommandHandler("schedule", macc))
    

    # on noncommand i.e message - echo the message on Telegram
    dp.add_handler(MessageHandler(Filters.text, echo))

    # log all errors
    dp.add_error_handler(error)

    HEROKU_APP_NAME = os.environ.get("HEROKU_APP_NAME")
    updater.start_webhook(listen="0.0.0.0",
                        port=PORT,
                        url_path=TOKEN)
    updater.bot.set_webhook("https://{}.herokuapp.com/{}".format(HEROKU_APP_NAME, TOKEN))
    updater.idle()

if __name__ == '__main__':
    main()
