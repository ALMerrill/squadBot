import { Message } from "discord.js";

export default class Utils {
  static dm_response(message: Message, response: string) {
    message.author.send(response);
    message.delete(1000);
  }
}
