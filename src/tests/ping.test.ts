import { timeStamp } from "console";
import { hasUncaughtExceptionCaptureCallback } from "process";

import { Client } from "discord.js";

const bot = new Client();

describe("basic bot functionality", () => {
  test("bot starting", () => {
    expect(bot).toBeDefined();
  });
});
