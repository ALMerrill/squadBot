import { Message} from "discord.js";
import { prefix } from "../../config.json";
import Utils from "../../util/utils";

module.exports = {
  name: "random-clip",
  usage: `${prefix}random-clip`,
  description: "Get a DM with a random Twitch clip of tennisshoesfan",
  execute(message: Message, args: string[]) {
    //const channel = message.client.channels.get("762863369400221696");
    //console.log(channel.messages)
    //channel.messages.fetch({ limit: 100  }).then((messages: Message[]) => {
    //  console.log(`Received ${messages.length} messages`);
    //  messages.forEach((message: Message) => {
    //    console.log(message.content)
    //  })
    //})
    //Utils.dm_response(message, response);
  },
};
