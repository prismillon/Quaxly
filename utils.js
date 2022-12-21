import { EmbedBuilder, ActionRowBuilder, ButtonBuilder, ButtonStyle, } from "discord.js";
import fs from "fs";
export const yes_no_buttons = new ActionRowBuilder().addComponents(new ButtonBuilder().setCustomId("Yes").setLabel("Yes").setStyle(ButtonStyle.Success), new ButtonBuilder().setCustomId("No").setLabel("No").setStyle(ButtonStyle.Danger));
export const track_list = fs.readFileSync("./tracklist.txt", "utf-8").replace(/^(?=\n)$|^\s|\s$|\n\n+/gm, "").split(/\r?\n/);
export var bdd = JSON.parse(fs.readFileSync("./bdd.json", "utf8"));
export var user_list = JSON.parse(fs.readFileSync("./user_list.json", "utf8"));

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
    await interaction.reply({ embeds: [embed], ephemeral: true });
}

export async function averageMmr(ids, embed, interaction, embedArray, jsonArray, mmrArray) {
    for (let i = 0; i < ids.length; i++) {
        await fetch("https://www.mk8dx-lounge.com/api/player?discordid=" + ids[i]).then(r => {
            return r.text()
        }).then(r => {
            let json = JSON.parse(r)
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
                embedArray[Math.floor((jsonArray.length - 1) / 21)].fields.push({ name: json.name, value: json.mmr, inline: true })
                interaction.editReply({ embeds: embedArray })

            }
            if (i === ids.length - 1) {
                embedArray[embedArray.length - 1].fields.push({ name: '\u200B', value: '\u200B' })
                embedArray[embedArray.length - 1].fields.push({ name: "MMR average", value: `__${parseInt(mmrArray.reduce((a, b) => a + b, 0) / mmrArray.length)}__`, inline: true })
                let top6 = jsonArray.sort((a, b) => b.mmr - a.mmr).slice(0, 6)
                embedArray[embedArray.length - 1].fields.push({ name: "Top 6 average", value: `__${parseInt(top6.reduce((a, b) => a + b.mmr, 0) / top6.length)}__`, inline: true })
                interaction.editReply({ embeds: embedArray })
            }
        })
    }
}
