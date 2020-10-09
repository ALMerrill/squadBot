const { Client, Permissions, User, WebhookClient } = require("discord.js");
import { Collection, Message } from "discord.js";
import fs from "fs";

import { token, webhook, prefix } from "./config.json";

const bot = new Client();
bot.commands = new Collection();
const commandFiles = fs
  .readdirSync(`${__dirname}/commands`)
  .filter((file) => file.endsWith(".js"));
for (const file of commandFiles) {
  const command = require(`${__dirname}/commands/${file}`);
  bot.commands.set(command.name, command);
}

bot.once("ready", () => {
  console.log("Bot is ready!");
});

bot.on("message", (message: Message) => {
  if (!message.content.startsWith(prefix) || message.author.bot) return;

  const args = message.content.slice(prefix.length).trim().split(/ +/) ?? [];
  const command = args.shift()?.toLowerCase();

  if (!bot.commands.has(command)) return;

  try {
    bot.commands.get(command).execute(message, args);
  } catch (error) {
    console.error(error);
    message.reply("there was an error trying to execute that command!");
  }
});

bot.login(token);
