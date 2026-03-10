# bot.py
import os

import asyncio
import discord

from discord import app_commands
from dotenv import load_dotenv
from amp_server_utils import (
    AmpServerState,
    get_status as get_ark_status,
    get_status_raw as get_ark_status_raw,
    get_status_info as get_ark_status_info,
    extract_instance_status as extract_ark_instance_status,
    graceful_stop_with_save,
    _action_ok,
    _action_reason,
    AMP_DEBUG,
    restart_server as restart_ark_server,
    start_server as start_ark_server,
    update_server as update_ark_server,
    ARK_CONNECT_URL,
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


async def _send_safe(interaction: discord.Interaction, content: str) -> None:
    if len(content) > 1900:
        content = content[:1900] + "… (truncated)"
    await interaction.followup.send(content)


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
        result = await asyncio.to_thread(start_ark_server)
        if not _action_ok(result):
            reason = _action_reason(result)
            await _send_safe(interaction, f"ARK server start failed. {reason}".strip())
            return
        msg = "ARK server start requested."
        if AMP_DEBUG:
            msg += f" Raw: {result}"
        await _send_safe(interaction, msg)
    except Exception as exc:
        msg = f"Failed to start ARK server: {exc}"
        await _send_safe(interaction, msg)


@tree.command(name="reboot-ark", description="Restart the ARK server", guild=guild)
async def reboot_ark(interaction: discord.Interaction):
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
            await interaction.followup.send("ARK server is stopped; use /start-ark.")
            return
        result = await asyncio.to_thread(restart_ark_server)
        if not _action_ok(result):
            reason = _action_reason(result)
            await _send_safe(interaction, f"ARK server restart failed. {reason}".strip())
            return
        msg = "ARK server restart requested."
        if AMP_DEBUG:
            msg += f" Raw: {result}"
        await _send_safe(interaction, msg)
    except Exception as exc:
        msg = f"Failed to restart ARK server: {exc}"
        await _send_safe(interaction, msg)


@tree.command(name="update-ark", description="Update the ARK server via AMP", guild=guild)
async def update_ark(interaction: discord.Interaction):
    if not _is_ark_channel(interaction):
        await interaction.response.send_message(
            "This command can only be used in the ARK control channel.",
            ephemeral=True,
        )
        return

    await interaction.response.defer(thinking=True)
    try:
        result = await asyncio.to_thread(update_ark_server)
        if not _action_ok(result):
            reason = _action_reason(result)
            await _send_safe(interaction, f"ARK server update failed. {reason}".strip())
            return
        msg = "ARK server update requested."
        if AMP_DEBUG:
            msg += f" Raw: {result}"
        await _send_safe(interaction, msg)
    except Exception as exc:
        msg = f"Failed to update ARK server: {exc}"
        await _send_safe(interaction, msg)


@tree.command(name="status-ark", description="Get ARK server status", guild=guild)
async def status_ark(interaction: discord.Interaction):
    if not _is_ark_channel(interaction):
        await interaction.response.send_message(
            "This command can only be used in the ARK control channel.",
            ephemeral=True,
        )
        return

    await interaction.response.defer(thinking=True)
    try:
        status, status_text = await asyncio.to_thread(get_ark_status_info)
        message = f"ARK server status: {status.name.lower()}."
        if status_text:
            message += f" ({status_text})"
        # AMP API for this instance doesn't expose player counts or rich state.
        if ARK_CONNECT_URL:
            message += f" Connect: {ARK_CONNECT_URL}"
        if AMP_DEBUG:
            raw = await asyncio.to_thread(get_ark_status_raw)
            message += f" Raw: {raw}"
        await _send_safe(interaction, message)
    except Exception as exc:
        msg = f"Failed to get ARK server status: {exc}"
        await _send_safe(interaction, msg)


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
        result = await asyncio.to_thread(graceful_stop_with_save)
        save_ok = _action_ok(result.get("save")) if isinstance(result, dict) else True
        stop_ok = _action_ok(result.get("stop")) if isinstance(result, dict) else True
        save_reason = _action_reason(result.get("save")) if isinstance(result, dict) else ""
        stop_reason = _action_reason(result.get("stop")) if isinstance(result, dict) else ""
        if not stop_ok:
            reason = stop_reason or save_reason
            await _send_safe(interaction, f"ARK server stop failed. {reason}".strip())
            return
        msg = "ARK server stop requested."
        if not save_ok and save_reason:
            msg += f" Save failed: {save_reason}"
        if AMP_DEBUG:
            msg += f" Raw: {result}"
        await _send_safe(interaction, msg)
    except Exception as exc:
        msg = f"Failed to stop ARK server: {exc}"
        await _send_safe(interaction, msg)


client.run(TOKEN)
