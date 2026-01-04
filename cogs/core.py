import discord
from discord import app_commands
from discord.ext import commands

from utils.clogger import Clogger
from utils.save_load import SaveLoad
from objects.server_config import ServerConfig

# TODO: Change the messages to useful embeds. Fill out the rest of the info.

class CoreCog(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.client: commands.Bot = client
        self.serverConfigs: dict = client.serverConfigs

    async def generateServerConfig(self, serverID: str, channelID: int) -> None:
        config = ServerConfig(serverID=serverID, channelID=channelID, enabled=True)
        self.serverConfigs[serverID] = config
        SaveLoad.saveData(self.serverConfigs, serverID)

    # setchannel: command to set the channel for bot messages
    @app_commands.command(name='set_channel', description='Sets the output channel for bot messages')
    async def setChannel(self, interaction: discord.Interaction):
        serverID = str(interaction.guild_id)
        channelID = interaction.channel_id

        if serverID not in self.serverConfigs:
            await self.generateServerConfig(serverID, channelID)

        self.serverConfigs[serverID].channelID = channelID
        SaveLoad.saveData(self.serverConfigs, serverID)

        await interaction.response.send_message(f"Set bot messages channel to <#{channelID}>", ephemeral=True)

    # toggle: enables / disables the bot messages for the set channel
    @app_commands.command(name='toggle', description='Enables or disables the bot messages for the set channel')
    async def toggle(self, interaction: discord.Interaction):
        serverID = str(interaction.guild_id)

        if serverID not in self.serverConfigs:
            await self.generateServerConfig(serverID, interaction.channel_id)

        currentStatus = self.serverConfigs[serverID].enabled
        self.serverConfigs[serverID].enabled = not currentStatus
        SaveLoad.saveData(self.serverConfigs, serverID)

        statusText = "enabled" if not currentStatus else "disabled"
        await interaction.response.send_message(f"Bot messages have been {statusText} for this server.", ephemeral=True)

    # about: notes that this is not affiliated with lospec in any way. links to github, maybe kofi
    @app_commands.command(name='about', description='Displays information about the bot & it\'s purpose')
    async def about(self, interaction: discord.Interaction):
        await interaction.response.send_message("testing !!!")

    # help: displays the simple help message for the bot
    @app_commands.command(name='help', description='Displays help information for the bot')
    async def help(self, interaction: discord.Interaction):
        await interaction.response.send_message("testing !!!@!@!@!@!@!!")

    @setChannel.error
    @toggle.error
    @about.error
    @help.error
    async def errorHandler(self, interaction: discord.Interaction, error: app_commands.CommandInvokeError):
        # TODO: improve this error handling
        Clogger.error(f"Error in {interaction.command.name} command: {str(error)}")
        await interaction.response.send_message(f"An error occurred: {str(error)}", ephemeral=True)

async def setup(client: commands.Bot) -> None:
    await client.add_cog(CoreCog(client))