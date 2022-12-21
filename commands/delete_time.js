import { bdd, is_track_init, user_and_server_id_check, get_track_formated, save_bdd, error_embed, yes_no_buttons } from "../utils.js";

import { EmbedBuilder, } from "discord.js";

export const delete_time = async (interaction) => {
    user_and_server_id_check(interaction.user.id, interaction.guild.id)
    const args = interaction.options.data;
    if (args.length == 3) {
        const speed = interaction.options.get("speed").value;
        let item = "NI";
        if (interaction.options.get("item").value == 1) {
            item = "Shroom";
        }
        let track = get_track_formated(interaction.options.get("track").value)
        if (track == 0) return await error_embed(interaction, `couldn't find \`${interaction.options.get("track").value}\` in the list, you can find the list of tracks with \`/tracks\``)
        if (is_track_init(interaction.user.id, speed, item, track)) {
            interaction.reply({
                embeds: [
                    new EmbedBuilder()
                        .setTitle(`Are you sure?`)
                        .setColor(0xff0000)
                        .setDescription(`you are about to delete **${bdd[interaction.user.id][speed][item][track]}** on \`${track}\` in ${speed}cc (${item})`)
                        .setThumbnail(`http://51.68.230.75:8000/mk8dx_tracks/${track}.png`),
                ],
                ephemeral: true,
                components: [yes_no_buttons],
            });
            const collector = interaction.channel.createMessageComponentCollector({
                filter: (i) => i.user.id === interaction.user.id,
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
            })
            collector.on("collect", async (i) => {
                if (i.customId == "Yes") {
                    item = "NI";
                    if (interaction.options.get("item").value == 1) {
                        item = "Shroom";
                    }
                    if (!is_track_init(interaction.user.id, speed, item, track)) {
                        return await error_embed(i, `you don't have any time saved on \`${track}\` in ${speed} (${item})`);
                    }
                    delete bdd[interaction.user.id][speed][item][track];
                    if (save_bdd() == 0) {
                        return await error_embed(i, `could not save the file as expected`);
                    }
                    const embed = new EmbedBuilder()
                        .setTitle(`Time deleted`)
                        .setColor(0x47e0ff)
                        .setDescription(`deleted your time on \`${track}\`, ${speed}cc (${item})`)
                        .setThumbnail(`http://51.68.230.75:8000/mk8dx_tracks/${track}.png`);
                    await i.reply({ embeds: [embed] });
                }
                if (i.customId == "No") {
                    await i.update({
                        embeds: [
                            new EmbedBuilder().setTitle(`Canceled`).setColor(0x00ff00),
                        ],
                        components: [],
                        fetchReply: true,
                    });
                }
            })
        }
        else {
            return await error_embed(interaction, `you don't have any time saved on \`${track}\` in ${speed} (${item})`);
        }
    }
    else if (args.length == 0) {
        interaction.reply({
            embeds: [
                new EmbedBuilder()
                    .setTitle(`Are you sure?`)
                    .setColor(0xff0000)
                    .setDescription(`you are about to delete **all** your times`),
            ],
            ephemeral: true,
            components: [yes_no_buttons],
        });
        const collector = interaction.channel.createMessageComponentCollector({
            filter: (i) => i.user.id === interaction.user.id,
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
        })
        collector.on("collect", async (i) => {
            if (i.customId == "Yes") {
                delete bdd[interaction.user.id];
                if (save_bdd() == 0) {
                    return await error_embed(i, `could not save the file as expected`);
                }
                const embed = new EmbedBuilder()
                    .setTitle(`Time deleted`)
                    .setColor(0x47e0ff)
                    .setDescription(`deleted all your times`);
                await i.reply({ embeds: [embed] });
            }
            if (i.customId == "No") {
                await i.update({
                    embeds: [
                        new EmbedBuilder().setTitle(`Canceled`).setColor(0x00ff00),
                    ],
                    components: [],
                    fetchReply: true,
                });
            }
        });
    }
    else if (args.length == 1 && args[0].name == "speed") {
        const speed = interaction.options.get("speed").value;
        interaction.reply({
            embeds: [
                new EmbedBuilder()
                    .setTitle(`Are you sure?`)
                    .setColor(0xff0000)
                    .setDescription(`you are about to delete **all** your times in ${speed}cc`),
            ],
            ephemeral: true,
            components: [yes_no_buttons],
        });
        const collector = interaction.channel.createMessageComponentCollector({
            filter: (i) => i.user.id === interaction.user.id,
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
        })
        collector.on("collect", async (i) => {
            if (i.customId == "Yes") {
                bdd[interaction.user.id][speed].Shroom = {};
                bdd[interaction.user.id][speed].NI = {};
                if (save_bdd() == 0) {
                    return await error_embed(i, `could not save the file as expected`);
                }
                const embed = new EmbedBuilder()
                    .setTitle(`Time deleted`)
                    .setColor(0x47e0ff)
                    .setDescription(`deleted all your times in ${speed}`);
                await i.reply({ embeds: [embed] });
            }
            if (i.customId == "No") {
                await i.update({
                    embeds: [
                        new EmbedBuilder().setTitle(`Canceled`).setColor(0x00ff00),
                    ],
                    components: [],
                    fetchReply: true,
                });
            }
        });
    }
    else if (args.length == 1 && args[0].name == "item") {
        let item = "NI";
        if (interaction.options.get("item").value == 1) {
            item = "Shroom";
        }
        interaction.reply({
            embeds: [
                new EmbedBuilder()
                    .setTitle(`Are you sure?`)
                    .setColor(0xff0000)
                    .setDescription(`you are about to delete **all** your times with ${item}`),
            ],
            ephemeral: true,
            components: [yes_no_buttons],
        });
        const collector = interaction.channel.createMessageComponentCollector({
            filter: (i) => i.user.id === interaction.user.id,
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
        })
        collector.on("collect", async (i) => {
            if (i.customId == "Yes") {
                bdd[interaction.user.id][150][item] = {};
                bdd[interaction.user.id][200][item] = {};
                if (save_bdd() == 0) {
                    return await error_embed(i, `could not save the file as expected`);
                }
                const embed = new EmbedBuilder()
                    .setTitle(`Time deleted`)
                    .setColor(0x47e0ff)
                    .setDescription(`deleted all your times with ${item}`);
                await i.reply({ embeds: [embed] });
            }
            if (i.customId == "No") {
                await i.update({
                    embeds: [
                        new EmbedBuilder().setTitle(`Canceled`).setColor(0x00ff00),
                    ],
                    components: [],
                    fetchReply: true,
                });
            }
        });
    }
    else if (args.length == 1 && args[0].name == "track") {
        let track = get_track_formated(interaction.options.get("track").value)
        if (track == 0) return await error_embed(interaction, `couldn't find \`${interaction.options.get("track").value}\` in the list, you can find the list of tracks with \`/tracks\``)
        interaction.reply({
            embeds: [
                new EmbedBuilder()
                    .setTitle(`Are you sure?`)
                    .setColor(0xff0000)
                    .setDescription(`you are about to delete **all** your times on ${track}`),
            ],
            ephemeral: true,
            components: [yes_no_buttons],
        });
        const collector = interaction.channel.createMessageComponentCollector({
            filter: (i) => i.user.id === interaction.user.id,
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
        })
        collector.on("collect", async (i) => {
            if (i.customId == "Yes") {
                bdd[interaction.user.id][150].Shroom[track] = {};
                bdd[interaction.user.id][150].NI[track] = {};
                bdd[interaction.user.id][200].Shroom[track] = {};
                bdd[interaction.user.id][200].NI[track] = {};
                if (save_bdd() == 0) {
                    return await error_embed(i, `could not save the file as expected`);
                }
                const embed = new EmbedBuilder()
                    .setTitle(`Time deleted`)
                    .setColor(0x47e0ff)
                    .setDescription(`deleted all your times on ${track}`);
                await i.reply({ embeds: [embed] });
            }
            if (i.customId == "No") {
                await i.update({
                    embeds: [
                        new EmbedBuilder().setTitle(`Canceled`).setColor(0x00ff00),
                    ],
                    components: [],
                    fetchReply: true,
                });
            }
        });
    }
    else if (args.length == 2 && (args[0].name == "speed" && args[1].name == "item") || (args[0].name == "item" && args[1].name == "speed")) {
        const speed = interaction.options.get("speed").value;
        let item = "NI";
        if (interaction.options.get("item").value == 1) {
            item = "Shroom";
        }
        interaction.reply({
            embeds: [
                new EmbedBuilder()
                    .setTitle(`Are you sure?`)
                    .setColor(0xff0000)
                    .setDescription(`you are about to delete **all** your times in ${item} on ${speed}cc`),
            ],
            ephemeral: true,
            components: [yes_no_buttons],
        });
        const collector = interaction.channel.createMessageComponentCollector({
            filter: (i) => i.user.id === interaction.user.id,
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
        })
        collector.on("collect", async (i) => {
            if (i.customId == "Yes") {
                bdd[interaction.user.id][speed][item] = {};
                if (save_bdd() == 0) {
                    return await error_embed(i, `could not save the file as expected`);
                }
                const embed = new EmbedBuilder()
                    .setTitle(`Time deleted`)
                    .setColor(0x47e0ff)
                    .setDescription(`deleted all your times in ${speed} with ${item}`);
                await i.reply({ embeds: [embed] });
            }
            if (i.customId == "No") {
                await i.update({
                    embeds: [
                        new EmbedBuilder().setTitle(`Canceled`).setColor(0x00ff00),
                    ],
                    components: [],
                    fetchReply: true,
                });
            }
        });
    }
    else if (args.length == 2 && (args[0].name == "speed" && args[1].name == "track") || (args[0].name == "track" && args[1].name == "speed")) {
        const speed = interaction.options.get("speed").value;
        let track = get_track_formated(interaction.options.get("track").value)
        if (track == 0) return await error_embed(interaction, `couldn't find \`${interaction.options.get("track").value}\` in the list, you can find the list of tracks with \`/tracks\``)
        interaction.reply({
            embeds: [
                new EmbedBuilder()
                    .setTitle(`Are you sure?`)
                    .setColor(0xff0000)
                    .setDescription(`you are about to delete **all** your times on ${track} in ${speed}cc`)
                    .setThumbnail(`http://51.68.230.75:8000/mk8dx_tracks/${track}.png`),
            ],
            ephemeral: true,
            components: [yes_no_buttons],
        });
        const collector = interaction.channel.createMessageComponentCollector({
            filter: (i) => i.user.id === interaction.user.id,
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
        })
        collector.on("collect", async (i) => {
            if (i.customId == "Yes") {
                delete bdd[interaction.user.id][speed].Shroom[track];
                delete bdd[interaction.user.id][speed].NI[track];
                if (save_bdd() == 0) {
                    return await error_embed(i, `could not save the file as expected`);
                }
                const embed = new EmbedBuilder()
                    .setTitle(`Time deleted`)
                    .setColor(0x47e0ff)
                    .setDescription(`deleted all your times on ${track} in ${speed}`)
                    .setThumbnail(`http://51.68.230.75:8000/mk8dx_tracks/${track}.png`);
                await i.reply({ embeds: [embed] });
            }
            if (i.customId == "No") {
                await i.update({
                    embeds: [
                        new EmbedBuilder().setTitle(`Canceled`).setColor(0x00ff00),
                    ],
                    components: [],
                    fetchReply: true,
                });
            }
        });
    }
    else if (args.length == 2 && (args[0].name == "item" && args[1].name == "track") || (args[0].name == "track" && args[1].name == "item")) {
        let item = "NI";
        if (interaction.options.get("item").value == 1) {
            item = "Shroom";
        }
        let track = get_track_formated(interaction.options.get("track").value)
        if (track == 0) return await error_embed(interaction, `couldn't find \`${interaction.options.get("track").value}\` in the list, you can find the list of tracks with \`/tracks\``)
        interaction.reply({
            embeds: [
                new EmbedBuilder()
                    .setTitle(`Are you sure?`)
                    .setColor(0xff0000)
                    .setDescription(`you are about to delete **all** your times on ${track} with ${item}`)
                    .setThumbnail(`http://51.68.230.75:8000/mk8dx_tracks/${track}.png`),
            ],
            ephemeral: true,
            components: [yes_no_buttons],
        });
        const collector = interaction.channel.createMessageComponentCollector({
            filter: (i) => i.user.id === interaction.user.id,
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
        })
        collector.on("collect", async (i) => {
            if (i.customId == "Yes") {
                delete bdd[interaction.user.id][150][item][track];
                delete bdd[interaction.user.id][200][item][track];
                if (save_bdd() == 0) {
                    return await error_embed(i, `could not save the file as expected`);
                }
                const embed = new EmbedBuilder()
                    .setTitle(`Time deleted`)
                    .setColor(0x47e0ff)
                    .setDescription(`deleted all your times on ${track} with ${item}`)
                    .setThumbnail(`http://51.68.230.75:8000/mk8dx_tracks/${track}.png`);
                await interaction.reply({ embeds: [embed] });
            }
            if (i.customId == "No") {
                await i.update({
                    embeds: [
                        new EmbedBuilder().setTitle(`Canceled`).setColor(0x00ff00),
                    ],
                    components: [],
                    fetchReply: true,
                });
            }
        });
    }
}