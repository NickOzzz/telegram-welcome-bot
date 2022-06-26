from datetime import datetime
import json
from typing import Callable
from telegram import Update
from telegram.ext import Updater, MessageHandler, Filters, CallbackContext
appsettings = "appsettings.json"


class App:
    def __init__(self, token: str, action):
        self.updater = Updater(token)
        self.callback = action

    def start(self):
        print(datetime.now(), "Starting app")
        self.updater.dispatcher.add_handler(MessageHandler(filters=Filters.all, callback=self.callback))
        self.updater.start_polling()
        self.updater.idle()
        print(datetime.now(), "finishing app")


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
                print(datetime.now(), "sending welcome message")
                self.send_welcome_message()
                break

    def generate_welcome_message_for_specific_user(self) -> str:
        print(datetime.now(), "welcome message generated")
        return str(self.config["welcomeMessage"]).format(self.username)

    def generate_image_url(self) -> str:
        print(datetime.now(), "Image URL generated")
        return str(self.config["welcomeImageURL"])

    def send_welcome_message(self) -> None:
        print(datetime.now(), "sending welcome message")
        self.send_message(message=self.generate_welcome_message_for_specific_user())
        self.send_image(image_url=self.generate_image_url())
        print(datetime.now(), "welcome message sent")
        countdown = float(self.config["deleteCountDown"])
        self.run_timer(callback_method=self.delete_message, timer=countdown)
        self.run_timer(callback_method=self.delete_image, timer=countdown)

    def run_timer(self, callback_method: Callable[[CallbackContext], None], timer: float = 15) -> None:
        print(datetime.now(), "starting timer")
        self.context.job_queue.run_once(callback_method, context=self.chat_id, when=timer)

    def send_message(self, message: str) -> None:
        print(datetime.now(), "send_message called")
        self.context.bot.send_message(chat_id=self.chat_id, text=message)

    def send_image(self, image_url: str) -> None:
        print(datetime.now(), "send_image called")
        self.context.bot.send_photo(chat_id=self.chat_id, photo=image_url)

    def delete_message(self, context: CallbackContext) -> None:
        print(datetime.now(), "delete_message called")
        context.bot.delete_message(self.chat_id, self.message_id)

    def delete_image(self, context: CallbackContext) -> None:
        print(datetime.now(), "delete_image called")
        context.bot.delete_message(self.chat_id, self.photo_id)


class JsonReader:
    def __init__(self, file_path: str, ):
        self.file_path = file_path

    def read_and_return(self) -> dict:
        with open(self.file_path, "r") as config:
            return json.load(config)


try:
    print(datetime.now(), "Execution started")
    App(token=str(JsonReader(file_path=appsettings).read_and_return()["token"]), action=WelcomeMessage).start()
except Exception as e:
    print(datetime.now(), f"Following error was raised: {e}")
finally:
    print(datetime.now(), "Execution stopped")
