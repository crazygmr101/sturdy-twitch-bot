import logging
import os

import dotenv

from twitchbot.bot import TwitchBot
import services

dotenv.load_dotenv()

logging.basicConfig(level=logging.INFO)

bot = TwitchBot(os.getenv("OAUTH"),
                os.getenv("USER"),
                os.getenv("CHANNEL"),
                "-")

bot.add_state_callback("connect", services.cnt1)
bot.add_state_callback("connect", services.cnt2)

bot.run()
