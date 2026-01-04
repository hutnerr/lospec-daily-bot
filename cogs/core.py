import discord
from discord import app_commands
from discord.ext import commands

from utils.clogger import Clogger

class CoreCog(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.client: commands.Bot = client
        self.serverConfigs: dict = client.serverConfigs

    async def generateServerConfig(self, serverID: str):
        # will be used on an else statement where we fail to get a server config
        # because none exists
        pass

    # setchannel: command to set the channel for bot messages
    @app_commands.command(name='set_channel', description='Sets the output channel for bot messages')
    async def setChannel(self, interaction: discord.Interaction):
        # 1. get the current channel
        # 2. try and get the server config for this server
        # 3. if it doesn't exist, create it
        # 4. set the channel ID in the server config
        # 5. save the server config
        pass

    # toggle: enables / disables the bot messages for the set channel
    @app_commands.command(name='toggle', description='Enables or disables the bot messages for the set channel')
    async def toggle(self, interaction: discord.Interaction):
        # 1. try and get the server config for this server
        # 2. if it doesn't exist, create it
        # 3. toggle the enabled state
        # 4. save the server config
        pass

    # about: notes that this is not affiliated with lospec in any way. links to github, maybe kofi
    @app_commands.command(name='about', description='Displays information about the bot & it\'s purpose')
    async def about(self, interaction: discord.Interaction):
        pass

    # help: displays the simple help message for the bot
    @app_commands.command(name='help', description='Displays help information for the bot')
    async def help(self, interaction: discord.Interaction):
        pass

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