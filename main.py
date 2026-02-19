import discord
from discord import app_commands
from discord.ext import commands
from flask import Flask, request, jsonify
import threading
import random
import string
import json

app = Flask(__name__)

class MyBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.members = True
        super().__init__(command_prefix="!", intents=intents)

    async def setup_hook(self):
        # Syncs slash commands with Discord
        await self.tree.sync()

bot = MyBot()
pending_links = {} # { "CODE": "MC_NAME" }
linked_accounts = {} # Load/Save logic as shown previously

@bot.tree.command(name="link", description="Link your Minecraft account")
@app_commands.describe(code="The 6-digit code shown in Minecraft")
async def link(interaction: discord.Interaction, code: str):
    code = code.upper()
    if code in pending_links:
        mc_name = pending_links.pop(code)
        linked_accounts[mc_name] = interaction.user.id
        # In a real app, call save_links() here
        await interaction.response.send_message(f"✅ Linked to **{mc_name}**!", ephemeral=True)
    else:
        await interaction.response.send_message("❌ Invalid code.", ephemeral=True)

# --- Flask Endpoints ---

@app.route('/request_link', methods=['POST'])
def request_link():
    username = request.json.get("username")
    code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
    pending_links[code] = username
    return jsonify({"code": code}), 200

@app.route('/update', methods=['POST'])
def update_armor():
    data = request.json
    username = data.get("username")
    material = data.get("armor")
    
    if username in linked_accounts:
        user_id = linked_accounts[username]
        bot.loop.create_task(assign_role(user_id, material))
    return {"status": "ok"}, 200

async def assign_role(user_id, material):
    # (Insert your role assignment logic here)
    pass

@app.route('/')
def health_check():
    return "Bot Alive", 200

def run_flask():
    app.run(host="0.0.0.0", port=10000)

if __name__ == "__main__":
    threading.Thread(target=run_flask, daemon=True).start()
    bot.run(os.environ.get('DISCORD_TOKEN'))
