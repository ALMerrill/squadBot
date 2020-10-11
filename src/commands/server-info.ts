import { Message } from "discord.js";
import { prefix } from "../config.json";

module.exports = {
  name: "server-info",
  usage: `${prefix}server-info`,
  description: "Get basic server info",
  execute(message: Message, args: string[]) {
    message.channel.send(`Server name: ${message.guild.name}\
                          \nTotal members: ${message.guild.memberCount}\
                          \nDate created: ${message.guild.createdAt}`);
  },
};
