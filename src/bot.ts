const { Client } = require("discord.js");
import { Collection, Message } from "discord.js";
import fs from "fs";

import { token, prefix } from "./config.json";
import Utils from "./util/utils"

const bot = new Client();
bot.commands = new Collection();
const commandCategories = fs.readdirSync(`${__dirname}/commands`);
let commandFiles: string[] = [];
commandCategories.forEach((cat) => {
  fs.readdirSync(`${__dirname}/commands/${cat}`).forEach((file) => {
    commandFiles.push(`${cat}/${file}`);
  });
});
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
    Utils.dm_response(message, "There was an error trying to execute that command!")

  }
});

bot.login(token);
