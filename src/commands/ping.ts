import { Message } from "discord.js";
import { prefix } from "../config.json";

module.exports = {
  name: "ping",
  usage: `${prefix}ping`,
  description: "Ping the bot for a quick test",
  execute(message: Message, args: string[]) {
    message.channel.send("Pong.");
  },
};
