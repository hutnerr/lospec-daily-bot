import os
import time

from discord.ext import commands, tasks

from utils.clogger import Clogger
from utils.save_load import SaveLoad

IMGPATH = os.path.join("assets", "lospec.png")

# 10:00 AM EST daily
DESIRED_HOUR = 10
DESIRED_MINUTE = 0

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
        
        # minute = DESIRED_MINUTE
        # hour = DESIRED_HOUR
        # Clogger.debug(f"Main loop check at {hour}:{minute} EST")
        
        if minute != DESIRED_MINUTE or hour != DESIRED_HOUR:
            # Clogger.debug("Not the scheduled time for daily posts, skipping...")
            return
            
        Clogger.info("Running main loop for daily posts")

        coreCog = self.client.get_cog("CoreCog")
        if coreCog is None:
            Clogger.error("CoreCog not found, cannot build daily data embed")
            return
        
        embed = await coreCog.buildDataEmbed()
        if embed is None:
            Clogger.error("Failed to build daily data embed, skipping daily posts")
            return
        
        embed.set_footer(text="Use /toggle to enable/disable daily posts.")
        activeServers = [sc for sc in self.serverConfigs.values() if sc.enabled and sc.channelID is not None]
        for serverConfig in activeServers:
            channel = self.client.get_channel(serverConfig.channelID)
            if channel is None:
                Clogger.warn(f"Could not find channel ID {serverConfig.channelID} for server {serverConfig.serverID}")
                continue
            try:
                await channel.send(embed=embed)
                # Clogger.debug(f"Sent daily post to server {serverConfig.serverID} in channel {serverConfig.channelID}")
            except Exception as e:
                Clogger.warn(f"Failed to send message to server {serverConfig.serverID} in channel {serverConfig.channelID}: {str(e)}")

        Clogger.info("Main loop daily posts complete")

    @saveServerConfigs.before_loop
    @mainloop.before_loop
    async def before_loop(self) -> None:
        await self.client.wait_until_ready()

async def setup(client: commands.Bot) -> None: 
    await client.add_cog(Looper(client))