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
    console.log(__dirname + '/..')
    console.log(fs.readdirSync(`${__dirname}/../`))
    const commandRoot = `${__dirname}/../`
    const commandDirs = fs.readdirSync(commandRoot)
    for (const dir of commandDirs) {
      const commandFiles = fs
        .readdirSync(`${commandRoot}/${dir}/`)
        .filter((file) => file.endsWith(".js"));
      for (const file of commandFiles) {
        const command = require(`${commandRoot}/${dir}/${file}`);
        if (
          (command.permission &&
            message.member?.hasPermission(command.permission)) ||
          !command.permission
        ) {
          help += `**${command.usage}:** ${command.description}\n`;
        }
      }
    }
    Utils.dm_response(message, help);
  },
};
