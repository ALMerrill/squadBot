import { Message } from "discord.js";
import { prefix } from "../../config.json";
import fs from "fs";
import Utils from "../../util/utils";

module.exports = {
  name: "help",
  usage: `${prefix}help`,
  description: "Shows all of the bot commands available to the user",
  execute(message: Message, args: string[]) {
    let help = "Here are the available commands!\n";
    const commandFiles = fs
      .readdirSync(`${__dirname}`)
      .filter((file) => file.endsWith(".js"));
    for (const file of commandFiles) {
      const command = require(`${__dirname}/${file}`);
      if (
        (command.permission &&
          message.member?.hasPermission(command.permission)) ||
        !command.permission
      ) {
        help += `**${command.usage}:** ${command.description}\n`;
      }
    }
    Utils.dm_response(message, help);
  },
};
