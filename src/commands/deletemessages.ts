import { Message } from "discord.js";
const { Permissions } = require("discord.js");

module.exports = {
  name: "deletemessages",
  description:
    "If user has permission, delete all channel messages (mostly for use during development to clear messages from bot",
  async execute(message: Message, args: string[]) {
    if (message.member.hasPermission(Permissions.FLAGS.MANAGE_MESSAGES)) {
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
