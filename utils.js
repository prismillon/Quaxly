import { EmbedBuilder } from "discord.js";
import { client } from "./Quaxly.js";
import fs from "fs";

export const track_list = fs.readFileSync("./tracklist.txt", "utf-8").replace(/^(?=\n)$|^\s|\s$|\n\n+/gm, "").split(/\r?\n/);
export var bdd = JSON.parse(fs.readFileSync("./bdd.json", "utf8"));
export var user_list = JSON.parse(fs.readFileSync("./user_list.json", "utf8"));
export let playerList = []
export let teamList


export async function updatePlayerList() {
    let playerObjectList = await (await fetch("https://www.mk8dx-lounge.com/api/player/list")).json()
    playerList = playerObjectList.players
    teamList = await (await fetch("https://www.mariokartcentral.com/mkc/api/registry/teams/category/150cc")).json()
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

export async function playersStats(searchType, ids, embed, interaction) {
    let season = interaction.options.get("season") && interaction.options.get("season").value != undefined ? "&season=" + interaction.options.get("season").value : "";
    let type = interaction.options.get("stat") && interaction.options.get("stat").value != undefined ? interaction.options.get("stat").value : "average"
    const stats = ids.map(el => fetch("https://www.mk8dx-lounge.com/api/player?" + searchType + "=" + el + season + "&quaxly=true"));

    let data = await Promise.allSettled(stats)
        .then(responses => {
            const fulfilledResponses = responses.filter(response => response.status === "fulfilled" && response.value.status === 200);
            const jsonPromises = fulfilledResponses.map(response => response.value.json());
            return Promise.all(jsonPromises);
        });
    data = data.filter(el => el.mmr != undefined)
    if (data.length == 0){
        return await interaction.editReply({
            embeds: [
                {
                    title: "Error",
                    description: "No player found or wrong season",
                    color: 0xff0000,
                }
            ]
        })
    }
    switch (type) {
        case "peak":
            data.forEach(el => {
                if (el.maxMmr != undefined) return el.target = el.maxMmr
                return el.target = el.mmr
            });
            break;
        case "events":
            for (const bPlayer of playerList) {
                const { name, eventsPlayed } = bPlayer

                for (const sPlayer of data) {
                    if (sPlayer.name === name) {
                        sPlayer.target = eventsPlayed
                        break;
                    }
                }
            }
            break;
        default:
            data.forEach(el => {
                return el.target = el.mmr
            })
            break;
    }
    data.sort((a, b) => b.target - a.target)
    let embedArray = [embed]
    data.forEach(el => {
        embedArray[embedArray.length-1].fields.push({ name: el.name, value: `<@${el.discordId}> ([${el.target}](https://www.mk8dx-lounge.com/PlayerDetails/${el.id}))`, inline: true })
        if (embedArray[embedArray.length-1].fields.length >= 21) embedArray.push({ color: 15514131, fields: [] })
    })
    embedArray[embedArray.length - 1].fields.push({ name: '\u200B', value: '\u200B' })
    embedArray[embedArray.length - 1].fields.push({ name: "Average", value: `__${(data.reduce((a, b) => a + b.target, 0) / data.length).toFixed()}__`, inline: true })
    let top6 = data.slice(0, 6)
    embedArray[embedArray.length - 1].fields.push({ name: "Top 6", value: `__${(top6.reduce((a, b) => a + b.target, 0) / top6.length).toFixed()}__`, inline: true })
    await interaction.editReply({ embeds: embedArray })
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
    if (!interaction.options.get("stat") || interaction.options.get("stat").value === "average") embed.title = season + "Average MMR"
    else if (interaction.options.get("stat").value === "peak") embed.title = season + "Average peak MMR"
    else if (interaction.options.get("stat").value === "events") embed.title = season + "Team Events"
    await playersStats("fc", ids, embed, interaction)
}
