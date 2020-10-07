const { Client, Permissions, Message, WebhookClient } = require("discord.js");

// var { token, webhook, prefix } = require("./config.json");
import { token, webhook, prefix } from "./config.json";

const bot = new Client();

// -------------------- Webhooks --------------------

const logsWebhook = new WebhookClient(webhook.id, webhook.token);

// -------------------- Commands/Events handling --------------------

bot.once("ready", () => {
  console.log("Bot is ready!");
});

bot.on("message", async (message: typeof Message) => {
  console.log(message.content);
  if (message.content.startsWith(`${prefix}ping`)) {
    message.channel.send("🚀 pong");
    // message.reply('pong!');
  }

  //TODO: make file of translations for all unique strings, like response messages.
  //      see if there are permission enums
  else if (message.content.startsWith(`${prefix}deletemessages`)) {
    console.log(Permissions.FLAGS.MANAGE_MESSAGES);
    if (message.member.hasPermission(Permissions.FLAGS.MANAGE_MESSAGES)) {
      try {
        const messages = await message.channel.fetchMessages();
        await message.channel.bulkDelete(messages);
      } catch (error) {
        console.log(error);
      }
    } else {
      message.author.send("You do not have permission to run this command");
    }
  }
});

// const cmds = ["aliases", "commands"];
// const handlers = ["command", "event"];

// cmds.forEach((x) => (bot[x] = new Collection()));
// handlers.forEach((x) => require(`./handlers/${x}`)(bot, logsWebhook));

// -------------------- Login --------------------

bot.login(token);
