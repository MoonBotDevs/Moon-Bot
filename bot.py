import discord
import os
import sqlite3
import logging
from dotenv import load_dotenv
from discord.ext import commands
from discord.ext.commands import when_mentioned_or
from os.path import isfile
from sqlite3 import connect
from apscheduler.triggers.cron import CronTrigger
from glob import glob
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import db

logger = logging.getLogger(__name__)
console_logger = logging.getLogger("console")
load_dotenv()
token = os.environ.get('TOKEN')
hg = os.environ.get('MOONBOTGUILD')
COGS = [path.split(os.sep)[-1][:-3] for path in glob("./cogs/*.py")]





db.build()

def get_prefix(bot, message):
    prefix = db.field("SELECT Prefix FROM Guilds WHERE GuildID = ?", message.guild.id)
    return when_mentioned_or(prefix)(bot, message)

class Bot(commands.Bot):
    def __init__(self):
        self.token = token
        self.moonbotguild = hg
        self.scheduler = AsyncIOScheduler()
        
        super(Bot, self).__init__(command_prefix=get_prefix, intents=discord.Intents.all())
        db.autosave(self.scheduler)

    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.NoPrivateMessage):
            await ctx.author.send('This command cannot be used in private messages.')
        elif isinstance(error, commands.DisabledCommand):
            await ctx.author.send('Sorry. This command is disabled and cannot be used.')
        elif isinstance(error, commands.CommandInvokeError):
            print(f'In {ctx.command.qualified_name}:', file=sys.stderr)
            traceback.print_tb(error.original.__traceback__)
            print(
                f'{error.original.__class__.__name__}: {error.original}', file=sys.stderr)
        
    async def on_ready(self):
        print('Logged in as:')
        print('Username: ' + self.user.name)
        print('ID: ' + str(self.user.id))
        print('------')
        for cog in COGS:
            self.load_extension(f"cogs.{cog}")
        activity = discord.Game(name="Minecraft", type=3)
        await self.change_presence(status=discord.Status.idle, activity=activity)

    
    def run(self):
        super().run(self.token, reconnect=True)

if __name__ == "__main__":
    moonbot = Bot()
    moonbot.run()
