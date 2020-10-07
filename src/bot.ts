const { Client, Permissions, User, WebhookClient } = require("discord.js");
import { Collection, Message } from "discord.js";
import fs from "fs";

// var { token, webhook, prefix } = require('./config.json');
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

// // -------------------- Commands/Events handling --------------------

// bot.on("message", async (message: typeof Message) => {
//   if (!message.content.startsWith(prefix) || message.author.bot) return;
//   const args = message.content.slice(prefix.length).trim().split(/ +/);
//   const command = args.shift().toLowerCase();
//   if (command === "deletemessages") {
//     if (message.member.hasPermission(Permissions.FLAGS.MANAGE_MESSAGES)) {
//       try {
//         const messages = await message.channel.fetchMessages();
//         await message.channel.bulkDelete(messages).catch(() => {
//           message.author.send("Error deleting messages");
//         });
//       } catch (error) {
//         console.log(error);
//       }
//     } else {
//       message.author.send("You do not have permission to run this command");
//     }
//   } else if (command === "server-info") {
//     message.channel.send(`Server name: ${message.guild.name}\
//                           \nTotal members: ${message.guild.memberCount}\
//                           \nDate created: ${message.guild.createdAt}`);
//   } else if (command === "avatar") {
//     if (!message.mentions.users.size) {
//       return message.channel.send(
//         `Your avatar: <${message.author.displayAvatarURL({
//           format: "png",
//           dynamic: true,
//         })}>`
//       );
//     }
//     const avatarList = message.mentions.users.map((user: typeof User) => {
//       return `${user.username}'s avatar: <${user.displayAvatarURL({
//         format: "png",
//         dynamic: true,
//       })}>`;
//     });
//     message.delete(1000);
//     message.author.send(avatarList);
//   }
// });

// // const cmds = ['aliases', 'commands'];
// // const handlers = ['command', 'event'];

// // cmds.forEach((x) => (bot[x] = new Collection()));
// // handlers.forEach((x) => require(`./handlers/${x}`)(bot, logsWebhook));

// // -------------------- Login --------------------

// bot.login(token);
