import logging
import os

import dotenv

from twitchbot.bot import TwitchBot
import services

dotenv.load_dotenv()

logging.basicConfig(level=logging.INFO)

bot = TwitchBot(os.getenv("OAUTH"),
                os.getenv("CHANNEL"),
                os.getenv("USERNAME"),
                "-")

bot.add_command_callback("add", services.add)

bot.run()
