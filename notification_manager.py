import os
from telegram import Bot

BOT_TOKEN = os.environ.get("TELEGRAM_TOKEN")
GROUP_CHATID = os.environ.get("CHAT_ID")


class Notifications():

    def __init__(self):
        self.my_cv_bot = Bot(token=BOT_TOKEN)
        self.send_status = False

    def send_message(self, action, tendency_months, profit):
        self.my_cv_bot.sendMessage(chat_id=GROUP_CHATID,
                                   text=f"Notificacion de Estrategia"
                                        f"\nEstrategia: Superacion de la Media"
                                        f"\nAccion: {action}\nMeses en Tendencia: {tendency_months}\n"
                                        f"\nRentabilidad desde cambio tendencia: {profit}")
        self.send_status = True

    def reset_notification(self):
        self.send_status = False