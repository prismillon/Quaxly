import { bdd, user_list, get_track_formated, save_user_list, error_embed, track_list } from "../utils.js";

import { EmbedBuilder, } from "discord.js";

export const display_time = async (interaction) => {
    let user
    if (user_list[interaction.guild.id] == undefined) {
        return error_embed(interaction, "sorry, but this server is not registered in the database, please register members with the \`/register\` command");
    }
    const args = interaction.options.data;
    if (args.length == 2 && (args[0].name == "item" && args[1].name == "speed" || args[0].name == "speed" && args[1].name == "item")) {
        const speed = interaction.options.get("speed").value;
        let item = "NI";
        if (interaction.options.get("item").value == 1) {
            item = "Shroom";
        }
        if (user_list[interaction.guild.id] == undefined) {
            return error_embed(interaction, "sorry, but this server is not registered in the database, please register members with the \`/register\` command");
        }
        let best_times_string = '';
        let best_time_object = {};
        let user;
        for (let i = 0; i < track_list.length; i++) {
            if (Object.values(best_time_object).length > 0 && !interaction.deferred) await interaction.deferReply();
            for (let j = 0; j < user_list[interaction.guild.id].length; j++) {
                if (bdd[user_list[interaction.guild.id][j]] == undefined) {
                    user_list[interaction.guild.id].splice(j, 1);
                    save_user_list();
                    j--;
                    continue;
                }
                try {
                    user = await interaction.guild.members.fetch(user_list[interaction.guild.id][j]);
                } catch (error) {
                    user_list[interaction.guild.id].splice(j, 1);
                    save_user_list();
                    j--;
                    continue;
                }
                if (user == undefined) {
                    user_list[interaction.guild.id].splice(j, 1);
                    save_user_list();
                    j--;
                    continue;
                }
                if (bdd[user_list[interaction.guild.id][j]][speed][item][track_list[i]] == undefined) {
                    continue;
                }
                if (best_time_object[track_list[i]] == undefined || (bdd[user_list[interaction.guild.id][j]][speed][item][track_list[i]] < best_time_object[track_list[i]].split("`")[1])) {
                    best_time_object[track_list[i]] = "**" + track_list[i] + `**: \`${bdd[user_list[interaction.guild.id][j]][speed][item][track_list[i]]}\` - ${user.displayName}`;
                }
                else if (bdd[user_list[interaction.guild.id][j]][speed][item][track_list[i]] == best_time_object[track_list[i]].split("`")[1]) {
                    best_time_object[track_list[i]] += `/${user.displayName}`;
                }
            }
        }
        for (let track in best_time_object) {
            best_times_string += best_time_object[track] + "\n";
        }
        if (best_times_string == '') {
            return error_embed(interaction, `no times found for this category`);
        }
        interaction.editReply({
            embeds: [
                new EmbedBuilder()
                    .setTitle(`${speed}cc ${item}`)
                    .setColor(0x47e0ff)
                    .setThumbnail(interaction.guild.iconURL())
                    .setDescription(best_times_string),
            ],
        })
    }
    else if (args.length == 3 && interaction.options.get("track") != undefined) {
        const speed = interaction.options.get("speed").value;
        let item = "NI";
        if (interaction.options.get("item").value == 1) {
            item = "Shroom";
        }
        let track = get_track_formated(interaction.options.get("track").value)
        if (track == 0) return await error_embed(interaction, `couldn't find \`${interaction.options.get("track").value}\` in the list, you can find the list of tracks with \`/tracks\``)
        if (user_list[interaction.guild.id] == undefined) {
            return error_embed(interaction, `sorry, but this server is not registered in the database, please register members with the \`/register_user\` command`);
        }
        let best_times_string = '';
        let best_time_object = [];
        for (let i = 0; i < user_list[interaction.guild.id].length; i++) {
            if (bdd[user_list[interaction.guild.id][i]] == undefined) {
                user_list[interaction.guild.id].splice(i, 1);
                save_user_list();
                i--;
                continue;
            }
            try {
                const user = await interaction.guild.members.fetch(user_list[interaction.guild.id][i]);
                if (user == undefined) {
                    user_list[interaction.guild.id].splice(i, 1);
                    save_user_list();
                    i--;
                    continue;
                }
                if (bdd[user_list[interaction.guild.id][i]][speed][item] == undefined) {
                    continue;
                }
                if (bdd[user_list[interaction.guild.id][i]][speed][item][track] != undefined) {
                    best_time_object.push({ time: bdd[user_list[interaction.guild.id][i]][speed][item][track], user: user.displayName });
                }
            }
            catch (e) {
            }
            if (best_time_object.length > 0 && !interaction.deferred) await interaction.deferReply();
        }
        best_time_object.sort((a, b) => {
            if (a["time"] < b["time"]) return -1;
            if (a["time"] > b["time"]) return 1;
            return 0;
        });
        for (let i = 0; i < best_time_object.length; i++) {
            best_times_string += `**${i + 1}**: ${best_time_object[i].user}: \`${best_time_object[i].time}\`\n`;
        }
        if (best_times_string == '') {
            return error_embed(interaction, `sorry, but no one has registered any time for this category`);
        }
        interaction.editReply({
            embeds: [
                new EmbedBuilder()
                    .setTitle(`${speed}cc ${item}`)
                    .setColor(0x47e0ff)
                    .setDescription(best_times_string)
                    .setThumbnail(`http://51.68.230.75:8000/mk8dx_tracks/${track}.png`)
            ],
        })
    }
    else if (args.length == 3 && interaction.options.get("user").value != undefined) {
        const speed = interaction.options.get("speed").value;
        let item = "NI";
        if (interaction.options.get("item").value == 1) {
            item = "Shroom";
        }
        var user_id = interaction.options.get("user").value.replace(/[^0-9]/g, '');
        if (bdd[user_id] == undefined) {
            return error_embed(interaction, "sorry, but the user you provided is invalid or not registered in the database");
        }
        try {
            user = await interaction.guild.members.fetch(user_id);
        }
        catch (e) {
            return error_embed(interaction, "sorry, but the user you provided is not valid");
        }
        let time_list = '';
        let track_rank = [];
        let total_time = 0;
        let nb_track_played = 0;
        let as_time_on_all_tracks = true;
        let total_string = '';
        for (let i = 0; i < track_list.length; i++) {
            if (bdd[user_id][speed][item][track_list[i]] != undefined) {
                nb_track_played++;
                total_time += parseInt(bdd[user_id][speed][item][track_list[i]][0]) * 60000 + parseInt(bdd[user_id][speed][item][track_list[i]][2] + bdd[user_id][speed][item][track_list[i]][3]) * 1000 + parseInt(bdd[user_id][speed][item][track_list[i]][5] + bdd[user_id][speed][item][track_list[i]][6] + bdd[user_id][speed][item][track_list[i]][7]);
                track_rank = [];
                for (let j = 0; j < user_list[interaction.guild.id].length; j++) {
                    if (bdd[user_list[interaction.guild.id][j]] == undefined) {
                        user_list[interaction.guild.id].splice(j, 1);
                        save_user_list();
                        j--;
                        continue;
                    }
                    if (bdd[user_list[interaction.guild.id][j]][speed][item][track_list[i]] != undefined) {
                        track_rank.push({ time: bdd[user_list[interaction.guild.id][j]][speed][item][track_list[i]], user: user_list[interaction.guild.id][j] });
                    }
                }
                track_rank.sort((a, b) => {
                    if (a["time"] < b["time"]) return -1;
                    if (a["time"] > b["time"]) return 1;
                    return 0;
                });
                for (let j = 0; j < track_rank.length; j++) {
                    if (track_rank[j].user == user_id) {
                        time_list += `**${track_list[i]}**: \`${bdd[user_id][speed][item][track_list[i]]}\` - ${j + 1}/${track_rank.length}\n`;
                        break;
                    }
                }
            }
            else {
                as_time_on_all_tracks = false;
            }
            if (track_rank.length > 0 && !interaction.deferred) await interaction.deferReply();
        }
        if (time_list == '') {
            return error_embed(interaction, "sorry, but this user has not registered any time for this category");
        }
        if (as_time_on_all_tracks) {
            let hours = Math.floor(total_time / 3600000);
            let minutes = Math.floor(total_time / 60000) - hours * 60;
            let seconds = Math.floor(total_time / 1000) - hours * 3600 - minutes * 60;
            let milliseconds = total_time - hours * 3600000 - minutes * 60000 - seconds * 1000;
            if (minutes < 10) {
                minutes = "0" + minutes;
            }
            if (seconds < 10) {
                seconds = "0" + seconds;
            }
            if (milliseconds < 10) {
                milliseconds = "00" + milliseconds;
            }
            else if (milliseconds < 100) {
                milliseconds = "0" + milliseconds;
            }
            total_string = `\n**Saved times**: ${nb_track_played}/${track_list.length}\n**Total time**: \`${hours}h${minutes}:${seconds}.${milliseconds}\``;
        }
        else {
            total_string = `\n**Saved times**: ${nb_track_played}/${track_list.length}\n**Total time**: *complete all tracks to get a total time*`;
        }
        interaction.editReply({
            embeds: [
                new EmbedBuilder()
                    .setTitle(`${user.displayName}  ${speed}cc ${item}`)
                    .setColor(0x47e0ff)
                    .setDescription(time_list + total_string)
                    .setThumbnail(user.displayAvatarURL()),
            ],
        })
    }
    else if (args.length == 4) {
        const speed = interaction.options.get("speed").value;
        let item = "NI";
        if (interaction.options.get("item").value == 1) {
            item = "Shroom";
        }
        let track = get_track_formated(interaction.options.get("track").value)
        if (track == 0) return await error_embed(interaction, `couldn't find \`${interaction.options.get("track").value}\` in the list, you can find the list of tracks with \`/tracks\``)
        var user_id = interaction.options.get("user").value.replace(/[^0-9]/g, '');
        if (bdd[user_id] == undefined) {
            return error_embed(interaction, "sorry, but the user you provided is invalid or not registered in the database");
        }
        try {
            user = await interaction.guild.members.fetch(user_id)
        } catch (error) {
            return error_embed(interaction, "sorry, but the user you provided is not valid");
        }
        if (bdd[user_id][speed][item][track] == undefined) {
            return error_embed(interaction, "sorry, but this user has not registered any time for this category");
        }
        interaction.reply({
            embeds: [
                new EmbedBuilder()
                    .setColor(0x47e0ff)
                    .setTitle(`${user.displayName}  ${speed}cc ${item}`)
                    .setDescription(`${track}   -    **${bdd[user_id][speed][item][track]}**`)
                    .setThumbnail(`http://51.68.230.75:8000/mk8dx_tracks/${track}.png`)
            ],
        })
    }
}