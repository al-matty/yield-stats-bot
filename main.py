#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Basic bot framework forked from Andrés Ignacio Torres <andresitorresm@gmail.com>,
all other files by Al Matty <al@almatty.com>.
"""
import time, os
import random
import logging
from telegram.ext import CommandHandler, Filters, MessageHandler, Updater


class MerchBot:
    """
    A class to encapsulate all relevant methods of the bot.
    """

    def __init__(self):
        """
        Constructor of the class. Initializes certain instance variables
        and checks if everything's O.K. for the bot to work as expected.
        """

        # This environment variable should be set before using the bot
        self.token = os.environ['STATS_BOT_TOKEN']


        # These will be checked against as substrings within each
        # message, so different variations are not required if their
        # radix is present (e.g. "all" covers "/all" and "ball")
        self.menu_trigger = ['/all', '/stats']
        self.loan_stats_trigger = ['/loans']
        self.il_trigger = ['/IL']
        self.assets_trigger = ['/assets']


        # Stops runtime if the token has not been set
        if self.token is None:
            raise RuntimeError(
                "FATAL: No token was found. " + \
                "You might need to specify one or more environment variables.")

        # Configures logging in debug level to check for errors
        logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                            level=logging.INFO)


    def run_bot(self):
        """
        Sets up the required bot handlers and starts the polling
        thread in order to successfully reply to messages.
        """

        # Instantiates the bot updater
        self.updater = Updater(self.token, use_context=True)
        self.dispatcher = self.updater.dispatcher

        # Declares and adds a handler for text messages that will reply with
        # content if a user message includes a trigger word
        text_handler = MessageHandler(Filters.text, self.handle_text_messages)
        self.dispatcher.add_handler(text_handler)

        # Fires up the polling thread. We're live!
        self.updater.start_polling()


    def send_textfile(self, textfile, update, context):
        """
        Takes a textfile (path) and sends it as mesage to the user.
        """

        with open(textfile, 'r') as file:
            MSG = file.read()

        context.bot.send_message(chat_id=update.message.chat_id, text=MSG)


    def send_str(self, msg_str, update, context):
        """
        Takes a string and sends it as mesage to the user.
        """
        MSG = msg_str
        context.bot.send_message(chat_id=update.message.chat_id, text=MSG)


    def show_menu(self, update, context):
        """
        Shows the menu with current items.
        """
        msg_file = 'menu_msg.txt'
        self.send_textfile(msg_file, update, context)


    def send_signature(self, update, context):
        """
        Sends out a signature message specified in a text file.
        """
        msg_file = 'signature_msg.txt'
        self.send_textfile(msg_file, update, context)


    def sendPic(self, pic_file, update, context, caption=None):
        """
        Sends picture as specified in pic_file.
        """

        # Send image
        with open(pic_file, 'rb') as img:

            # Sends the picture
            context.bot.send_photo(
                chat_id=update.message.chat_id,
                photo=img,
                caption=caption
                )

        # Some protection against repeatedly calling a bot function
        time.sleep(0.3)


    def show_loan_stats(self, update, context):
        """
        Sends out a preliminary message plus the loan stats infographic.
        """

        # Send preliminary message
        msg = 'Some message...'
        self.send_str(msg, update, context)

        # Send pic
        self.sendPic('loans.png', update, context)


    def show_il(self, update, context):
        """
        Sends out a preliminary message plus the IL infographic.
        """

        # Send preliminary message
        msg = 'Some other message...'
        self.send_str(msg, update, context)

        # Send pic
        self.sendPic('il.png', update, context)


    def show_assets(self, update, context):
        """
        Sends out a preliminary message plus the IL infographic.
        """

        # Send preliminary message
        msg = 'Some other message...'
        self.send_str(msg, update, context)

        # Send pic
        self.sendPic('assets.png', update, context)


    def handle_text_messages(self, update, context):
        """
        Encapsulates all logic of the bot to conditionally reply with content
        based on trigger words.
        """

        # Split user input into single words
        words = set(update.message.text.lower().split())
        logging.debug(f'Received message: {update.message.text}')

        # For debugging: Log users that received something from bot
        chat_user_client = update.message.from_user.username
        if chat_user_client == None:
            chat_user_client = update.message.chat_id


        # Possibility: received command from menu_trigger
        for Trigger in self.menu_trigger:
            for word in words:
                if word.startswith(Trigger):

                    self.show_menu(update, context)
                    logging.info(f'{chat_user_client} checked out the menu!')

                    return


        # Possibility: received command from loan_stats_trigger
        for Trigger in self.loan_stats_trigger:
            for word in words:
                if word.startswith(Trigger):

                    #self.send_textfile('under_construction.txt', update, context)
                    self.show_loan_stats(update, context)
                    self.send_signature(update, context)
                    logging.info(f'{chat_user_client} got loan stats!')

                    return

        # Possibility: received command from il_trigger
        for Trigger in self.il_trigger:
            for word in words:
                if word.startswith(Trigger):

                    self.send_textfile('under_construction.txt', update, context)
                    #self.show_il(update, context)
                    #self.send_signature(update, context)
                    logging.info(f'{chat_user_client} tried to get IL info!')

                    return

        # Possibility: received command from assets_trigger
        for Trigger in self.assets_trigger:
            for word in words:
                if word.startswith(Trigger):

                    self.send_textfile('under_construction.txt', update, context)
                    #self.self.show_assets(update, context)
                    #self.send_signature(update, context)
                    logging.info(f'{chat_user_client} tried to get asset info!')

                    return



def main():
    """
    Entry point of the script. If run directly, instantiates the
    MerchBot class and fires it up!
    """

    merch_bot = MerchBot()
    merch_bot.run_bot()


# If the script is run directly, fires the main procedure
if __name__ == "__main__":
    main()
