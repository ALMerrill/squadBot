# Valoo Bot

A Discord bot for controlling ARK servers via AMP

## Testing locally

1. Create a bot [on the Discord developer portal](https://discord.com/developers/applications)
2. Create a webhook on your own discord server [by following this tutorial](https://docs.gitlab.com/ee/user/project/integrations/discord_notifications.html). Actually seems like this may not be needed now
3. Create a `.env` in the project root and fill in the values listed below. The first token is on the bot page accessed from the side of the Discord Developer Portal, and the webook information is found on the page when you navigate to the webhook url
4. Invite your dev bot to your server by [following this url](https://discord.com/oauth2/authorize?client_id=761568927188123669&scope=bot&permissions=1141124160), replacing the client id with your bot's client id (found on it's general information page), and the permissions with the Permission Integer created in the Developer Portal as you select permissions for your bot,
5. Once these steps are setup, simply run `python -m venv venv && source activate venv/bin/activate && pip install -r requirements.txt` and `python bot.py` from the terminal in the root directory of the repo,
6. Test the bot is connected by running `/ping` for this bot. It should then respond with "Pong" to show you that it is online and connected.

## Environment variables

Required:
- `DISCORD_TOKEN`
- `SERVER_ID` (Discord guild ID)
- `ARK_CONTROL_CHANNEL_ID` (channel allowed to run ARK commands)
- `AMP_BASE_URL` (e.g. `https://amp.droo.app`)
- `AMP_USERNAME`
- `AMP_PASSWORD`
- `ARK_INSTANCE_NAME` (AMP instance name, e.g. `ark01`)
- `ARK_INSTANCE_ID` (AMP instance GUID)

Optional:
- `ARK_SAVE_DELAY_SECONDS` (default `15`)
- `ARK_CONNECT_URL` (optional connect URL shown in `/status-ark`, e.g. `steam://connect/amp.droo.app:27015`)
- `AMP_DEBUG` (set `true` to include raw AMP responses in command output)

## AMP permissions

The AMP user must have:
- `Console - Send`
- `Manage Instance`

## Commands

- `/start-ark`
- `/stop-ark`
- `/reboot-ark`
- `/update-ark`
- `/status-ark`

## Docker

This repo uses a Python bot container. Replace `.env` with your values, then:

```bash
docker compose up --build
```


## License
This project is open source and available under the [MIT](https://github.com/ALMerrill/squadBot/blob/master/LICENSE)
