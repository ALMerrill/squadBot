# bot.py
import os

import asyncio
import discord

from discord import app_commands
from dotenv import load_dotenv
from amp_server_utils import (
    AmpServerState,
    get_status as get_ark_status,
    graceful_stop_with_save,
    start_server as start_ark_server,
)

load_dotenv()
SERVER_ID = int(os.getenv("SERVER_ID", "-1"))
TOKEN = os.getenv("DISCORD_TOKEN")
ARK_CONTROL_CHANNEL_ID = int(os.getenv("ARK_CONTROL_CHANNEL_ID", "-1"))

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)
guild = discord.Object(id=SERVER_ID)

@client.event
async def on_ready():
    await tree.sync(guild=guild)
    print(f"{client.user} has connected to Discord!")


@tree.command(name="ping", description="Ping the bot", guild=guild)
async def ping(interaction: discord.Interaction):
    await interaction.response.send_message("pong")


def _is_ark_channel(interaction: discord.Interaction) -> bool:
    return interaction.channel_id == ARK_CONTROL_CHANNEL_ID


@tree.command(name="start-ark", description="Start the ARK server", guild=guild)
async def start_ark(interaction: discord.Interaction):
    if not _is_ark_channel(interaction):
        await interaction.response.send_message(
            "This command can only be used in the ARK control channel.",
            ephemeral=True,
        )
        return

    await interaction.response.defer(thinking=True)
    try:
        status = await asyncio.to_thread(get_ark_status)
        if status in (AmpServerState.RUNNING, AmpServerState.STARTING):
            await interaction.followup.send(f"ARK server is already {status.name.lower()}.")
            return
        await asyncio.to_thread(start_ark_server)
        await interaction.followup.send("ARK server start requested.")
    except Exception as exc:
        await interaction.followup.send(f"Failed to start ARK server: {exc}")


@tree.command(name="stop-ark", description="Stop the ARK server (save then stop)", guild=guild)
async def stop_ark(interaction: discord.Interaction):
    if not _is_ark_channel(interaction):
        await interaction.response.send_message(
            "This command can only be used in the ARK control channel.",
            ephemeral=True,
        )
        return

    await interaction.response.defer(thinking=True)
    try:
        status = await asyncio.to_thread(get_ark_status)
        if status in (AmpServerState.STOPPED, AmpServerState.STOPPING):
            await interaction.followup.send(f"ARK server is already {status.name.lower()}.")
            return
        await asyncio.to_thread(graceful_stop_with_save)
        await interaction.followup.send("ARK server save issued and stop requested.")
    except Exception as exc:
        await interaction.followup.send(f"Failed to stop ARK server: {exc}")


client.run(TOKEN)
