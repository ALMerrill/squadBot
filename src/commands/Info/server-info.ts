import { Message } from "discord.js";
import { prefix } from "../../config.json";
import Utils from "../../util/utils";

module.exports = {
  name: "server-info",
  usage: `${prefix}server-info`,
  description: "Get basic server info",
  execute(message: Message, args: string[]) {
    const response = `Server name: ${message.guild.name}\
    \nTotal members: ${message.guild.memberCount}\
    \nDate created: ${message.guild.createdAt}`;
    Utils.dm_response(message, response);
  },
};
