import { Client, GatewayIntentBits, ActivityType, } from "discord.js";
export const client = new Client({ intents: [GatewayIntentBits.Guilds, GatewayIntentBits.GuildMembers, GatewayIntentBits.GuildMessages, GatewayIntentBits.MessageContent] });
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

client.on('messageCreate', async (message) => {
    if (message.content.replace(' ', '').includes("<@726933780677394532>antifraud")) {
        let array = message.content.replace('<@726933780677394532>', '').replace('antifraud ', '').split(", ")
        let param = array.length > 1 ? array[0] + "&season=" + array[1] : array[0]
        let json = await (await fetch(`https://www.mk8dx-lounge.com/api/player/details?name=${param}&quaxly=true`)).json()
        let totalScores = 0
        let totalPartnerScores = 0
        let divider = 0
        let partnerDivider = 0
        json.mmrChanges.filter((tab) => { return tab.tier !== "SQ" }).filter((tab) => { return tab.score !== undefined }).forEach((tab, index) => {
            totalScores += tab.score
            divider += 1
            if (tab.partnerScores.length > 0) {
                tab.partnerScores.forEach((array) => {
                    totalPartnerScores += array
                    partnerDivider += 1
                })
            }
            if (index == json.mmrChanges.filter((tab) => { return tab.tier !== "SQ" }).filter((tab) => { return tab.score !== undefined }).length - 1) {
                let embed =
                {
                    title: "S" + json.season + " | " + json.name + "'s no SQ stats",
                    color: 15514131,
                    fields: [
                        {
                            name: "Events",
                            value: `${json.eventsPlayed} => __${index}__`
                        },
                        {
                            name: "Avg. Score",
                            value: `${json.averageScore.toFixed(1)} => __${(totalScores / divider).toFixed(1)}__`
                        },
                        {
                            name: "Partner Avg.",
                            value: `${json.partnerAverage.toFixed(1)} => __${(totalPartnerScores / partnerDivider).toFixed(1)}__`
                        }
                    ]
                }
                message.reply({ embeds: [embed] })
            }
        })
    }
})

client.login(config.token);
