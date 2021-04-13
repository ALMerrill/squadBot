import { Collection, Message, TextChannel } from "discord.js";
import { prefix } from "../../config.json";
import Utils from "../../util/utils";

module.exports = {
  name: "random-clip",
  usage: `${prefix}random-clip`,
  description: "Get a DM with a random Twitch clip of tennisshoesfan",
  execute(message: Message, args: string[]) {
    const channel = message.client.channels.cache.get("762863369400221696")
    if (channel) {
        const messages = (channel as TextChannel).messages
        messages.fetch({ limit: 100 }).then((messages: Collection<string, Message>) => {
          messages.forEach((message: Message) => {
            if (message.content.includes('https://clips.twitch.tv/')) {
              console.log(message.content)
            }
          })
          const twitch_clips = messages
                                .filter(message => message.content.includes('https://clips.twitch.tv/'))
                                .map(message => message.content)
          const response: string = twitch_clips[Math.floor(Math.random() * twitch_clips.length) as number]
          Utils.dm_response(message, response)
        })
    }
  },
};
