import asyncio
import discord
import os
import requests
import urllib3

from dotenv import load_dotenv
from enum import Enum
from message_utils import Emoji
from requests.exceptions import ConnectionError
from urllib3.exceptions import InsecureRequestWarning

load_dotenv()
ADMIN_USER_ID = os.getenv("ADMIN_USER_ID")
API_URL = os.getenv("SAT_SERVER_API_URL")
BEARER_TOKEN = os.getenv("SAT_SERVER_BEARER")
SERVER_ID = int(os.getenv("SERVER_ID", -1))
BOT_CHANNEL_ID = int(os.getenv("BOT_CHANNEL_ID", -1))
SAT_CHANNEL_ID = int(os.getenv("SAT_SERVER_NOTIFY_CHANNEL_ID", -1))

urllib3.disable_warnings(InsecureRequestWarning)


class ServerStatus(Enum):
    HEALTHY = "healthy"
    SLOW = "slow"
    OFFLINE = "offline"

def get_server_status() -> ServerStatus:
    body = {
        "function": "HealthCheck",
        "data": {"clientCustomData": ""}
    }
    headers = {
        "Authorization": f"Bearer {BEARER_TOKEN}",
        "content-type": "application/json;charset=utf-8",
    }
    try:
        response = requests.post(API_URL, json=body, headers=headers, verify=False)
    except ConnectionError as e:
        return ServerStatus.OFFLINE

    if response.status_code == 200:
        status = response.json()["data"]["health"]
        return ServerStatus[status.upper()]
    else:
        return ServerStatus.OFFLINE


async def monitor_server(client: discord.Client):
    guild = client.get_guild(SERVER_ID)
    channel = guild.get_channel(SAT_CHANNEL_ID)
    if channel is None:
        print("Invalid channel ID or bot does not have access to the channel.")
        return
    last_status = None

    status_messages = {
        (ServerStatus.OFFLINE, ServerStatus.HEALTHY): (Emoji.GREEN_CHECK.value, "Server is back online with status: {}"),
        (ServerStatus.OFFLINE, ServerStatus.SLOW): (Emoji.WARNING.value, "Server is back online with status: {}"),
        (ServerStatus.SLOW, ServerStatus.HEALTHY): (Emoji.GREEN_CHECK.value, "Server is back at healthy status"),
        (ServerStatus.SLOW, ServerStatus.OFFLINE): (Emoji.ERROR.value, "Server has gone offline"),
        (ServerStatus.HEALTHY, ServerStatus.SLOW): (Emoji.WARNING.value, "Server is unhealthy with status: {}"),
        (ServerStatus.HEALTHY, ServerStatus.OFFLINE): (Emoji.ERROR.value, "Server has gone offline"),
    }

    while True:
        status = get_server_status()
        str_status = status.value.title()

        if status != last_status:
            message_template = status_messages.get((last_status, status))
            if message_template:
                emoji, message = message_template
                await channel.send(f"<@{ADMIN_USER_ID}> {emoji} {message.format(str_status)}")

            last_status = status

        await asyncio.sleep(60)


def get_server_state() -> dict:
    body = {
        "function": "QueryServerState",
        "data": {"clientCustomData": ""}
    }
    headers = {
        "Authorization": f"Bearer {BEARER_TOKEN}",
        "content-type": "application/json;charset=utf-8",
    }
    try:
        response = requests.post(API_URL, json=body, headers=headers, verify=False)
    except ConnectionError as e:
        return {}

    if response.status_code == 200:
        state = response.json()["data"]["serverGameState"]
        return state
    else:
        return {}


async def monitor_server_state(client: discord.Client):
    guild = client.get_guild(SERVER_ID)
    bot_channel = guild.get_channel(BOT_CHANNEL_ID)
    sat_channel = guild.get_channel(SAT_CHANNEL_ID)
    if not bot_channel or not sat_channel:
        print(f"Invalid channel ID or bot does not have access to the channel.")
        return
    last_state = None

    while True:
        state = get_server_state()
        if state["isGamePaused"]:
            return
        state = {
            "players": state["numConnectedPlayers"],
            "tier": state["techTier"],
            "phase": state["gamePhase"].split("_")[-1].replace("'", ""),
            "schematic": state["activeSchematic"].split("_")[-1].replace("'", "")
        }
        if not state["phase"].isdigit():
            state["phase"] = "Unknown"


        messages = {
            "players": ("Active players changed to: {}", bot_channel),
            "tier": ("Congratulations! The factory has reached tier {}", sat_channel),
            "phase": ("Congratulations! The factory has reached phase {}", sat_channel),
            "schematic": ("Schematic {} has been initiated", sat_channel)
        }

        if state != last_state and last_state is not None:
            for state_key, value in state.items():
                if value == "Unknown" or value == "None" or value is None:
                    continue
                if value != last_state[state_key]:
                    message, channel = messages[state_key]
                    await channel.send(f"{message.format(value)}")
            last_state = state

        await asyncio.sleep(30)