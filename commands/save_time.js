import { bdd, is_track_init, user_and_server_id_check, player_update, get_track_formated, save_bdd, error_embed } from "../utils.js";

import { EmbedBuilder, } from "discord.js";

export const save_time = async (interaction) => {
    try {
        let uuid = Date.now()
        const yes_no_buttons = new ActionRowBuilder().addComponents(new ButtonBuilder().setCustomId("Yes" + uuid).setLabel("Yes").setStyle(ButtonStyle.Success), new ButtonBuilder().setCustomId("No" + uuid).setLabel("No").setStyle(ButtonStyle.Danger));
        user_and_server_id_check(interaction.user.id, interaction.guild.id)
        const speed = interaction.options.get("speed").value;
        let track = get_track_formated(interaction.options.get("track").value)
        if (track == 0) return await error_embed(interaction, `couldn't find \`${interaction.options.get("track").value}\` in the list, you can find the list of tracks with \`/tracks\``)
        const time = interaction.options.get("time").value;
        const reg = new RegExp("^[0-9]:[0-5][0-9]\\.[0-9]{3}$");
        if (!reg.test(time)) {
            const embed = new EmbedBuilder()
                .setTitle(`Invalid time format`)
                .setColor(0xff0000)
                .setDescription(`recived \`${time}\` please use this format instead -> \`1:23.456\``);
            await interaction.reply({ embeds: [embed], ephemeral: true });
            return;
        }
        let item = "NI";
        if (interaction.options.get("item").value == 1) {
            item = "Shroom";
        }
        if (is_track_init(interaction.user.id, speed, item, track)) {
            if (bdd[interaction.user.id][speed][item][track] < time) {
                const embed = new EmbedBuilder()
                    .setTitle(`Error`)
                    .setColor(0xff0000)
                    .setDescription(`you already have \`${bdd[interaction.user.id][speed][item][track]}\` on this track, do you really want to override it?`)
                    .setThumbnail(`http://51.68.230.75:8000/mk8dx_tracks/${track}.png`);
                await interaction.reply({
                    embeds: [embed],
                    ephemeral: true,
                    components: [yes_no_buttons],
                });
                const collector = interaction.channel.createMessageComponentCollector({
                    filter: (i) => i.customId.replace(/[^0-9]/gm, '') == uuid && i.user.id === interaction.user.id,
                    max: 1,
                    time: 15000,
                });
                collector.on('end', async () => {
                    await interaction.editReply({
                        embeds: [
                            new EmbedBuilder().setTitle(`Canceled`).setColor(0x00ff00)
                                .setDescription(`you didn't answer in time, the command has been canceled`)
                        ], components: []
                    })
                    collector.stop();
                })
                collector.on("collect", async (i) => {
                    i.customId = i.customId.replace(/[0-9]/gm, '')
                    if (i.customId == "No") {
                        await i.update({
                            embeds: [
                                new EmbedBuilder().setTitle(`Canceled`).setColor(0x00ff00),
                            ],
                            components: [],
                            fetchReply: true,
                        });

                    }
                    if (i.customId == "Yes") {
                        bdd[interaction.user.id][speed][item][track] = time;
                        if (save_bdd() == 0) {
                            return error_embed(i, "could not save the file as expected");
                        }
                        await i.update({
                            embeds: [
                                new EmbedBuilder()
                                    .setTitle(`Done`)
                                    .setColor(0x00ff00)
                                    .setDescription(`you now have **${bdd[interaction.user.id][speed][item][track]}** on \`${track}\` in ${speed} (${item})`)
                                    .setThumbnail(`http://51.68.230.75:8000/mk8dx_tracks/${track}.png`)
                            ],
                            components: [],
                            fetchReply: true,
                        });

                    }
                });
                return;
            }
            else if (bdd[interaction.user.id][speed][item][track] == time) {
                return error_embed(interaction, `you already have \`${bdd[interaction.user.id][speed][item][track]}\` on this track`);
            }
        }
        player_update(interaction.user.id);
        let time_diff = 0;
        let time_diff_str = "";
        if (bdd[interaction.user.id][speed][item][track] != undefined) {
            let old_time = bdd[interaction.user.id][speed][item][track];
            time_diff = (parseInt(old_time[0]) * 60 + parseInt(old_time[2] + old_time[3])) * 1000 + parseInt(old_time[5] + old_time[6] + old_time[7]) - (parseInt(time[0]) * 60 + parseInt(time[2] + time[3])) * 1000 - parseInt(time[5] + time[6] + time[7]);
        }
        if (time_diff != 0) {
            let min = Math.floor(time_diff / 60000);
            let sec = Math.floor((time_diff - min * 60000) / 1000);
            let ms = time_diff - min * 60000 - sec * 1000;
            if (min < 10) {
                min = "0" + min;
            }
            if (sec < 10) {
                sec = "0" + sec;
            }
            if (ms < 10) {
                ms = "00" + ms;
            }
            else if (ms < 100) {
                ms = "0" + ms;
            }
            time_diff_str = `\nyou improved by \`${min}:${sec}.${ms}\` 🏁`;
        }
        bdd[interaction.user.id][speed][item][track] = time;
        if (save_bdd() == 0) {
            return error_embed(interaction, "could not save the new time");
        }
        const embed = new EmbedBuilder()
            .setTitle(`Time saved`)
            .setColor(0x47e0ff)
            .setDescription(`**${interaction.member.displayName}** saved **${time}** on \`${track}\`, ${speed}cc (${item})` + time_diff_str)
            .setThumbnail(`http://51.68.230.75:8000/mk8dx_tracks/${track}.png`);
        await interaction.reply({ embeds: [embed] });
    } catch (e) {
        throw e;
    }
}