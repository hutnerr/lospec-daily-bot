import time

from discord.ext import commands, tasks
from utils.save_load import SaveLoad
from utils.clogger import Clogger
from utils.data_getter import getDailyData
from objects.server_config import ServerConfig

# TODO: Change the messages to useful embeds. Fill out the rest of the info.

class Looper(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.client = client 
        self.serverConfigs = client.serverConfigs
            
        self.mainloop.start()
        self.saveServerConfigs.start()
    
    # save all server data once a day
    @tasks.loop(hours=24)
    async def saveServerConfigs(self) -> None:
        SaveLoad.saveAllData(self.serverConfigs)

    @tasks.loop(minutes=1)
    async def mainloop(self) -> None:
        # dow = int(time.strftime('%w'))  # 0 = sunday, 6 = saturday
        hour = int(time.strftime('%H'))
        minute = int(time.strftime('%M'))
        
        minute = 0
        hour = 12

        Clogger.debug(f"Main loop check at {hour}:{minute} UTC")

        if minute != 0 and hour != 12:
            # only run at the top of the hour
            # only run at noon
            Clogger.debug("Not the scheduled time for daily posts, skipping...")
            return
            
        Clogger.info("Running main loop for daily posts")

        data = await getDailyData()
        if data is None:
            Clogger.error("Failed to get daily data")
            return

        topic, palleteURL = data
        activeServers = [
            sc for sc in self.serverConfigs.values() if sc.enabled and sc.channelID is not None
        ]

        for serverConfig in activeServers:
            channel = self.client.get_channel(serverConfig.channelID)
            if channel is None:
                Clogger.warn(f"Could not find channel ID {serverConfig.channelID} for server {serverConfig.serverID}")
                continue

            try:
                await channel.send(f"Topic: {topic}\nPalette URL: {palleteURL}")
                Clogger.info(f"Sent daily post to server {serverConfig.serverID} in channel {serverConfig.channelID}")
            except Exception as e:
                Clogger.warn(f"Failed to send message to server {serverConfig.serverID} in channel {serverConfig.channelID}: {str(e)}")

        Clogger.info("Main loop daily posts complete")

    @saveServerConfigs.before_loop
    @mainloop.before_loop
    async def before_loop(self) -> None:
        await self.client.wait_until_ready()

async def setup(client: commands.Bot) -> None: 
    await client.add_cog(Looper(client))