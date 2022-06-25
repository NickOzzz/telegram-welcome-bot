import json
from typing import Callable
from telegram import Update
from telegram.ext import Updater, MessageHandler, Filters, CallbackContext
appsettings = "appsettings.json"


class App:
    def __init__(self, token: str, action):
        print("Starting app")
        updater = Updater(token)
        updater.dispatcher.add_handler(MessageHandler(filters=Filters.all, callback=action))
        updater.start_polling()
        updater.idle()
        print("finishing app")


class WelcomeMessage:
    def __init__(self, update: Update, context: CallbackContext):
        self.update = update
        self.context = context
        self.chat_id = update.message.chat.id
        self.message_id = update.message.message_id + 1
        self.photo_id = update.message.message_id + 2
        self.username = update.message.from_user.username
        self.config = JsonReader(file_path=appsettings).read_and_return()
        list_of_users = update.message.new_chat_members
        for user in list_of_users:
            if user.username == self.username:
                print("sending welcome message")
                self.send_welcome_message()
                break

    def generate_welcome_message_for_specific_user(self) -> str:
        print("welcome message generated")
        return self.config["welcomeMessage"].format(self.username)

    def generate_image_url(self) -> str:
        print("Image URL generated")
        return self.config["welcomeImageURL"]

    def send_welcome_message(self) -> None:
        print("sending welcome message")
        self.send_message(message=self.generate_welcome_message_for_specific_user())
        self.send_image(image_url=self.generate_image_url())
        print("welcome message sent")
        self.run_timer(callback_method=self.delete_message, timer=self.config["deleteCountDown"])
        self.run_timer(callback_method=self.delete_image, timer=self.config["deleteCountDown"])

    def run_timer(self, callback_method: Callable[[CallbackContext], None], timer=15) -> None:
        print("starting timer")
        self.context.job_queue.run_once(callback_method, context=self.chat_id, when=timer)

    def send_message(self, message: str) -> None:
        print("send_message called")
        self.context.bot.send_message(chat_id=self.chat_id, text=message)

    def send_image(self, image_url: str) -> None:
        print("send_image called")
        self.context.bot.send_photo(chat_id=self.chat_id, photo=image_url)

    def delete_message(self, context: CallbackContext) -> None:
        print("delete_message called")
        context.bot.delete_message(self.chat_id, self.message_id)

    def delete_image(self, context: CallbackContext) -> None:
        print("delete_image called")
        context.bot.delete_message(self.chat_id, self.photo_id)


class JsonReader:
    def __init__(self, file_path: str, ):
        self.file_path = file_path

    def read_and_return(self) -> dict:
        with open(self.file_path, "r") as config:
            return json.load(config)


App(token=JsonReader(file_path=appsettings).read_and_return()["token"], action=WelcomeMessage)
