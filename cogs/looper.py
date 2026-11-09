import datetime
import traceback

import discord
from discord.ext import commands, tasks

from pyutils import Clogger
from utils import schedule
from utils.data_getter import DailyData, DailyDataError, getDailyData
from utils.save_load import SaveLoad

class Looper(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.client = client
        self.serverConfigs = client.serverConfigs

        # persisted: lastPostedDate, lastTag, lastPallete, skippedDate
        self.state: dict = SaveLoad.loadState() or self.initialState()

        # in memory only: retry bookkeeping for the current day
        self.nextAttempt: datetime.datetime | None = None
        self.failureDate: str | None = None

        self.mainloop.start()
        self.saveServerConfigs.start()
        Clogger.info("Looper Cog initialized and loops started")

    def cog_unload(self) -> None:
        self.mainloop.cancel()
        self.saveServerConfigs.cancel()

    @staticmethod
    def initialState() -> dict:
        # no state file yet (first run with this version). if today's post time has
        # already passed, assume the previous version already posted so we don't double post
        now = schedule.now()
        state = {}
        if now >= schedule.postTimeOn(now):
            state["lastPostedDate"] = now.date().isoformat()
        SaveLoad.saveState(state)
        Clogger.info(f"No bot state found, created a new one: {state}")
        return state

    # save all server data once a day
    # just in case
    @tasks.loop(hours=24)
    async def saveServerConfigs(self) -> None:
        SaveLoad.saveAllData(self.serverConfigs)

    # checks every minute whether today's daily still needs to go out. checking
    # "is it past the post time and not posted yet" instead of "is it exactly 8:00"
    # means restarts, slow iterations, and failed fetches all get caught up on
    @tasks.loop(minutes=1)
    async def mainloop(self) -> None:
        # never let an exception escape, an unhandled one would stop the loop for good
        try:
            await self.checkDailyPost()
        except Exception:
            Clogger.error(f"Unexpected error in main loop:\n{traceback.format_exc()}")

    async def checkDailyPost(self) -> None:
        now = schedule.now()
        today = now.date().isoformat()

        if today in (self.state.get("lastPostedDate"), self.state.get("skippedDate")):
            return
        if now < schedule.postTimeOn(now):
            return
        if self.nextAttempt is not None and now < self.nextAttempt:
            return

        Clogger.info("Running main loop for daily posts")

        try:
            data = await getDailyData()
            self.checkNotStale(data, now)
        except DailyDataError as e:
            await self.handleFailure(str(e), now, today)
            return

        coreCog = self.client.get_cog("CoreCog")
        if coreCog is None:
            Clogger.error("CoreCog not found, cannot build daily data embed")
            return

        embed = coreCog.buildDataEmbed(data)
        embed.set_footer(text="Use /toggle to enable/disable daily posts.")
        await self.sendDailyPosts(embed)

        self.state["lastPostedDate"] = today
        self.state["lastTag"] = data.tag
        self.state["lastPallete"] = data.palleteURL
        SaveLoad.saveState(self.state)
        self.nextAttempt = None

        if self.failureDate == today:
            await self.alertOwner(f"✅ Recovered: today's Lospec Daily ({data.tag}) was posted.")
        Clogger.info("Main loop daily posts complete")

    def checkNotStale(self, data: DailyData, now: datetime.datetime) -> None:
        # lospec occasionally hasn't rolled over to the new daily by our post time.
        # posting anyway would send yesterday's daily again
        if data.pageDate is not None and data.pageDate != now.date():
            raise DailyDataError(f"Lospec is still showing the daily for {data.pageDate}, not today ({now.date()})")
        if (data.tag, data.palleteURL) == (self.state.get("lastTag"), self.state.get("lastPallete")):
            raise DailyDataError(f"Lospec is still showing the same daily as last time ({data.tag})")

    async def handleFailure(self, reason: str, now: datetime.datetime, today: str) -> None:
        firstFailureToday = self.failureDate != today
        self.failureDate = today

        giveUpTime = schedule.postTimeOn(now) + schedule.GIVE_UP_AFTER
        if now + schedule.RETRY_INTERVAL > giveUpTime:
            Clogger.error(f"Giving up on today's daily post: {reason}")
            self.state["skippedDate"] = today
            SaveLoad.saveState(self.state)
            self.nextAttempt = None
            await self.alertOwner(f"❌ Gave up on today's Lospec Daily post, nothing was sent.\nLast error: {reason}")
            return

        self.nextAttempt = now + schedule.RETRY_INTERVAL
        Clogger.warn(f"Daily post failed, retrying at {self.nextAttempt:%H:%M}: {reason}")
        if firstFailureToday:
            await self.alertOwner(
                f"⚠️ Today's Lospec Daily post failed, retrying every "
                f"{int(schedule.RETRY_INTERVAL.total_seconds() // 60)} minutes.\nError: {reason}"
            )

    async def sendDailyPosts(self, embed: discord.Embed) -> None:
        activeServers = [sc for sc in self.serverConfigs.values() if sc.enabled and sc.channelID is not None]
        for serverConfig in activeServers:
            serverID = serverConfig.serverID
            guild = self.client.get_guild(int(serverID))

            # the bot was kicked or the server was deleted while we were offline
            if guild is None:
                Clogger.warn(f"Bot is no longer in server {serverID}, removing its config")
                SaveLoad.deleteData(self.serverConfigs, serverID)
                continue

            # discord outage, the server will come back. don't touch its config
            if guild.unavailable:
                Clogger.warn(f"Server {serverID} is temporarily unavailable, skipping it today")
                continue

            channel = guild.get_channel_or_thread(int(serverConfig.channelID))
            if channel is None:
                Clogger.warn(f"Channel {serverConfig.channelID} no longer exists in server {guild.name} ({serverID}), disabling daily posts")
                serverConfig.enabled = False
                SaveLoad.saveData(self.serverConfigs, serverID)
                continue

            try:
                await channel.send(embed=embed)
                Clogger.debug(f"Sent daily post to server {guild.name} ({serverID}) in channel {serverConfig.channelID}")
            except discord.Forbidden:
                Clogger.warn(f"Missing permissions to post in channel {serverConfig.channelID} in server {guild.name} ({serverID})")
            except Exception as e:
                Clogger.warn(f"Failed to send message to server {serverID} in channel {serverConfig.channelID}: {str(e)}")

    async def alertOwner(self, message: str) -> None:
        try:
            app = await self.client.application_info()
            owner = app.team.owner if app.team and app.team.owner else app.owner
            await owner.send(message)
        except Exception as e:
            Clogger.warn(f"Could not DM the bot owner: {e}")

    @saveServerConfigs.before_loop
    @mainloop.before_loop
    async def before_loop(self) -> None:
        await self.client.wait_until_ready()

async def setup(client: commands.Bot) -> None:
    await client.add_cog(Looper(client))
