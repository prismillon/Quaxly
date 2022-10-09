const { Client, GatewayIntentBits, EmbedBuilder, ActivityType, ActionRowBuilder, ButtonBuilder, ButtonStyle, } = require("discord.js");

const client = new Client({ intents: [GatewayIntentBits.Guilds, GatewayIntentBits.GuildMembers] });
const token = require("./config.json");
const fs = require("fs");
const { time } = require("console");
const buttons = new ActionRowBuilder().addComponents(new ButtonBuilder().setCustomId("Yes").setLabel("Yes").setStyle(ButtonStyle.Success), new ButtonBuilder().setCustomId("No").setLabel("No").setStyle(ButtonStyle.Danger));

function is_track_init(user_id, speed, item, track) {
    if (bdd[user_id] != undefined && bdd[user_id][speed] != undefined && bdd[user_id][speed][item] != undefined && bdd[user_id][speed][item][track] != undefined) {
        return true;
    }
    return false;
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

bdd = JSON.parse(fs.readFileSync("./bdd.json", "utf8"));

user_list = JSON.parse(fs.readFileSync("./user_list.json", "utf8"));

fs.writeFileSync("./bdd_backup.json", JSON.stringify(bdd, null, 4));

fs.writeFileSync("./user_list_backup.json", JSON.stringify(user_list, null, 4));

const track_list = fs.readFileSync("./tracklist.txt", "utf-8").split(/\r?\n/);

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
        if (user_list[interaction.guild.id] == undefined) {
            user_list[interaction.guild.id] = [interaction.user.id];
            save_user_list();
        }
        else if (!user_list[interaction.guild.id].includes(interaction.user.id)) {
            user_list[interaction.guild.id].push(interaction.user.id);
            save_user_list();
        }
        const speed = interaction.options.get("speed").value;
        track = interaction.options.get("track").value;
        for (let i = 0; i < track_list.length; i++) {
            if (track_list[i].toLowerCase() == track.toLowerCase()) {
                track = track_list[i];
                break;
            }
            if (i == track_list.length - 1) {
                const embed = new EmbedBuilder()
                    .setTitle("Error")
                    .setColor(0xff0000)
                    .setDescription(`could not find \`${track}\` in the track list`);
                await interaction.reply({ embeds: [embed], ephemeral: true });
                return;
            }
        }
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
                    .setDescription(`you already have \`${bdd[interaction.user.id][speed][item][track]}\` on this track, do you really want to override it?`);
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
                            i.reply({ embeds: [new EmbedBuilder().setTitle(`Error`).setColor(0xff0000).setDescription(`could not save the new time`)], ephemeral: true });
                            return;
                        }
                        await i.update({
                            embeds: [
                                new EmbedBuilder()
                                    .setTitle(`Done`)
                                    .setColor(0x00ff00)
                                    .setDescription(`you now have **${bdd[interaction.user.id][speed][item][track]}** on \`${track}\` in ${speed} (${item})`),
                            ],
                            components: [],
                            fetchReply: true,
                        });

                    }
                });
                return;
            }
            else if (bdd[interaction.user.id][speed][item][track] == time) {
                const embed = new EmbedBuilder()
                    .setTitle(`Error`)
                    .setColor(0xff0000)
                    .setDescription(`you already have **${bdd[interaction.user.id][speed][item][track]}** on \`${track}\` in ${speed} (${item})`);
                await interaction.reply({ embeds: [embed], ephemeral: true });
                return;
            }
            bdd[interaction.user.id][speed][item][track] = time;
        }
        if (bdd[interaction.user.id] == undefined) {
            bdd[interaction.user.id] = {
                150: {
                    Shroom: {},
                    NI: {},
                },
                200: {
                    Shroom: {},
                    NI: {},
                },
            };
        }
        bdd[interaction.user.id][speed][item][track] = time;
        if (save_bdd() == 0) {
            interaction.reply({ embeds: [new EmbedBuilder().setTitle(`Error`).setColor(0xff0000).setDescription(`could not save the file as expected`)], ephemeral: true });
            return;
        }
        const embed = new EmbedBuilder()
            .setTitle(`Time saved`)
            .setColor(0x47e0ff)
            .setDescription(`saved **${time}** on \`${track}\`, ${speed}cc (${item})`);
        await interaction.reply({ embeds: [embed] });
        ``;
    }
    if (interaction.commandName === "delete_time") {
        if (user_list[interaction.guild.id] == undefined) {
            user_list[interaction.guild.id] = [interaction.user.id];
            save_user_list();
        }
        else if (!user_list[interaction.guild.id].includes(interaction.user.id)) {
            user_list[interaction.guild.id].push(interaction.user.id);
            save_user_list();
        }
        const args = interaction.options.data;
        if (args.length == 3) {
            const speed = interaction.options.get("speed").value;
            item = "NI";
            if (interaction.options.get("item").value == 1) {
                item = "Shroom";
            }
            track = interaction.options.get("track").value;
            for (let i = 0; i < track_list.length; i++) {
                if (track_list[i].toLowerCase() == track.toLowerCase()) {
                    track = track_list[i];
                    break;
                }
                if (i == track_list.length - 1) {
                    const embed = new EmbedBuilder()
                        .setTitle("Error")
                        .setColor(0xff0000)
                        .setDescription(`could not find \`${track}\` in the track list`);
                    await interaction.reply({ embeds: [embed], ephemeral: true });
                    return;
                }
            }
            if (is_track_init(interaction.user.id, speed, item, track)) {
                interaction.reply({
                    embeds: [
                        new EmbedBuilder()
                            .setTitle(`Are you sure?`)
                            .setColor(0xff0000)
                            .setDescription(`you are about to delete **${bdd[interaction.user.id][speed][item][track]}** on \`${track}\` in ${speed}cc (${item})`),
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
                            const embed = new EmbedBuilder()
                                .setTitle(`Error`)
                                .setColor(0xff0000)
                                .setDescription(`you don't have any time saved on \`${track}\` in ${speed} (${item})`);
                            await i.reply({ embeds: [embed], ephemeral: true });
                            return;
                        }
                        delete bdd[interaction.user.id][speed][item][track];
                        if (save_bdd() == 0) {
                            i.reply({ embeds: [new EmbedBuilder().setTitle(`Error`).setColor(0xff0000).setDescription(`could not save the file as expected`)], ephemeral: true });
                            return;
                        }
                        const embed = new EmbedBuilder()
                            .setTitle(`Time deleted`)
                            .setColor(0x47e0ff)
                            .setDescription(`deleted your time on \`${track}\`, ${speed}cc (${item})`);
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
                const embed = new EmbedBuilder()
                    .setTitle(`Error`)
                    .setColor(0xff0000)
                    .setDescription(`you don't have any time saved on \`${track}\` in ${speed} (${item})`);
                await interaction.reply({ embeds: [embed], ephemeral: true });
                return;
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
                        i.reply({ embeds: [new EmbedBuilder().setTitle(`Error`).setColor(0xff0000).setDescription(`could not save the file as expected`)], ephemeral: true });
                        return;
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
                        i.reply({ embeds: [new EmbedBuilder().setTitle(`Error`).setColor(0xff0000).setDescription(`could not save the file as expected`)], ephemeral: true });
                        return;
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
                        i.reply({ embeds: [new EmbedBuilder().setTitle(`Error`).setColor(0xff0000).setDescription(`could not save the file as expected`)], ephemeral: true });
                        return;
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
            track = interaction.options.get("track").value;
            for (let i = 0; i < track_list.length; i++) {
                if (track_list[i].toLowerCase() == track.toLowerCase()) {
                    track = track_list[i];
                    break;
                }
                if (i == track_list.length - 1) {
                    const embed = new EmbedBuilder()
                        .setTitle("Error")
                        .setColor(0xff0000)
                        .setDescription(`could not find \`${track}\` in the track list`);
                    await interaction.reply({ embeds: [embed], ephemeral: true });
                    return;
                }
            }
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
                        i.reply({ embeds: [new EmbedBuilder().setTitle(`Error`).setColor(0xff0000).setDescription(`could not save the file as expected`)], ephemeral: true });
                        return;
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
                        .setDescription(`you are about to delete **all** your times with ${item} on ${speed}cc`),
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
                        i.reply({ embeds: [new EmbedBuilder().setTitle(`Error`).setColor(0xff0000).setDescription(`could not save the file as expected`)], ephemeral: true });
                        return;
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
            track = interaction.options.get("track").value;
            for (let i = 0; i < track_list.length; i++) {
                if (track_list[i].toLowerCase() == track.toLowerCase()) {
                    track = track_list[i];
                    break;
                }
                if (i == track_list.length - 1) {
                    const embed = new EmbedBuilder()
                        .setTitle("Error")
                        .setColor(0xff0000)
                        .setDescription(`could not find \`${track}\` in the track list`);
                    await interaction.reply({ embeds: [embed], ephemeral: true });
                    return;
                }
            }
            interaction.reply({
                embeds: [
                    new EmbedBuilder()
                        .setTitle(`Are you sure?`)
                        .setColor(0xff0000)
                        .setDescription(`you are about to delete **all** your times on ${track} in ${speed}cc`),
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
                        i.reply({ embeds: [new EmbedBuilder().setTitle(`Error`).setColor(0xff0000).setDescription(`could not save the file as expected`)], ephemeral: true });
                        return;
                    }
                    const embed = new EmbedBuilder()
                        .setTitle(`Time deleted`)
                        .setColor(0x47e0ff)
                        .setDescription(`deleted all your times on ${track} in ${speed}`);
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
            track = interaction.options.get("track").value;
            for (let i = 0; i < track_list.length; i++) {
                if (track_list[i].toLowerCase() == track.toLowerCase()) {
                    track = track_list[i];
                    break;
                }
                if (i == track_list.length - 1) {
                    const embed = new EmbedBuilder()
                        .setTitle("Error")
                        .setColor(0xff0000)
                        .setDescription(`could not find \`${track}\` in the track list`);
                    await interaction.reply({ embeds: [embed], ephemeral: true });
                    return;
                }
            }
            interaction.reply({
                embeds: [
                    new EmbedBuilder()
                        .setTitle(`Are you sure?`)
                        .setColor(0xff0000)
                        .setDescription(`you are about to delete **all** your times on ${track} with ${item}`),
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
                        i.reply({ embeds: [new EmbedBuilder().setTitle(`Error`).setColor(0xff0000).setDescription(`could not save the file as expected`)], ephemeral: true });
                        return;
                    }
                    const embed = new EmbedBuilder()
                        .setTitle(`Time deleted`)
                        .setColor(0x47e0ff)
                        .setDescription(`deleted all your times on ${track} with ${item}`);
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
        if (user_list[interaction.guild.id] == undefined) {
            user_list[interaction.guild.id] = [interaction.user.id];
            save_user_list();
        }
        else if (!user_list[interaction.guild.id].includes(interaction.user.id)) {
            user_list[interaction.guild.id].push(interaction.user.id);
            save_user_list();
        }
        if (!bdd[interaction.user.id]) {
            bdd[interaction.user.id] = {
                150: {
                    Shroom: {},
                    NI: {},
                },
                200: {
                    Shroom: {},
                    NI: {},
                },
            };
        }
        const speed = interaction.options.get("speed").value;
        item = "NI";
        if (interaction.options.get("item").value == 1) {
            item = "Shroom";
        }
        const list = interaction.options.get("list").value;
        const list_array = list.match(/[a-z,A-Z,0-9]+ : [0-9]+\/[0-9]+ -> [0-9]:[0-5][0-9]\.[0-9]{3}/g);
        if (list_array == null) {
            const embed = new EmbedBuilder()
                .setTitle("Error")
                .setColor(0xff0000)
                .setDescription(`the list you provided is not valid`);
            await interaction.reply({ embeds: [embed], ephemeral: true });
            return;
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
            time = list_array[i].split(" -> ")[1];
            bdd[interaction.user.id][speed][item][track] = time;
        }
        if (save_bdd() == 0) {
            interaction.reply({ embeds: [new EmbedBuilder().setTitle(`Error`).setColor(0xff0000).setDescription(`could not save the file as expected`)], ephemeral: true });
            return;
        }
        const embed = new EmbedBuilder()
            .setTitle(`Times imported`)
            .setColor(0x47e0ff)
            .setDescription(`imported all your times from the list`);
        await interaction.reply({ embeds: [embed] });
    }
    if (interaction.commandName === "display_time") {
        const args = interaction.options.data;
        if (args.length == 2 && (args[0].name == "item" && args[1].name == "speed" || args[0].name == "speed" && args[1].name == "item")) {
            const speed = interaction.options.get("speed").value;
            item = "NI";
            if (interaction.options.get("item").value == 1) {
                item = "Shroom";
            }
            if (user_list[interaction.guild.id] == undefined) {
                interaction.reply({
                    embeds: [
                        new EmbedBuilder()
                            .setTitle(`Error`)
                            .setColor(0xff0000)
                            .setDescription(`sorry, but this server is not registered in the database, please register members with the \`/register\` command`),
                    ],
                    ephemeral: true,
                })
            }
            else {
                best_times_string = '';
                best_time_object = {};
                for (let i = 0; i < user_list[interaction.guild.id].length; i++) {
                    if (bdd[user_list[interaction.guild.id][i]] == undefined) {
                        user_list[interaction.guild.id].splice(i, 1);
                        save_user_list();
                        i--;
                        continue;
                    }
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
                    for (let track in bdd[user_list[interaction.guild.id][i]][speed][item]) {
                        if (best_time_object[track] == undefined) {
                            best_time_object[track] = track + `: \`${bdd[user_list[interaction.guild.id][i]][speed][item][track]}\` - ${user.displayName}`;
                        }
                        else if (bdd[user_list[interaction.guild.id][i]][speed][item][track] < best_time_object[track].split("`")[1]) {
                            best_time_object[track] = track + `: \`${bdd[user_list[interaction.guild.id][i]][speed][item][track]}\` - ${user.displayName}`;
                        }
                        else if (bdd[user_list[interaction.guild.id][i]][speed][item][track] == best_time_object[track].split("`")[1]) {
                            best_time_object[track] += `/${user.displayName}`;
                        }
                    }
                }
                for (let track in best_time_object) {
                    best_times_string += best_time_object[track] + "\n";
                }
                if (best_times_string == '') {
                    interaction.reply({
                        embeds: [
                            new EmbedBuilder()
                                .setTitle(`Error`)
                                .setColor(0xff0000)
                                .setDescription(`sorry, but no one has registered any time for this category`),
                        ],
                        ephemeral: true,
                    })
                }
                else {
                    interaction.reply({
                        embeds: [
                            new EmbedBuilder()
                                .setTitle(`${speed}cc ${item}`)
                                .setColor(0x47e0ff)
                                .setDescription(best_times_string),
                        ],
                    })
                }
            }
        }
        else if (args.length == 3 && interaction.options.get("track") != undefined) {
            const speed = interaction.options.get("speed").value;
            item = "NI";
            if (interaction.options.get("item").value == 1) {
                item = "Shroom";
            }
            track = interaction.options.get("track").value;
            for (let i = 0; i < track_list.length; i++) {
                if (track_list[i].toLowerCase() == track.toLowerCase()) {
                    track = track_list[i];
                    break;
                }
                if (i == track_list.length - 1) {
                    interaction.reply({
                        embeds: [
                            new EmbedBuilder()
                                .setTitle(`Error`)
                                .setColor(0xff0000)
                                .setDescription(`sorry, but the track you provided is not valid`),
                        ],
                        ephemeral: true
                    })
                }
            }
            if (user_list[interaction.guild.id] == undefined) {
                interaction.reply({
                    embeds: [
                        new EmbedBuilder()
                            .setTitle(`Error`)
                            .setColor(0xff0000)
                            .setDescription(`sorry, but this server is not registered in the database, please register members with the \`/register\` command`),
                    ],
                    ephemeral: true,
                })
            }
            else {
                best_times_string = '';
                best_time_object = [];
                for (let i = 0; i < user_list[interaction.guild.id].length; i++) {
                    if (bdd[user_list[interaction.guild.id][i]] == undefined) {
                        user_list[interaction.guild.id].splice(i, 1);
                        save_user_list();
                        i--;
                        continue;
                    }
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
                best_time_object.sort((a, b) => a.time - b.time);
                for (let i = 0; i < best_time_object.length; i++) {
                    best_times_string += `**${i + 1}**: ${best_time_object[i].user}: \`${best_time_object[i].time}\`\n`;
                }
                if (best_times_string == '') {
                    interaction.reply({
                        embeds: [
                            new EmbedBuilder()
                                .setTitle(`Error`)
                                .setColor(0xff0000)
                                .setDescription(`sorry, but no one has registered any time for this category`),
                        ],
                        ephemeral: true,
                    })
                }
                else {
                    interaction.reply({
                        embeds: [
                            new EmbedBuilder()
                                .setTitle(`${track} ${speed}cc ${item}`)
                                .setColor(0x47e0ff)
                                .setDescription(best_times_string),
                        ],
                    })
                }
            }
        }
        else if (args.length == 3 && interaction.options.get("user").value != undefined) {
            const speed = interaction.options.get("speed").value;
            item = "NI";
            if (interaction.options.get("item").value == 1) {
                item = "Shroom";
            }
            var user_id = interaction.options.get("user").value;
            if (user_id.startsWith("<@!") && user_id.endsWith(">")) {
                user_id = user_id.slice(3, -1);
            }
            else if (user_id.startsWith("<@") && user_id.endsWith(">")) {
                user_id = user_id.slice(2, -1);
            }
            if (isNaN(user_id)) {
                interaction.reply({
                    embeds: [
                        new EmbedBuilder()
                            .setTitle(`Error`)
                            .setColor(0xff0000)
                            .setDescription(`sorry, but the user you provided is not valid`),
                    ],
                    ephemeral: true,
                })
                return;
            }
            if (bdd[user_id] == undefined) {
                interaction.reply({
                    embeds: [
                        new EmbedBuilder()
                            .setTitle(`Error`)
                            .setColor(0xff0000)
                            .setDescription(`sorry, but the user you provided is not registered in the database`),
                    ],
                    ephemeral: true,
                })
                return;
            }
            try {
                user = await interaction.guild.members.fetch(user_id);
            }
            catch (e) {
                interaction.reply({
                    embeds: [
                        new EmbedBuilder()
                            .setTitle(`Error`)
                            .setColor(0xff0000)
                            .setDescription(`sorry, but the user you provided is not valid`),
                    ],
                    ephemeral: true,
                })
                return;
            }
            time_list = '';
            for (let i = 0; i < track_list.length; i++) {
                if (bdd[user_id][speed][item][track_list[i]] != undefined) {
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
                    track_rank.sort((a, b) => a.time - b.time);
                    for (let j = 0; j < track_rank.length; j++) {
                        if (track_rank[j].user == user_id) {
                            time_list += `**${track_list[i]}**: \`${bdd[user_id][speed][item][track_list[i]]}\` - ${j + 1}/${track_rank.length}\n`;
                            break;
                        }
                    }
                }
            }
            if (time_list == '') {
                interaction.reply({
                    embeds: [
                        new EmbedBuilder()
                            .setTitle(`Error`)
                            .setColor(0xff0000)
                            .setDescription(`sorry, but this user has not registered any time for this category`),
                    ],
                    ephemeral: true,
                })
            }
            else {
                interaction.reply({
                    embeds: [
                        new EmbedBuilder()
                            .setTitle(`${user.displayName} ${speed}cc ${item}`)
                            .setColor(0x47e0ff)
                            .setDescription(time_list),
                    ],
                })
            }
        }
        else if (args.length == 4) {
            const speed = interaction.options.get("speed").value;
            item = "NI";
            if (interaction.options.get("item").value == 1) {
                item = "Shroom";
            }
            var track = interaction.options.get("track").value;
            for (let i = 0; i < track_list.length; i++) {
                if (track_list[i].toLowerCase() == track.toLowerCase()) {
                    track = track_list[i];
                    break;
                }
                if (i == track_list.length - 1) {
                    interaction.reply({
                        embeds: [
                            new EmbedBuilder()
                                .setTitle(`Error`)
                                .setColor(0xff0000)
                                .setDescription(`sorry, but the track you provided is not valid`),
                        ],
                        ephemeral: true,
                    })
                    return;
                }
            }
            var user_id = interaction.options.get("user").value;
            if (user_id.startsWith("<@!") && user_id.endsWith(">")) {
                user_id = user_id.slice(3, -1);
            }
            else if (user_id.startsWith("<@") && user_id.endsWith(">")) {
                user_id = user_id.slice(2, -1);
            }
            if (isNaN(user_id)) {
                interaction.reply({
                    embeds: [
                        new EmbedBuilder()
                            .setTitle(`Error`)
                            .setColor(0xff0000)
                            .setDescription(`sorry, but the user you provided is not valid`),
                    ],
                    ephemeral: true,
                })
                return;
            }
            if (bdd[user_id] == undefined) {
                interaction.reply({
                    embeds: [
                        new EmbedBuilder()
                            .setTitle(`Error`)
                            .setColor(0xff0000)
                            .setDescription(`sorry, but the user you provided is not registered in the database`),
                    ],
                    ephemeral: true,
                })
                return;
            }
            try {
                user = await interaction.guild.members.fetch(user_id);
            }
            catch (e) {
                interaction.reply({
                    embeds: [
                        new EmbedBuilder()
                            .setTitle(`Error`)
                            .setColor(0xff0000)
                            .setDescription(`sorry, but the user you provided is not valid`),
                    ],
                    ephemeral: true,
                })
                return;
            }
            if (bdd[user_id][speed][item][track] == undefined) {
                interaction.reply({
                    embeds: [
                        new EmbedBuilder()
                            .setTitle(`Error`)
                            .setColor(0xff0000)
                            .setDescription(`sorry, but this user has not registered any time for this category`),
                    ],
                    ephemeral: true,
                })
            }
            else {
                interaction.reply({
                    embeds: [
                        new EmbedBuilder()
                            .setTitle(`${user.displayName} ${track} ${speed}cc ${item}`)
                            .setColor(0x47e0ff)
                            .setDescription(`\`${bdd[user_id][speed][item][track]}\` + ratio`),
                    ],
                })
            }
        }
    }
});

client.login(token.Quaxly);
