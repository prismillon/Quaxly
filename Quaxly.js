const { Client, GatewayIntentBits, EmbedBuilder, ActivityType, ActionRowBuilder, ButtonBuilder, ButtonStyle, } = require("discord.js");

const client = new Client({ intents: [GatewayIntentBits.Guilds, GatewayIntentBits.GuildMembers] });
const token = require("./config.json");
const fs = require("fs");
const buttons = new ActionRowBuilder().addComponents(new ButtonBuilder().setCustomId("Yes").setLabel("Yes").setStyle(ButtonStyle.Success), new ButtonBuilder().setCustomId("No").setLabel("No").setStyle(ButtonStyle.Danger));

const track_list = fs.readFileSync("./tracklist.txt", "utf-8").replace(/^(?=\n)$|^\s|\s$|\n\n+/gm, "").split(/\r?\n/);
bdd = JSON.parse(fs.readFileSync("./bdd.json", "utf8"));
user_list = JSON.parse(fs.readFileSync("./user_list.json", "utf8"));

fs.writeFileSync("./bdd_backup.json", JSON.stringify(bdd, null, 4));
fs.writeFileSync("./user_list_backup.json", JSON.stringify(user_list, null, 4));

function is_track_init(user_id, speed, item, track) {
    if (bdd[user_id] != undefined && bdd[user_id][speed] != undefined && bdd[user_id][speed][item] != undefined && bdd[user_id][speed][item][track] != undefined) {
        return true;
    }
    return false;
}

function user_and_server_id_check(user_id, guild_id) {
    if (user_list[guild_id] == undefined) {
        user_list[guild_id] = [user_id];
    }
    else if (!user_list[guild_id].includes(user_id)) {
        user_list[guild_id].push(user_id);
    }
    save_user_list();
}

function player_update(user_id) {
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

function get_track_formated(track) {
    for (let i = 0; i < track_list.length; i++) {
        if (track_list[i].toLowerCase() == track.toLowerCase()) {
            return track_list[i];
        }
    }
    return 0
}

function save_bdd() {
    fs.writeFile("./bdd.json", JSON.stringify(bdd, null, 4), (err) => {
        if (err) {
            console.error(err);
            return 0;
        }
        return 1;
    });
}

function save_user_list() {
    fs.writeFile("./user_list.json", JSON.stringify(user_list, null, 4), (err) => {
        if (err) {
            console.error(err);
            return 0;
        }
        return 1;
    });
}

function error_embed(interaction, error) {
    const embed = new EmbedBuilder()
        .setTitle("Error")
        .setDescription(error)
        .setColor(0xff0000)
    interaction.reply({ embeds: [embed], ephemeral: true });
}

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

client.on("interactionCreate", async (interaction) => {
    if (!interaction.isChatInputCommand()) return;

    if (interaction.commandName === "ping") {
        const embed = new EmbedBuilder()
            .setTitle("Pong!")
            .setColor(0x47e0ff)
            .setDescription("took " + client.ws.ping + "ms");
        await interaction.reply({ embeds: [embed], ephemeral: true });
    }
    if (interaction.commandName === "save_time") {
        user_and_server_id_check(interaction.user.id, interaction.guild.id)
        const speed = interaction.options.get("speed").value;
        track = get_track_formated(interaction.options.get("track").value)
        if (track == 0) return error_embed(interaction, `couldn't find \`${interaction.options.get("track").value}\` in the list`)
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
        item = "NI";
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
                    components: [buttons],
                });
                const collector = interaction.channel.createMessageComponentCollector({
                    filter: (i) => i.user.id === interaction.user.id,
                    max: 1,
                    time: 15000,
                });
                collector.on("collect", async (i) => {
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
    }
    if (interaction.commandName === "delete_time") {
        user_and_server_id_check(interaction.user.id, interaction.guild.id)
        const args = interaction.options.data;
        if (args.length == 3) {
            const speed = interaction.options.get("speed").value;
            item = "NI";
            if (interaction.options.get("item").value == 1) {
                item = "Shroom";
            }
            track = get_track_formated(interaction.options.get("track").value)
            if (track == 0) return error_embed(interaction, `couldn't find \`${interaction.options.get("track").value}\` in the list`)
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
                    components: [buttons],
                });
                const collector = interaction.channel.createMessageComponentCollector({
                    filter: (i) => i.user.id === interaction.user.id,
                    max: 1,
                    time: 15000,
                });
                collector.on("collect", async (i) => {
                    if (i.customId == "Yes") {
                        item = "NI";
                        if (interaction.options.get("item").value == 1) {
                            item = "Shroom";
                        }
                        if (!is_track_init(interaction.user.id, speed, item, track)) {
                            return error_embed(i, `you don't have any time saved on \`${track}\` in ${speed} (${item})`);
                        }
                        delete bdd[interaction.user.id][speed][item][track];
                        if (save_bdd() == 0) {
                            return error_embed(i, `could not save the file as expected`);
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
                });
            }
            else {
                return error_embed(interaction, `you don't have any time saved on \`${track}\` in ${speed} (${item})`);
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
                components: [buttons],
            });
            const collector = interaction.channel.createMessageComponentCollector({
                filter: (i) => i.user.id === interaction.user.id,
                max: 1,
                time: 15000,
            });
            collector.on("collect", async (i) => {
                if (i.customId == "Yes") {
                    delete bdd[interaction.user.id];
                    if (save_bdd() == 0) {
                        return error_embed(i, `could not save the file as expected`);
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
                components: [buttons],
            });
            const collector = interaction.channel.createMessageComponentCollector({
                filter: (i) => i.user.id === interaction.user.id,
                max: 1,
                time: 15000,
            });
            collector.on("collect", async (i) => {
                if (i.customId == "Yes") {
                    bdd[interaction.user.id][speed].Shroom = {};
                    bdd[interaction.user.id][speed].NI = {};
                    if (save_bdd() == 0) {
                        return error_embed(i, `could not save the file as expected`);
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
            item = "NI";
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
                components: [buttons],
            });
            const collector = interaction.channel.createMessageComponentCollector({
                filter: (i) => i.user.id === interaction.user.id,
                max: 1,
                time: 15000,
            });
            collector.on("collect", async (i) => {
                if (i.customId == "Yes") {
                    bdd[interaction.user.id][150][item] = {};
                    bdd[interaction.user.id][200][item] = {};
                    if (save_bdd() == 0) {
                        return error_embed(i, `could not save the file as expected`);
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
            track = get_track_formated(interaction.options.get("track").value)
            if (track == 0) return error_embed(interaction, `couldn't find \`${interaction.options.get("track").value}\` in the list`)
            interaction.reply({
                embeds: [
                    new EmbedBuilder()
                        .setTitle(`Are you sure?`)
                        .setColor(0xff0000)
                        .setDescription(`you are about to delete **all** your times on ${track}`),
                ],
                ephemeral: true,
                components: [buttons],
            });
            const collector = interaction.channel.createMessageComponentCollector({
                filter: (i) => i.user.id === interaction.user.id,
                max: 1,
                time: 15000,
            });
            collector.on("collect", async (i) => {
                if (i.customId == "Yes") {
                    bdd[interaction.user.id][150].Shroom[track] = {};
                    bdd[interaction.user.id][150].NI[track] = {};
                    bdd[interaction.user.id][200].Shroom[track] = {};
                    bdd[interaction.user.id][200].NI[track] = {};
                    if (save_bdd() == 0) {
                        return error_embed(i, `could not save the file as expected`);
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
            item = "NI";
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
                components: [buttons],
            });
            const collector = interaction.channel.createMessageComponentCollector({
                filter: (i) => i.user.id === interaction.user.id,
                max: 1,
                time: 15000,
            });
            collector.on("collect", async (i) => {
                if (i.customId == "Yes") {
                    bdd[interaction.user.id][speed][item] = {};
                    if (save_bdd() == 0) {
                        return error_embed(i, `could not save the file as expected`);
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
            track = get_track_formated(interaction.options.get("track").value)
            if (track == 0) return error_embed(interaction, `couldn't find \`${interaction.options.get("track").value}\` in the list`)
            interaction.reply({
                embeds: [
                    new EmbedBuilder()
                        .setTitle(`Are you sure?`)
                        .setColor(0xff0000)
                        .setDescription(`you are about to delete **all** your times on ${track} in ${speed}cc`)
                        .setThumbnail(`http://51.68.230.75:8000/mk8dx_tracks/${track}.png`),
                ],
                ephemeral: true,
                components: [buttons],
            });
            const collector = interaction.channel.createMessageComponentCollector({
                filter: (i) => i.user.id === interaction.user.id,
                max: 1,
                time: 15000,
            });
            collector.on("collect", async (i) => {
                if (i.customId == "Yes") {
                    delete bdd[interaction.user.id][speed].Shroom[track];
                    delete bdd[interaction.user.id][speed].NI[track];
                    if (save_bdd() == 0) {
                        return error_embed(i, `could not save the file as expected`);
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
            item = "NI";
            if (interaction.options.get("item").value == 1) {
                item = "Shroom";
            }
            track = get_track_formated(interaction.options.get("track").value)
            if (track == 0) return error_embed(interaction, `couldn't find \`${interaction.options.get("track").value}\` in the list`)
            interaction.reply({
                embeds: [
                    new EmbedBuilder()
                        .setTitle(`Are you sure?`)
                        .setColor(0xff0000)
                        .setDescription(`you are about to delete **all** your times on ${track} with ${item}`)
                        .setThumbnail(`http://51.68.230.75:8000/mk8dx_tracks/${track}.png`),
                ],
                ephemeral: true,
                components: [buttons],
            });
            const collector = interaction.channel.createMessageComponentCollector({
                filter: (i) => i.user.id === interaction.user.id,
                max: 1,
                time: 15000,
            });
            collector.on("collect", async (i) => {
                if (i.customId == "Yes") {
                    delete bdd[interaction.user.id][150][item][track];
                    delete bdd[interaction.user.id][200][item][track];
                    if (save_bdd() == 0) {
                        return error_embed(i, `could not save the file as expected`);
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
    if (interaction.commandName === "import_times") {
        user_and_server_id_check(interaction.user.id, interaction.guild.id)
        player_update(interaction.user.id)
        const speed = interaction.options.get("speed").value;
        item = "NI";
        if (interaction.options.get("item").value == 1) {
            item = "Shroom";
        }
        const list = interaction.options.get("list").value;
        const list_array = list.match(/[a-z,A-Z,0-9]+ : [0-9]+\/[0-9]+ -> [0-9]:[0-5][0-9]\.[0-9]{3}/g);
        if (list_array == null) {
            return error_embed(interaction, "could not find any time in the list you provided");
        }
        for (let i = 0; i < list_array.length; i++) {
            track = list_array[i].split(" : ")[0];
            for (let i = 0; i < track_list.length; i++) {
                if (track_list[i].toLowerCase() == track.toLowerCase()) {
                    track = track_list[i];
                    break;
                }
                if (i == track_list.length - 1) {
                    continue;
                }
            }
            let time = list_array[i].split(" -> ")[1];
            bdd[interaction.user.id][speed][item][track] = time;
        }
        if (save_bdd() == 0) {
            return error_embed(interaction, `could not save the file as expected`);
        }
        const embed = new EmbedBuilder()
            .setTitle(`Times imported`)
            .setColor(0x47e0ff)
            .setDescription(`imported all your times from the list`);
        await interaction.reply({ embeds: [embed] });
    }
    if (interaction.commandName === "display_time") {
        if (user_list[interaction.guild.id] == undefined) {
            return error_embed(interaction, "sorry, but this server is not registered in the database, please register members with the \`/register\` command");
        }
        const args = interaction.options.data;
        if (args.length == 2 && (args[0].name == "item" && args[1].name == "speed" || args[0].name == "speed" && args[1].name == "item")) {
            const speed = interaction.options.get("speed").value;
            item = "NI";
            if (interaction.options.get("item").value == 1) {
                item = "Shroom";
            }
            if (user_list[interaction.guild.id] == undefined) {
                return error_embed(interaction, "sorry, but this server is not registered in the database, please register members with the \`/register\` command");
            }
            best_times_string = '';
            best_time_object = {};
            for (let i = 0; i < track_list.length; i++) {
                for (let j = 0; j < user_list[interaction.guild.id].length; j++) {
                    if (bdd[user_list[interaction.guild.id][j]] == undefined) {
                        user_list[interaction.guild.id].splice(j, 1);
                        save_user_list();
                        j--;
                        continue;
                    }
                    const user = await interaction.guild.members.fetch(user_list[interaction.guild.id][j]);
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
            interaction.reply({
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
            item = "NI";
            if (interaction.options.get("item").value == 1) {
                item = "Shroom";
            }
            track = get_track_formated(interaction.options.get("track").value)
            if (track == 0) return error_embed(interaction, `couldn't find \`${interaction.options.get("track").value}\` in the list`)
            if (user_list[interaction.guild.id] == undefined) {
                return error_embed(interaction, `sorry, but this server is not registered in the database, please register members with the \`/register_user\` command`);
            }
            best_times_string = '';
            best_time_object = [];
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
            interaction.reply({
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
            item = "NI";
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
            time_list = '';
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
            interaction.reply({
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
            item = "NI";
            if (interaction.options.get("item").value == 1) {
                item = "Shroom";
            }
            track = get_track_formated(interaction.options.get("track").value)
            if (track == 0) return error_embed(interaction, `couldn't find \`${interaction.options.get("track").value}\` in the list`)
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
    if (interaction.commandName == "help") {
        //get last 8 tracks from tracklist
        let new_tracks = track_list.slice(-8);
        let new_tracks_string = "";
        for (let i = 0; i < new_tracks.length; i++) {
            new_tracks_string += `\`${new_tracks[i]}\` `;
        }
        interaction.reply({
            embeds: [
                new EmbedBuilder()
                    .setTitle("Help menu")
                    .setColor(0x47e0ff)
                    .setThumbnail("https://archives.bulbagarden.net/media/upload/4/49/Quaxly.png")
                    .setFooter({ text: "Made by pierre#1111, feel free to contact me if you have any questions" })
                    .addFields({
                        name: "/ping",
                        value: "Returns the bot's latency",

                    },
                        {
                            name: "/save_time",
                            value: "Saves your time in the chosen category",
                        },
                        {
                            name: "/delete_time",
                            value: "Deletes times based on the parameters you provide",
                        },
                        {
                            name: "/import_times",
                            value: "Import times from Cadoizzob#8500's bot, copy paste the text from the bot in the list field",
                        },
                        {
                            name: "/display_time",
                            value: "Displays your times based on the parameters you provide",
                        },
                        {
                            name: "/register_user",
                            value: "Register the user selected in the server",
                        },
                        {
                            name: "/remove_user",
                            value: "Remove the user selected from the server",
                        },
                        {
                            name: "Last 8 dlc tracks names in order:",
                            value: new_tracks_string,
                        }
                    )
            ],
        })
    }
    if (interaction.commandName == "register_user") {
        if (user_list[interaction.guild.id] == undefined) {
            user_list[interaction.guild.id] = [];
        }
        var user_id = interaction.options.get("user").value.replace(/[^0-9]/g, '');
        if (bdd[user_id] == undefined) {
            return error_embed(interaction, "sorry, but the user you provided is invalid or not registered in the database");
        }
        try {
            user = await interaction.guild.members.fetch(user_id);
        }
        catch (e) {
            return error_embed(interaction, "sorry, but the user you provided is not valid or not in this server");
        }
        if (user_list[interaction.guild.id].includes(user_id)) {
            return error_embed(interaction, "sorry, but this user is already registered in this server");
        }
        user_list[interaction.guild.id].push(user_id);
        interaction.reply({
            embeds: [
                new EmbedBuilder()
                    .setTitle("User registered")
                    .setColor(0x47e0ff)
                    .setDescription(`${user.displayName} has been registered in this server`)
                    .setThumbnail(user.displayAvatarURL()),
            ],
        })
    }
    if (interaction.commandName == "remove_user") {
        if (user_list[interaction.guild.id] == undefined) {
            user_list[interaction.guild.id] = [];
        }
        var user_id = interaction.options.get("user").value.replace(/[^0-9]/g, '');
        if (!user_list[interaction.guild.id].includes(user_id)) {
            return error_embed(interaction, "sorry, but this user is invalid or not registered in this server");
        }
        user_list[interaction.guild.id].splice(user_list[interaction.guild.id].indexOf(user_id), 1);
        interaction.reply({
            embeds: [
                new EmbedBuilder()
                    .setTitle("User removed")
                    .setColor(0x47e0ff)
                    .setDescription(`${user_id} has been removed from this server`)
                    .setThumbnail(interaction.guild.iconURL()),
            ],
        })
    }
    if (interaction.commandName === "team_mmr") {
        const role = interaction.options.get("role").value.replace(/\D/g, '');
        if (role.length === 18 && interaction.options.get("role").value.includes('<@&')) {
            interaction.guild.members.fetch()
                .then(async members => {
                    const ids = members.filter(mmbr => mmbr.roles.cache.get(role)).map(m => m.user.id)
                    console.log(interaction.options.get("role"))
                    let embed =
                    {
                        title: "Average MMR ",
                        description: interaction.options.get("role").value,
                        color: 15514131,
                        fields: [
                        ],
                        thumbnail: {
                            url: "https://cdn.discordapp.com/icons/445404006177570829/a_8fd213e4469496c5da086d02b195f4ff.gif?size=96"
                        }
                    }

                    let mmrArray = []
                    let jsonArray = []
                    let embedArray = []
                    if (ids.length > 300) {
                        interaction.reply({
                            embeds: [{
                                description: "Your role have too many members. Please retry with another role under 300 members.",
                                color: 15863148
                            }]
                        })
                    }
                    else {
                        interaction.reply({ embeds: [embed] }).then(async () => {
                            for (let i = 0; i < ids.length; i++) {
                                await fetch("https://www.mk8dx-lounge.com/api/player?discordid=" + ids[i], {
                                    "headers": {
                                        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
                                        "accept-language": "en-US,en;q=0.9,fr-FR;q=0.8,fr;q=0.7,ja-FR;q=0.6,ja;q=0.5",
                                        "cache-control": "max-age=0",
                                        "sec-ch-ua": "\"Not?A_Brand\";v=\"8\", \"Chromium\";v=\"108\", \"Google Chrome\";v=\"108\"",
                                        "sec-ch-ua-mobile": "?0",
                                        "sec-ch-ua-platform": "\"Windows\"",
                                        "sec-fetch-dest": "document",
                                        "sec-fetch-mode": "navigate",
                                        "sec-fetch-site": "none",
                                        "sec-fetch-user": "?1",
                                        "upgrade-insecure-requests": "1"
                                    },
                                    "referrerPolicy": "strict-origin-when-cross-origin",
                                    "body": null,
                                    "method": "GET",
                                    "mode": "cors",
                                    "credentials": "include"
                                }).then(r => {
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
                        })
                    }
                });
        }
        else return error_embed(interaction, "Please use a @role");
    }
    if (interaction.commandName === "name_history") {
        const discordId = interaction.options.get("player").value.replace(/\D/g, '');
        if (discordId.length === 18) {
            fetch("https://www.mk8dx-lounge.com/api/player?discordid=" + discordId, {
                "headers": {
                    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
                    "accept-language": "en-US,en;q=0.9,fr-FR;q=0.8,fr;q=0.7,ja-FR;q=0.6,ja;q=0.5",
                    "cache-control": "max-age=0",
                    "sec-ch-ua": "\"Not?A_Brand\";v=\"8\", \"Chromium\";v=\"108\", \"Google Chrome\";v=\"108\"",
                    "sec-ch-ua-mobile": "?0",
                    "sec-ch-ua-platform": "\"Windows\"",
                    "sec-fetch-dest": "document",
                    "sec-fetch-mode": "navigate",
                    "sec-fetch-site": "none",
                    "sec-fetch-user": "?1",
                    "upgrade-insecure-requests": "1"
                },
                "referrerPolicy": "strict-origin-when-cross-origin",
                "body": null,
                "method": "GET",
                "mode": "cors",
                "credentials": "include"
            }).then(r => {
                return r.text()
            }).then(r => {
                const currentName = JSON.parse(r).name
                fetch("https://www.mk8dx-lounge.com/api/player/details?name=" + currentName, {
                    "headers": {
                        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
                        "accept-language": "en-US,en;q=0.9,fr-FR;q=0.8,fr;q=0.7,ja-FR;q=0.6,ja;q=0.5",
                        "sec-ch-ua": "\"Not?A_Brand\";v=\"8\", \"Chromium\";v=\"108\", \"Google Chrome\";v=\"108\"",
                        "sec-ch-ua-mobile": "?0",
                        "sec-ch-ua-platform": "\"Windows\"",
                        "sec-fetch-dest": "document",
                        "sec-fetch-mode": "navigate",
                        "sec-fetch-site": "none",
                        "sec-fetch-user": "?1",
                        "upgrade-insecure-requests": "1"
                    },
                    "referrerPolicy": "strict-origin-when-cross-origin",
                    "body": null,
                    "method": "GET",
                    "mode": "cors",
                    "credentials": "include"
                }).then(r => {
                    return r.text()
                }).then(r => {
                    const json = JSON.parse(r)
                    let nameDate = new Date(json.nameHistory[0].changedOn)
                    let nextChange
                    nameDate.setDate(nameDate.getDate() + 60)
                    if (nameDate < new Date()) {
                        nextChange = "✅ User can change their name since <t:" + Math.floor(nameDate.getTime() / 1000) + '>'
                    }
                    else {
                        nextChange = "⏳ User will be able to change their name on <t:" + Math.floor(nameDate.getTime() / 1000) + '>'
                    }
                    let embed =
                    {
                        title: currentName + "'s name history",
                        description: nextChange,
                        color: 15514131,
                        fields: [],
                        thumbnail: {
                            url: "https://cdn.discordapp.com/icons/445404006177570829/a_8fd213e4469496c5da086d02b195f4ff.gif?size=96"
                        }
                    }
                    json.nameHistory.forEach(function (nameArray) {
                        embed.fields.push({ name: nameArray.name, value: 'Changed on: <t:' + Math.floor(new Date(nameArray.changedOn).getTime() / 1000) + '>', inline: false })
                    })
                    interaction.reply({ embeds: [embed] })
                })
            })
        }
        else return error_embed(interaction, "Please use a @user or ID");
    }
});

client.login(token.Quaxly);
