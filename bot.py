import time
import json
import logging
import traceback
from logging.handlers import RotatingFileHandler

import discord
from discord.ext import commands

from pyutils import Clogger, CloggerConfig
from pyutils import get_env
from utils.save_load import SaveLoad

class Client(commands.Bot):
    def __init__(self):
        intents = discord.Intents().all()
        super().__init__(
            command_prefix = commands.when_mentioned_or("/"),
            intents = intents,
            activity = discord.Activity(type = discord.ActivityType.playing, name = "/help for commands"),
        )
        
        self.cogslist = [
            "cogs.core",
            "cogs.looper",
        ]
        
        # loads all server data on startup. returns a dict with serverID string as key
        # and value of ServerConfig object
        self.serverConfigs = SaveLoad.loadData()
        
        Clogger.debugEnabled = True
        Clogger.useTimestamps = True

    # runs once on startup. on_ready fires again on every reconnect, so syncing
    # slash commands here avoids re-syncing each time
    async def setup_hook(self) -> None:
        for ext in self.cogslist:
            await self.load_extension(ext) # loads our cogs    
        synced = await self.tree.sync()
        Clogger.info(f"Slash CMDs Synced {len(synced)}")
    
    async def on_ready(self):
        Clogger.info(f"Logged in as {self.user.name}")

# discord.py's own logs (gateway disconnects, unhandled errors in events/tasks, etc.)
# go to the console and a rotating discord.log, so crashes leave a trace
def setupLogging() -> None:
    discord.utils.setup_logging(level=logging.INFO)
    discord.utils.setup_logging(
        handler=RotatingFileHandler("discord.log", maxBytes=5 * 1024 * 1024, backupCount=3, encoding="utf-8"),
        level=logging.INFO,
    )

if __name__ == "__main__":
    setupLogging()
    Clogger.config = CloggerConfig(
        simplify_timestamps=False,
        show_source_file=False,
        write_to_file=True,
        log_file_path="bot.log",
    )

    client = Client()
    client.remove_command("help") # remove default help so I can add custom one. 

    key = get_env("LOSPEC_BOT_KEY", None)

    if not key:
        Clogger.error(
            "No Discord key found. Please set the LOSPEC_BOT_KEY environment variable.",
            exc=KeyError
        )

    try:
        client.run(key, log_handler=None) # logging is already set up above
    except Exception:
        Clogger.error(f"Bot crashed:\n{traceback.format_exc()}")
        raise