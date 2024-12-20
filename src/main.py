import discord
from discord.ext import commands
from API import getAPI_KEY, getPass
from slashCommands import register_slash_commands
from flask import Flask
import os
import threading

API_KEY = getAPI_KEY()

# Discord bot setup
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

# Flask app for Heroku port binding
app = Flask(__name__)

@app.route("/")
def home():
    return "Bot is running!"

def run_flask():
    port = int(os.getenv("PORT", 5000))  # Use the $PORT provided by Heroku
    app.run(host="0.0.0.0", port=port)

# Start Flask in a separate thread
if __name__ == "__main__":
    threading.Thread(target=run_flask).start()  # Start Flask server
    bot.run(API_KEY)  # Start Discord bot
