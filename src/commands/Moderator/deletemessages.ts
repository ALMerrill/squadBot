import { Message, PermissionOverwrites } from "discord.js";
const { Permissions } = require("discord.js");
import { prefix } from "../../config.json";

const permissions = [Permissions.FLAGS.MANAGE_MESSAGES];

module.exports = {
  name: "deletemessages",
  usage: `${prefix}deletemessages`,
  permission: permissions,
  description:
    "If user has permission, delete all channel messages (mostly for use during development to clear messages from bot",
  async execute(message: Message, args: string[]) {
    if (message.member.hasPermission(permissions)) {
      try {
        const messages = await message.channel.fetchMessages();
        await message.channel.bulkDelete(messages).catch(() => {
          message.author.send("Error deleting messages");
        });
      } catch (error) {
        console.log(error);
      }
    } else {
      message.author.send("You do not have permission to run this command");
    }
  },
};
