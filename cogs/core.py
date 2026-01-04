import os
import discord
from discord import app_commands
from discord.ext import commands

from utils.clogger import Clogger
from utils.save_load import SaveLoad
from objects.server_config import ServerConfig

RAT_ICON_PATH = os.path.join("assets", "rat-pfp.png")

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

        embed = discord.Embed(
            title="Channel Set!",
            description=f"Bot messages will be sent to <#{channelID}>",
            color=discord.Color.green()
        )
        embed.set_footer(text="The bot is enabled by default. Use /toggle to enable/disable messages.")

        await interaction.response.send_message(embed=embed, ephemeral=True)

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

        embed = discord.Embed(
            title="Status Toggled!",
            description=f"Bot messages have been **{statusText}** for this server.",
            color=discord.Color.green() if not currentStatus else discord.Color.red()
        )
        embed.set_footer(text="Don't forget to set the channel with /set_channel.")

        await interaction.response.send_message(embed=embed, ephemeral=True)

    # about: notes that this is not affiliated with lospec in any way. links to github, maybe kofi
    @app_commands.command(name='about', description='Displays information about the bot & it\'s purpose')
    async def about(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="About",
            description="This bot posts the Lospec Daily Palette to a designated channel once a day at noon.\n\n"
                        "This bot is not affiliated with Lospec in any way. I created this bot as a personal project to help my friends and I improve at pixel art.\n\n"
                        "**Source Code**: [GitHub](https://github.com/hutnerr/lospec-daily-bot)\n",
            color=discord.Color.blue()
        )

        with open(RAT_ICON_PATH, "rb") as img_file:
            rat_icon = img_file.read()
        
        embed.set_thumbnail(url="attachment://rat-pfp.png")
        await interaction.response.send_message(embed=embed, files=[discord.File(RAT_ICON_PATH, filename="rat-pfp.png")])

    # help: displays the simple help message for the bot
    @app_commands.command(name='help', description='Displays help information for the bot')
    async def help(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="Bot Help",
            description="This bot posts the Lospec Daily Tag & Palette to a designated channel once a day at noon.\n\n"
                        "Commands:\n"
                        "`/set_channel`: Sets the output channel for bot messages.\n"
                        "`/toggle`: Enables or disables the bot messages for the set channel.\n"
                        "`/about`: Displays information about the bot & its purpose.\n"
                        "`/help`: Displays this help information.",
            color=discord.Color.blue()
        )

        with open(RAT_ICON_PATH, "rb") as img_file:
            rat_icon = img_file.read()
        
        embed.set_thumbnail(url="attachment://rat-pfp.png")

        await interaction.response.send_message(embed=embed, files=[discord.File(RAT_ICON_PATH, filename="rat-pfp.png")], ephemeral=True)

    @setChannel.error
    @toggle.error
    @about.error
    @help.error
    async def errorHandler(self, interaction: discord.Interaction, error: app_commands.CommandInvokeError):
        Clogger.error(f"Error in {interaction.command.name} command: {str(error)}")
        await interaction.response.send_message(f"An error occurred: {str(error)}", ephemeral=True)

async def setup(client: commands.Bot) -> None:
    await client.add_cog(CoreCog(client))