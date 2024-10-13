# bot.py
import os

import discord
import textwrap

from discord import app_commands
from dotenv import load_dotenv
from satisfactory_server_utils import (
    get_server_status,
    get_server_state,
    monitor_server,
    monitor_server_state,
    ServerStatus
)

load_dotenv()
SERVER_ID = os.getenv("SERVER_ID")
TOKEN = os.getenv("DISCORD_TOKEN")
PREFIX = os.getenv("BOT_PREFIX")

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)
guild = discord.Object(id=SERVER_ID)

@client.event
async def on_ready():
    client.loop.create_task(monitor_server(client))
    client.loop.create_task(monitor_server_state(client))
    await tree.sync(guild=guild)
    print(f"{client.user} has connected to Discord!")


@tree.command(name="ping", description="Ping the bot", guild=guild)
async def status(interaction: discord.Interaction):
    await interaction.response.send_message("pong")


@tree.command(name="status", description="Get current running status of the Satisfactory server", guild=guild)
async def status(interaction: discord.Interaction):
    status = get_server_status().value.title()
    await interaction.response.send_message(f"Server's current status: {status}")


@tree.command(name="state", description="Get info on the state of the server", guild=guild)
async def status(interaction: discord.Interaction):
    state = get_server_state()
    tier = state["techTier"]
    phase = state["gamePhase"].split("_")[-1]
    if not phase.isdigit():
        phase = "Unknown"
    players = state["numConnectedPlayers"]
    schematic = state["activeSchematic"]
    paused = state["isGamePaused"]
    message = textwrap.dedent(f"""
    **Active players**: `{players}`
    **Game running**: `{not paused}`
    **Current tier**: `{tier}`
    **Current phase**: `{phase}`
    **Current schematic**: `{schematic}`
    """).strip()
    await interaction.response.send_message(message)


@client.event
async def on_message(message):
    if message.author == client.user:
        return
    content = message.content
    if not content.startswith(PREFIX):
        return
    content = content.replace(f"{PREFIX} ", "").strip().lower()
    

client.run(TOKEN)