import { Client, GatewayIntentBits, ActivityType, } from "discord.js";
export const client = new Client({ intents: [GatewayIntentBits.Guilds, GatewayIntentBits.GuildMembers] });
import config from "./config.js";
import fs from "fs";
import { bdd, user_list } from "./utils.js";

fs.writeFileSync("./bdd_backup.json", JSON.stringify(bdd, null, 4));
fs.writeFileSync("./user_list_backup.json", JSON.stringify(user_list, null, 4));

client.on("ready", () => {
    console.log(`Logged in as ${client.user.tag}!`);
    client.user.setActivity(`${client.guilds.cache.size} servers`, {
        type: ActivityType.Watching,
    });
    setInterval(() => {
        client.user.setActivity(`${client.guilds.cache.size} servers`, {
            type: ActivityType.Watching,
        });
    }, 60000);
});

import { CommandHandler } from "./commands.js";

client.on("interactionCreate", CommandHandler);

client.on('error', async (error) => {
    try {
        const owner = await client.users.fetch("169497208406802432");
        owner.send(`An error occurred: \`\`\`${error}\`\`\``);
    } catch (error) {
        console.error(error);
    }
});

client.login(config.token);
