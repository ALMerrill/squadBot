import { Message } from "discord.js";
import { prefix } from "../../config.json";
import Utils from "../../util/utils";

module.exports = {
  name: "server-info",
  usage: `${prefix}server-info`,
  description: "Get basic server info",
  execute(message: Message, args: string[]) {
    const guild = message.guild
    if (guild) {
        const response = `Server name: ${guild.name}\
        \nTotal members: ${guild.memberCount}\
        \nDate created: ${guild.createdAt}`;
        Utils.dm_response(message, response);
    }
  },
};
