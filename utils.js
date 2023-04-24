import { EmbedBuilder } from "discord.js";
import { client } from "./Quaxly.js";
import fs from "fs";

export const track_list = fs.readFileSync("./tracklist.txt", "utf-8").replace(/^(?=\n)$|^\s|\s$|\n\n+/gm, "").split(/\r?\n/);
export var bdd = JSON.parse(fs.readFileSync("./bdd.json", "utf8"));
export var user_list = JSON.parse(fs.readFileSync("./user_list.json", "utf8"));
export let playerList = []


export async function updatePlayerList() {
    let playerObjectList = await (await fetch("https://www.mk8dx-lounge.com/api/player/list")).json()
    playerList = []
    playerObjectList.players.forEach(el => {
        playerList.push(el.name)
    })
}

export function is_track_init(user_id, speed, item, track) {
    if (bdd[user_id] != undefined && bdd[user_id][speed] != undefined && bdd[user_id][speed][item] != undefined && bdd[user_id][speed][item][track] != undefined) {
        return true;
    }
    return false;
}

export function user_and_server_id_check(user_id, guild_id) {
    if (user_list[guild_id] == undefined) {
        user_list[guild_id] = [user_id];
    }
    else if (!user_list[guild_id].includes(user_id)) {
        user_list[guild_id].push(user_id);
    }
    save_user_list();
}

export function player_update(user_id) {
    if (bdd[user_id] != undefined) return
    bdd[user_id] = {
        150: {
            Shroom: {},
            NI: {},
        },
        200: {
            Shroom: {},
            NI: {},
        },
    }
}

export function get_track_formated(track) {
    if (track.toLowerCase() == "bcm64") return "bCMo";
    if (track.toLowerCase() == "bcmw") return "bCMa";
    for (let i = 0; i < track_list.length; i++) {
        if (track_list[i].toLowerCase() == track.toLowerCase()) {
            return track_list[i];
        }
    }
    return 0
}

export function save_bdd() {
    fs.writeFile("./bdd.json", JSON.stringify(bdd, null, 4), (err) => {
        if (err) {
            console.error(err);
            return 0;
        }
        return 1;
    });
}

export function save_user_list() {
    fs.writeFile("./user_list.json", JSON.stringify(user_list, null, 4), (err) => {
        if (err) {
            console.error(err);
            return 0;
        }
        return 1;
    });
}

export async function error_embed(interaction, error) {
    const embed = new EmbedBuilder()
        .setTitle("Error")
        .setDescription(error)
        .setColor(0xff0000)
    if (interaction.deferred) {
        await interaction.editReply({ embeds: [embed], components: [] });
    } else if (!interaction.replied) {
        await interaction.reply({ embeds: [embed], ephemeral: true });
    } else {
        await interaction.followUp({ embeds: [embed], ephemeral: true });
    }
}

export async function teamEvents(searchType, ids, embed, interaction, embedArray, jsonArray, eventsArray) {
    for (let i = 0; i < ids.length; i++) {
        let nameJson
        let json
        let season = interaction.options.get("season") && interaction.options.get("season").value != undefined ? "&season=" + interaction.options.get("season").value : ""
        try {
            nameJson = await (await fetch("https://www.mk8dx-lounge.com/api/player?" + searchType + "=" + ids[i] + "&quaxly=true")).json()
            json = await (await fetch("https://www.mk8dx-lounge.com/api/player/details?name=" + nameJson.name + season + "&quaxly=true")).json()
        } catch (e) {
            console.log(interaction, e);
        }
        if (json.eventsPlayed != undefined && json.eventsPlayed > 0) {
            eventsArray.push(json.eventsPlayed)
            jsonArray.push(json)
            if ((jsonArray.length - 1) % 21 === 0 && jsonArray.length > 1) {
                embedArray.push({
                    color: 15514131,
                    fields: [
                    ]
                })
            }
            else if ((jsonArray.length - 1) % 21 === 0) {
                embedArray.push(embed)
            }
            embedArray[Math.floor((jsonArray.length - 1) / 21)].fields.push({ name: json.name, value: `<@${nameJson.discordId}> ([${json.eventsPlayed}](https://www.mk8dx-lounge.com/PlayerDetails/${json.playerId}))`, inline: true })
            embedArray[Math.floor((jsonArray.length - 1) / 21)].fields.sort(function (a, b) { return parseInt(b.value.split('> ([')[1].split(']')[0]) - parseInt(a.value.split('> ([')[1].split(']')[0]); })
            await interaction.editReply({ embeds: embedArray })

        }
        if (i === ids.length - 1 && embedArray[embedArray.length - 1] != undefined) {
            embedArray.forEach(array => {
                array.fields.sort(function (a, b) { return parseInt(b.value.split('> ([')[1].split(']')[0]) - parseInt(a.value.split('> ([')[1].split(']')[0]); })
            })
            embedArray[embedArray.length - 1].fields.push({ name: '\u200B', value: '\u200B' })
            let sum = parseInt(eventsArray.reduce((a, b) => a + b, 0))
            embedArray[embedArray.length - 1].fields.push({ name: "Total", value: `__${sum}__`, inline: true })
            embedArray[embedArray.length - 1].fields.push({ name: "Average/player", value: `__${parseInt(sum / eventsArray.length)}__`, inline: true })
            await interaction.editReply({ embeds: embedArray })
        } else if (i === ids.length - 1) {
            await interaction.editReply({
                embeds: [
                    {
                        title: "Error",
                        description: "No player found or wrong season",
                        color: 0xff0000,
                    }
                ]
            })
        }
    }
}

export async function averagePeakMmr(searchType, ids, embed, interaction, embedArray, jsonArray, mmrArray) {
    for (let i = 0; i < ids.length; i++) {
        let nameJson
        let json
        let season = interaction.options.get("season") && interaction.options.get("season").value != undefined ? "&season=" + interaction.options.get("season").value : ""
        try {
            nameJson = await (await fetch("https://www.mk8dx-lounge.com/api/player?" + searchType + "=" + ids[i] + "&quaxly=true")).json()
            json = await (await fetch("https://www.mk8dx-lounge.com/api/player/details?name=" + nameJson.name + season + "&quaxly=true")).json()
        } catch (e) {
            console.log(interaction);
            const owner = await client.users.fetch("169497208406802432");
            owner.send(`An error occurred: \`\`\`${e}\`\`\`\n\n\`\`\`${interaction}\`\`\`\n\n\`\`\`${searchType}\`\`\`\n\n\`\`\`${ids[i]}\`\`\``).catch(() => {
                console.log("Error while sending error to owner\n\n" + e + "\n\n" + interaction + "\n\n" + searchType + "\n\n" + ids[i])
            });
            continue;
        }
        if (json.name != undefined && json.mmr) {
            let mmrValue = json.maxMmr != undefined ? json.maxMmr : json.mmr
            mmrArray.push(parseInt(mmrValue))
            jsonArray.push(json)
            if ((jsonArray.length - 1) % 21 === 0 && jsonArray.length > 1) {
                embedArray.push({
                    color: 15514131,
                    fields: [
                    ]
                })
            }
            else if ((jsonArray.length - 1) % 21 === 0) {
                embedArray.push(embed)
            }
            embedArray[Math.floor((jsonArray.length - 1) / 21)].fields.push({ name: json.name, value: `<@${nameJson.discordId}> ([${mmrValue}](https://www.mk8dx-lounge.com/PlayerDetails/${json.playerId}))`, inline: true })
            embedArray[Math.floor((jsonArray.length - 1) / 21)].fields.sort(function (a, b) { return parseInt(b.value.split('> ([')[1].split(']')[0]) - parseInt(a.value.split('> ([')[1].split(']')[0]); })
            await interaction.editReply({ embeds: embedArray })

        }
        if (i === ids.length - 1 && embedArray[embedArray.length - 1] != undefined) {
            embedArray.forEach(array => {
                array.fields.sort(function (a, b) { return parseInt(b.value.split('> ([')[1].split(']')[0]) - parseInt(a.value.split('> ([')[1].split(']')[0]); })
            })
            embedArray[embedArray.length - 1].fields.push({ name: '\u200B', value: '\u200B' })
            embedArray[embedArray.length - 1].fields.push({ name: "Average", value: `__${parseInt(mmrArray.reduce((a, b) => a + b, 0) / mmrArray.length)}__`, inline: true })
            let top6 = jsonArray.sort((a, b) => (b.maxMmr != undefined ? b.maxMmr : b.mmr) - (a.maxMmr != undefined ? a.maxMmr : a.mmr)).slice(0, 6)
            embedArray[embedArray.length - 1].fields.push({ name: "Top 6", value: `__${parseInt(top6.reduce((a, b) => a + (b.maxMmr != undefined ? b.maxMmr : b.mmr), 0) / top6.length)}__`, inline: true })
            await interaction.editReply({ embeds: embedArray })
        }
        else if (i === ids.length - 1) {
            await interaction.editReply({
                embeds: [
                    {
                        title: "Error",
                        description: "No player found or wrong season",
                        color: 0xff0000,
                    }
                ]
            })
        }

    }
}
export async function averageMmr(searchType, ids, embed, interaction, embedArray, jsonArray, mmrArray) {
    for (let i = 0; i < ids.length; i++) {
        let json
        let season = interaction.options.get("season") && interaction.options.get("season").value != undefined ? "&season=" + interaction.options.get("season").value : ""
        try {
            json = await (await fetch("https://www.mk8dx-lounge.com/api/player?" + searchType + "=" + ids[i] + season + "&quaxly=true")).json()
        } catch (e) {
            console.log(interaction);
            const owner = await client.users.fetch("169497208406802432");
            owner.send(`An error occurred: \`\`\`${e}\`\`\`\n\n\`\`\`${interaction}\`\`\`\n\n\`\`\`${searchType}\`\`\`\n\n\`\`\`${ids[i]}\`\`\``).catch(() => {
                console.log("Error while sending error to owner\n\n" + e + "\n\n" + interaction + "\n\n" + searchType + "\n\n" + ids[i])
            });
            continue;
        }
        if (json.name != undefined && json.mmr != undefined) {
            mmrArray.push(parseInt(json.mmr))
            jsonArray.push(json)
            if ((jsonArray.length - 1) % 21 === 0 && jsonArray.length > 1) {
                embedArray.push({
                    color: 15514131,
                    fields: [
                    ]
                })
            }
            else if ((jsonArray.length - 1) % 21 === 0) {
                embedArray.push(embed)
            }
            embedArray[Math.floor((jsonArray.length - 1) / 21)].fields.push({ name: json.name, value: `<@${json.discordId}> ([${json.mmr}](https://www.mk8dx-lounge.com/PlayerDetails/${json.id}))`, inline: true })
            embedArray[Math.floor((jsonArray.length - 1) / 21)].fields.sort(function (a, b) { return parseInt(b.value.split('> ([')[1].split(']')[0]) - parseInt(a.value.split('> ([')[1].split(']')[0]); })
            await interaction.editReply({ embeds: embedArray })

        }
        if (i === ids.length - 1 && embedArray[embedArray.length - 1] != undefined) {
            embedArray.forEach(array => {
                array.fields.sort(function (a, b) { return parseInt(b.value.split('> ([')[1].split(']')[0]) - parseInt(a.value.split('> ([')[1].split(']')[0]); })
            })
            embedArray[embedArray.length - 1].fields.push({ name: '\u200B', value: '\u200B' })
            embedArray[embedArray.length - 1].fields.push({ name: "Average", value: `__${parseInt(mmrArray.reduce((a, b) => a + b, 0) / mmrArray.length)}__`, inline: true })
            let top6 = jsonArray.sort((a, b) => b.mmr - a.mmr).slice(0, 6)
            embedArray[embedArray.length - 1].fields.push({ name: "Top 6", value: `__${parseInt(top6.reduce((a, b) => a + b.mmr, 0) / top6.length)}__`, inline: true })
            await interaction.editReply({ embeds: embedArray })
        } else if (i === ids.length - 1) {
            await interaction.editReply({
                embeds: [
                    {
                        title: "Error",
                        description: "No player found or wrong season",
                        color: 0xff0000,
                    }
                ]
            })
        }
    }
}

export async function teamFCs(team_id, interaction) {
    let json
    let season = interaction.options.get("season") && interaction.options.get("season").value != undefined ? "Season " + interaction.options.get("season").value + " " : ""

    try {
        json = await (await fetch(`https://www.mariokartcentral.com/mkc/api/registry/teams/${team_id}`)).json()
    } catch (e) {
        return error_embed(interaction, "Team not found")
    }
    if (json.rosters.length === 0) return error_embed(interaction, "This team has no members")
    let ids = []
    json.rosters[json.team_category].members.forEach((player) => { ids.push(player.custom_field) })
    let embed =
    {
        title: "",
        description: `[${json.team_tag} - ${json.team_name}](https://www.mariokartcentral.com/mkc/registry/teams/${team_id})`,
        color: 15514131,
        fields: [
        ],
        thumbnail: {
            url: "https://www.mariokartcentral.com/mkc/storage/" + json.team_logo
        }
    }
    if (!interaction.options.get("stat") || interaction.options.get("stat").value === "average") {
        embed.title = season + "Average MMR"
        await interaction.editReply({ embeds: [embed] }).then(async () => {
            await averageMmr("fc", ids, embed, interaction, [], [], [])
        })
    }
    else if (interaction.options.get("stat").value === "peak") {
        embed.title = season + "Average peak MMR"
        await interaction.editReply({ embeds: [embed] }).then(async () => {
            await averagePeakMmr("fc", ids, embed, interaction, [], [], [])
        })
    }
    else if (interaction.options.get("stat").value === "events") {
        embed.title = season + "Team Events"
        await interaction.editReply({ embeds: [embed] }).then(async () => {
            await teamEvents("fc", ids, embed, interaction, [], [], [])
        })
    }
}
