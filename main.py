import discord
from discord.ext import commands
from flask import Flask, request
import threading
import os

app = Flask(__name__)
intents = discord.Intents.default()
intents.members = True
bot = commands.Bot(command_prefix="!", intents=intents)

# Configuration: Replace with your actual Role IDs
ROLE_IDS = {
    "copper": 1234567890,
    "iron": 1234567891,
    "diamond": 1234567892,
    "netherite": 1234567893
}

@app.route('/update', methods=['POST'])
def update_armor():
    data = request.json
    username = data.get("username")
    material = data.get("armor")
    
    # We trigger a background task in the bot to update roles
    bot.loop.create_task(assign_role(username, material))
    return {"status": "success"}, 200

async def assign_role(username, material):
    guild = bot.guilds[0] # Assumes bot is in one server
    member = discord.utils.get(guild.members, name=username)
    
    if member and material in ROLE_IDS:
        role = guild.get_role(ROLE_IDS[material])
        if role not in member.roles:
            # Remove other armor roles first (optional)
            await member.remove_roles(*[guild.get_role(i) for i in ROLE_IDS.values() if guild.get_role(i) in member.roles])
            await member.add_roles(role)
            print(f"Assigned {material} role to {username}")

@app.route('/')
def home():
    return "Bot is Online"

def run_flask():
    app.run(host="0.0.0.0", port=10000)

if __name__ == "__main__":
    # Start Flask in a separate thread for UptimeRobot to ping
    threading.Thread(target=run_flask).start()
    bot.run("YOUR_DISCORD_BOT_TOKEN")
