from datetime import datetime
import json
from typing import Callable
from telegram import Update
from telegram.ext import Updater, MessageHandler, Filters, CallbackContext
appsettings = "appsettings.json"
new_users = []


class App:
    def __init__(self, token: str, action):
        self.updater = Updater(token)
        self.callback = action

    def start(self):
        print(datetime.now(), "Starting app")
        self.updater.dispatcher.add_handler(MessageHandler(filters=Filters.update, callback=self.callback))
        self.updater.start_polling()
        self.updater.idle()
        print(datetime.now(), "finishing app")


class WelcomeMessage:
    def __init__(self, update: Update, context: CallbackContext):
        global new_users
        self.update = update
        self.context = context
        self.chat_id = update.message.chat.id
        self.message_id = update.message.message_id + 1
        self.photo_id = update.message.message_id + 2
        self.user_id = update.message.from_user.id
        self.username = update.message.from_user.username
        self.config = JsonReader(file_path=appsettings).read_and_return()
        list_of_users = update.message.new_chat_members
        for user in list_of_users:
            if user.id == self.user_id:
                print(datetime.now(), f"User joined: {user.username}")
                if user.id in new_users:
                    print(datetime.now(), "Welcome message has already been sent to user before")
                else:
                    print(datetime.now(), "Sending welcome message")
                    new_users.append(self.user_id)
                    self.send_welcome_message()
                print(datetime.now(), "IDs of new users:", new_users)
                break

    def generate_welcome_message_for_specific_user(self) -> str:
        print(datetime.now(), "welcome message generated")
        welcome_message = self.config["welcomeMessage"]
        return str("" if welcome_message is None or type(welcome_message) is not str else welcome_message).format(self.username)

    def generate_image_url(self) -> str:
        print(datetime.now(), "Image URL generated")
        welcome_image = self.config["welcomeImageURL"]
        return str("" if welcome_image is None or type(welcome_image) is not str else welcome_image)

    def send_welcome_message(self) -> None:
        try:
            countdown = 0 if self.config["deleteCountDown"] is None else self.config["deleteCountDown"]
            message = self.generate_welcome_message_for_specific_user()
            image = self.generate_image_url()
            print(datetime.now(), "sending welcome message:", f"message is '{message}'", f"image url is '{image}'")
            if message and message.strip():
                self.send_message(message=message)
                self.run_timer(callback_method=self.delete_message, timer=countdown)
            if image and image.strip():
                self.send_image(image_url=image)
                self.run_timer(callback_method=self.delete_image, timer=countdown + 1)
            print(datetime.now(), "welcome message sent")
        except Exception as ex:
            print(f"Exception was raised during send_welcome_message operation: {ex}")

    def run_timer(self, callback_method: Callable[[CallbackContext], None], timer: float = 15) -> None:
        print(datetime.now(), "starting timer")
        try:
            self.context.job_queue.run_once(callback_method, context=self.chat_id, when=timer)
        except Exception as ex:
            print(datetime.now(), "Exception by run_timer was raised:", ex)

    def send_message(self, message: str) -> None:
        print(datetime.now(), "send_message called")
        try:
            self.context.bot.send_message(chat_id=self.chat_id, text=message)
        except Exception as ex:
            print(datetime.now(), f"Exception was raised while sending a message: {ex}")

    def send_image(self, image_url: str) -> None:
        print(datetime.now(), "send_image called")
        try:
            self.context.bot.send_photo(chat_id=self.chat_id, photo=image_url)
        except Exception as ex:
            print(datetime.now(), f"Exception was raised while sending an image: {ex}")

    def delete_message(self, context: CallbackContext) -> None:
        print(datetime.now(), "delete_message called")
        context.bot.delete_message(self.chat_id, self.message_id)

    def delete_image(self, context: CallbackContext) -> None:
        print(datetime.now(), "delete_image called")
        context.bot.delete_message(self.chat_id, self.photo_id)
        new_users.pop(new_users.index(self.user_id))


class JsonReader:
    def __init__(self, file_path: str, ):
        self.file_path = file_path

    def read_and_return(self) -> dict:
        with open(self.file_path, "r") as config:
            return json.load(config)


try:
    print(datetime.now(), "Execution started")
    init_token = str(JsonReader(file_path=appsettings).read_and_return()["token"])
    if (init_token is None) or not (init_token and init_token.strip()):
        print(datetime.now(), "Please set the correct token!")
    else:
        App(token=init_token, action=WelcomeMessage).start()
except Exception as e:
    print(datetime.now(), f"Following error was raised: {e}")
finally:
    print(datetime.now(), "Execution stopped")
