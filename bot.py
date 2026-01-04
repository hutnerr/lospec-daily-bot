import time
import json

import discord
from colorama import Back, Fore, Style
from discord.ext import commands

from utils.clogger import Clogger
from utils.save_load import SaveLoad

class Client(commands.Bot):
    def __init__(self):
        intents = discord.Intents().all()
        super().__init__(command_prefix = commands.when_mentioned_or("/"), intents = intents)
        
        self.cogslist = [
            "cogs.core",
            "cogs.looper",
        ]
        
        # loads all server data on startup. returns a dict with serverID string as key
        # and value of ServerConfig object
        self.serverConfigs = SaveLoad.loadData()
        
        Clogger.debugEnabled = True
        Clogger.useTimestamps = True

    async def setup_hook(self) -> None:
        for ext in self.cogslist:
            await self.load_extension(ext) # loads our cogs    
    
    # prints info to console, gives us custom status, and syncs slash commands
    async def on_ready(self):
        Clogger.info(f"Logged in as {Fore.YELLOW}{client.user.name}{Style.RESET_ALL}")
        synced = await client.tree.sync()
        Clogger.info(f"Slash CMDs Synced {Fore.YELLOW}{str(len(synced))}{Style.RESET_ALL}")
        await client.change_presence(activity = discord.Activity(type = discord.ActivityType.playing, name = "/help for commands"))

client = Client()
client.remove_command("help") # remove default help so I can add custom one. 

# key = "testkey"
key = "key"

with open("data/key.json", "r") as file:
    key = json.load(file)[key]

client.run(key)