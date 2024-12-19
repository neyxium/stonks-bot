import discord
from discord.ext import commands
from API import getAPI_KEY, getPass
from slashCommands import register_slash_commands

API_KEY = getAPI_KEY()

intents = discord.Intents.default()
bot = commands.Bot(command_prefix=".", intents=intents)

@bot.event
async def on_ready():
    try:
        await bot.tree.sync()
        print("Global slash commands synced.")
        print(f"Logged on as {bot.user}!")
    except Exception as e:
        print(f"Failed to sync commands: {e}")

register_slash_commands(bot)

bot.run(API_KEY)
