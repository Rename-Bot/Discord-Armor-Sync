import discord
from discord.ext import commands
from flask import Flask, request, jsonify
import threading
import random
import string
import json

app = Flask(__name__)
bot = commands.Bot(command_prefix="!", intents=discord.Intents.all())

# Temporary storage for codes: { "code": "MinecraftName" }
pending_links = {}

# Persistent storage: { "MinecraftName": "DiscordID" }
try:
    with open("links.json", "r") as f:
        linked_accounts = json.load(f)
except:
    linked_accounts = {}

def save_links():
    with open("links.json", "w") as f:
        json.dump(linked_accounts, f)

# --- FLASK ENDPOINTS ---

@app.route('/request_link', methods=['POST'])
def request_link():
    data = request.json
    username = data.get("username")
    # Generate a random 6-digit code
    code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
    pending_links[code] = username
    return jsonify({"code": code}), 200

@app.route('/update', methods=['POST'])
def update_armor():
    data = request.json
    username = data.get("username")
    material = data.get("armor")
    
    # Check if the player is linked
    if username in linked_accounts:
        discord_id = linked_accounts[username]
        bot.loop.create_task(assign_role(discord_id, material))
    return {"status": "processed"}, 200

# --- DISCORD COMMANDS ---

@bot.command()
async def link(ctx, code: str):
    code = code.upper()
    if code in pending_links:
        mc_name = pending_links.pop(code)
        linked_accounts[mc_name] = ctx.author.id
        save_links()
        await ctx.send(f"✅ Successfully linked **{mc_name}** to your Discord account!")
    else:
        await ctx.send("❌ Invalid or expired code. Run `/scriptevent sync:link` in Minecraft again.")

async def assign_role(user_id, material):
    guild = bot.guilds[0] 
    member = await guild.fetch_member(user_id)
    # (Role logic from previous response goes here...)

def run_flask():
    app.run(host="0.0.0.0", port=10000)

if __name__ == "__main__":
    threading.Thread(target=run_flask).start()
    bot.run(os.environ.get('DISCORD_TOKEN'))
