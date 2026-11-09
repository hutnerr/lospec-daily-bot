import os

import discord
from discord import app_commands
from discord.ext import commands

from objects.server_config import ServerConfig
from pyutils import Clogger
from utils import schedule
from utils.data_getter import DailyData, DailyDataError, getDailyData
from utils.save_load import SaveLoad

RAT_ICON_PATH = os.path.join("assets", "rat-pfp.png")
IMG_URL = "https://cdn.lospec.com/thumbnails/palette-list/REPLACEME-social.png"

class CoreCog(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.client: commands.Bot = client
        self.serverConfigs: dict = client.serverConfigs
        Clogger.info("CoreCog initialized")

    async def generateServerConfig(self, serverID: str, channelID: int) -> None:
        config = ServerConfig(serverID=serverID, channelID=channelID, enabled=True)
        self.serverConfigs[serverID] = config
        SaveLoad.saveData(self.serverConfigs, serverID)
        Clogger.info(f"Generated new server config for server {serverID} with channel {channelID}")

    # the bot was removed from a server, its config is useless now
    @commands.Cog.listener()
    async def on_guild_remove(self, guild: discord.Guild) -> None:
        serverID = str(guild.id)
        if serverID in self.serverConfigs:
            Clogger.info(f"Removed from server {guild.name}({serverID}), deleting its config")
            SaveLoad.deleteData(self.serverConfigs, serverID)

    @staticmethod
    def buildDataEmbed(data: DailyData) -> discord.Embed:
        topic, palleteURL = data.tag, data.palleteURL
        embed = discord.Embed(
            title="Lospec Daily",
            url="https://lospec.com/dailies/",
            description=f"Topic: **{topic}**!\nPalette: [{palleteURL.split('/')[-1].title().replace('-', ' ').replace('_', ' ')}]({palleteURL})",
            color=discord.Color.blue(),
        )
        embed.set_thumbnail(url="https://avatars.githubusercontent.com/u/48259315?s=200&v=4")
        embed.set_image(url=IMG_URL.replace("REPLACEME", palleteURL.split("/")[-1]))
        return embed

    # setchannel: command to set the channel for bot messages
    @app_commands.command(name='setchannel', description='Sets the output channel for bot messages')
    async def setChannel(self, interaction: discord.Interaction):
        if interaction.guild is None:
            await interaction.response.send_message("This command can only be used in a server.", ephemeral=True)
            return
        
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
        embed.set_footer(text="The bot is enabled by default. Use /toggle to enable/disable messages or check the current config with /serverconfig.")
        if interaction.guild is not None:
            Clogger.action(f"Set channel for server {interaction.guild.name}({serverID}) to {channelID}")
        
        await interaction.response.send_message(embed=embed, ephemeral=True)

    # toggle: enables / disables the bot messages for the set channel
    @app_commands.command(name='toggle', description='Enables or disables the daily loop messages')
    async def toggle(self, interaction: discord.Interaction):
        if interaction.guild is None:
            await interaction.response.send_message("This command can only be used in a server.", ephemeral=True)
            return
        
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
        embed.set_footer(text="Don't forget to set the channel with /setchannel or check the current config with /serverconfig.")
        if interaction.guild is not None:
            Clogger.action(f"Toggle status for server {interaction.guild.name}({serverID}) to {not currentStatus}")
        
        await interaction.response.send_message(embed=embed, ephemeral=True)

    # about: notes that this is not affiliated with lospec in any way. links to github, maybe kofi
    @app_commands.command(name='about', description='Displays information about the bot & it\'s purpose')
    async def about(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="About",
            description=f"This bot posts the Lospec Daily Palette to a designated channel once a day at {schedule.POST_TIME_TEXT}.\n\n"
                        "This bot is not affiliated with Lospec in any way. I created this bot as a personal project to help my friends and I improve at pixel art.\n\n"
                        "**Source Code**: [GitHub](https://github.com/hutnerr/lospec-daily-bot)\n",
            color=discord.Color.blue()
        )
        embed.set_thumbnail(url="attachment://rat-pfp.png")
        if interaction.guild is not None:
            Clogger.action(f"About command executed for server {interaction.guild.name}({interaction.guild_id})")
        
        await interaction.response.send_message(embed=embed, files=[discord.File(RAT_ICON_PATH, filename="rat-pfp.png")])

    # help: displays the simple help message for the bot
    @app_commands.command(name='help', description='Displays help information for the bot')
    async def help(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="Bot Help",
            description=f"This bot posts the Lospec Daily Tag & Palette to a designated channel once a day at {schedule.POST_TIME_TEXT}.\n\n",
            color=discord.Color.blue()
        )
        embed.add_field(name="Setup", value="Run `/setchannel` in the channel you want the daily posted to. That's it, posts are enabled automatically.", inline=False)
        embed.add_field(name="Commands", value= 
                        "`/getdailydata`: Displays today's Lospec Daily.\n"
                        "`/toggle`: Enables or disables the daily loop messages.\n"
                        "`/setchannel`: Sets the output channel for bot messages.\n"
                        "`/serverconfig`: Displays the current server config for the bot.\n"
                        "`/about`: Displays information about the bot & its purpose.\n"
                        "`/help`: Displays this help information.", inline=False)
        embed.add_field(name="Error Reporting", value="If you encounter any issues or have suggestions, please report them on the [GitHub Issues Page](https://github.com/hutnerr/lospec-daily-bot/issues) or contact me directly [here](https://www.hunter-baker.com/pages/nav/contact.html).", inline=False)
        embed.set_thumbnail(url="attachment://rat-pfp.png")
        if interaction.guild is not None:
            Clogger.action(f"Help command executed for server {interaction.guild.name}({interaction.guild_id})")
            
        await interaction.response.send_message(embed=embed, files=[discord.File(RAT_ICON_PATH, filename="rat-pfp.png")], ephemeral=True)

    # getdailydata: command to manually get today's lospec daily data
    @app_commands.command(name="getdailydata", description="Displays today's Lospec Daily.")
    async def getDailyDataCommand(self, interaction: discord.Interaction):
        # scraping lospec can take longer than the 3 seconds discord gives us to respond
        await interaction.response.defer()

        try:
            data = await getDailyData()
        except DailyDataError:
            await interaction.followup.send("Couldn't get today's Lospec Daily right now, please try again later.", ephemeral=True)
            return

        embed = self.buildDataEmbed(data)

        # nudge servers that haven't set up daily posts yet
        config = self.serverConfigs.get(str(interaction.guild_id))
        if interaction.guild is not None and (config is None or not config.enabled):
            embed.set_footer(text="Want this posted here every day? Run /setchannel in the channel you want it in.")

        if interaction.guild is not None:
            Clogger.action(f"Get daily data command executed for server {interaction.guild.name}({interaction.guild_id})")
            
        await interaction.followup.send(embed=embed)

    @app_commands.command(name="serverconfig", description="Displays the current server configuration for the bot.")
    async def serverConfig(self, interaction: discord.Interaction):
        if interaction.guild is None:
            await interaction.response.send_message("This command can only be used in a server.", ephemeral=True)
            return
        
        serverID = str(interaction.guild_id)
        if serverID not in self.serverConfigs:
            await self.generateServerConfig(serverID, interaction.channel_id)

        config = self.serverConfigs[serverID]
        statusText = "Enabled" if config.enabled else "Disabled"
        channelText = f"<#{config.channelID}>" if config.channelID is not None else "Not Set"

        embed = discord.Embed(
            title="Server Configuration",
            color=discord.Color.blue()
        )
        embed.add_field(name="Status", value=statusText, inline=False)
        embed.add_field(name="Channel", value=channelText, inline=False)
        embed.set_thumbnail(url=interaction.guild.icon.url if interaction.guild.icon else None)
        if interaction.guild is not None:
            Clogger.action(f"Server config command executed for server {interaction.guild.name}({interaction.guild_id})")
            
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @setChannel.error
    @toggle.error
    @about.error
    @help.error
    @getDailyDataCommand.error
    @serverConfig.error
    async def errorHandler(self, interaction: discord.Interaction, error: app_commands.CommandInvokeError):
        errEmbed = discord.Embed(
            title="Error",
            description=f"An error occurred while processing the command: {str(error)}",
            color=discord.Color.red()
        )
        errEmbed.add_field(name="Reporting", value="Please report this on the [GitHub Issues Page](https://github.com/hutnerr/lospec-daily-bot/issues) or contact me directly [here](https://www.hunter-baker.com/pages/nav/contact.html).", inline=False)
        commandName = interaction.command.name if interaction.command else "unknown"
        Clogger.error(f"Error in {commandName} command: {str(error)}")

        # the command may have already responded or deferred, and the interaction may have expired
        try:
            if interaction.response.is_done():
                await interaction.followup.send(embed=errEmbed, ephemeral=True)
            else:
                await interaction.response.send_message(embed=errEmbed, ephemeral=True)
        except discord.HTTPException as e:
            Clogger.warn(f"Could not send error message for {commandName} command: {e}")

async def setup(client: commands.Bot) -> None:
    await client.add_cog(CoreCog(client))