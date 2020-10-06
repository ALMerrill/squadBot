# Squad Bot

A Discord bot for you and your squad

## Testing locally

1. Create a bot [on the Discord developer portal](https://discord.com/developers/applications),
2. Create a webhook on your own discord server [by following this tutorial](https://docs.gitlab.com/ee/user/project/integrations/discord_notifications.html),
3. Copy the `src/config.example.json` from the project to `src/config.json` and fill in the gaps with the information from the bot and the webhook. The first token is on the bot page accessed from the side of the Discord Developer Portal, and the webook information is found on the page when you navigate to the webhook url,
4. Invite your dev bot to your server by [following this url](https://discord.com/oauth2/authorize?client_id=761568927188123669&scope=bot&permissions=1141124160), replacing the client id with your bot's client id (found on it's general information page), and the permissions with the Permission Integer created in the Developer Portal as you select permissions for your bot,
5. Once these steps are setup, simply run `yarn install` and `yarn run dev` from the terminal in the root directory of the repo,
6. Test the bot is connected by running `<your-prefix>ping`. It should then respond with "Pong" to show you that it is online and connected.
