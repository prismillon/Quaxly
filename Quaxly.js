const {
    Client,
    GatewayIntentBits,
    EmbedBuilder,
    ActivityType,
    ActionRowBuilder,
    ButtonBuilder,
    ButtonStyle,
} = require("discord.js");
const client = new Client({ intents: [GatewayIntentBits.Guilds] });
const token = require("./config.json");
const fs = require("fs");

function is_track_init(user_id, speed, item, track) {
    if (bdd[user_id] != undefined && bdd[user_id][speed] != undefined && bdd[user_id][speed][item] != undefined && bdd[user_id][speed][item][track] != undefined) {
        return true;
    }
    return false;
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

fs.writeFileSync("./bdd_backup.json", JSON.stringify(bdd, null, 4));

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
                .setDescription(
                    `recived \`${time}\` please use this format instead -> \`1:23.456\``
                );
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
                    .setDescription(
                        `you already have \`${bdd[interaction.user.id][speed][item][track]}\` on this track, do you really want to override it?`
                    );
                await interaction.reply({
                    embeds: [embed],
                    ephemeral: true,
                    components: [
                        new ActionRowBuilder().addComponents(
                            new ButtonBuilder()
                                .setCustomId("cancel")
                                .setLabel("No")
                                .setStyle(ButtonStyle.Danger),
                            new ButtonBuilder()
                                .setCustomId("override")
                                .setLabel("Yes")
                                .setStyle(ButtonStyle.Success)
                        ),
                    ],
                });
                const collector = interaction.channel.createMessageComponentCollector({
                    filter: (i) => i.user.id === interaction.user.id,
                    max: 1,
                    time: 15000,
                });
                collector.on("collect", async (i) => {
                    if (i.customId == "cancel") {
                        await i.update({
                            embeds: [
                                new EmbedBuilder().setTitle(`Canceled`).setColor(0x00ff00),
                            ],
                            components: [],
                            fetchReply: true,
                        });
                        
                    }
                    if (i.customId == "override") {
                        bdd[interaction.user.id][speed][item][track] = time;
                        fs.writeFile("./bdd.json", JSON.stringify(bdd, null, 4), (err) => {
                            if (err) {
                                interaction.reply({
                                    content: `error while saving the time`,
                                    ephemeral: true,
                                });
                                
                                return;
                            }
                        });
                        await i.update({
                            embeds: [
                                new EmbedBuilder()
                                    .setTitle(`Done`)
                                    .setColor(0x00ff00)
                                    .setDescription(
                                        `you now have **${bdd[interaction.user.id][speed][item][track]}** on \`${track}\` in ${speed} (${item})`
                                    ),
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
                    .setDescription(
                        `you already have **${bdd[interaction.user.id][speed][item][track]}** on \`${track}\` in ${speed} (${item})`
                    );
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
        fs.writeFile("./bdd.json", JSON.stringify(bdd, null, 4), (err) => {
            if (err) {
                interaction.reply({
                    content: `error while saving the time`,
                    ephemeral: true,
                });
                return;
            }
        });
        const embed = new EmbedBuilder()
            .setTitle(`Time saved`)
            .setColor(0x47e0ff)
            .setDescription(
                `saved **${time}** on \`${track}\`, ${speed}cc (${item})`
            );
        await interaction.reply({ embeds: [embed] });
        ``;
    }
    if (interaction.commandName === "delete_time") {
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
                            .setDescription(
                                `you are about to delete **${bdd[interaction.user.id][speed][item][track]}** on \`${track}\` in ${speed}cc (${item})`
                            ),
                    ],
                    ephemeral: true,
                    components: [
                        new ActionRowBuilder().addComponents(
                            new ButtonBuilder()
                                .setCustomId("Yes")
                                .setLabel("Yes")
                                .setStyle(ButtonStyle.Success),
                            new ButtonBuilder()
                                .setCustomId("No")
                                .setLabel("No")
                                .setStyle(ButtonStyle.Danger)
                        ),
                    ],
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
                                .setDescription(
                                    `you don't have any time saved on \`${track}\` in ${speed} (${item})`
                                );
                            await i.reply({ embeds: [embed], ephemeral: true });
                            return;
                        }
                        delete bdd[interaction.user.id][speed][item][track];
                        fs.writeFile("./bdd.json", JSON.stringify(bdd, null, 4), (err) => {
                            if (err) {
                                i.reply({
                                    content: `error while saving database`,
                                    ephemeral: true,
                                });
                                
                                return;
                            }
                        });
                        const embed = new EmbedBuilder()
                            .setTitle(`Time deleted`)
                            .setColor(0x47e0ff)
                            .setDescription(
                                `deleted your time on \`${track}\`, ${speed}cc (${item})`
                            );
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
                    .setDescription(
                        `you don't have any time saved on \`${track}\` in ${speed} (${item})`
                    );
                await interaction.reply({ embeds: [embed], ephemeral: true });
                return;
            }
        }
        else if (args.length == 0){
            interaction.reply({
                embeds: [
                    new EmbedBuilder()
                        .setTitle(`Are you sure?`)
                        .setColor(0xff0000)
                        .setDescription(
                            `you are about to delete **all** your times`
                        ),
                ],
                ephemeral: true,
                components: [
                    new ActionRowBuilder().addComponents(
                        new ButtonBuilder()
                            .setCustomId("Yes")
                            .setLabel("Yes")
                            .setStyle(ButtonStyle.Success),
                        new ButtonBuilder()
                            .setCustomId("No")
                            .setLabel("No")
                            .setStyle(ButtonStyle.Danger)
                    ),
                ],
            });
            const collector = interaction.channel.createMessageComponentCollector({
                filter: (i) => i.user.id === interaction.user.id,
                max: 1,
                time: 15000,
            });
            collector.on("collect", async (i) => {
                if (i.customId == "Yes") {
                    delete bdd[interaction.user.id];
                    fs.writeFile("./bdd.json", JSON.stringify(bdd, null, 4), (err) => {
                        if (err) {
                            i.reply({
                                content: `error while saving database`,
                                ephemeral: true,
                            });
                            return;
                        }
                    });
                    const embed = new EmbedBuilder()
                        .setTitle(`Time deleted`)
                        .setColor(0x47e0ff)
                        .setDescription(
                            `deleted all your times`
                        );
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
        else if(args.length == 1 && args[0].name == "speed"){
            const speed = interaction.options.get("speed").value;
            interaction.reply({
                embeds: [
                    new EmbedBuilder()
                        .setTitle(`Are you sure?`)
                        .setColor(0xff0000)
                        .setDescription(
                            `you are about to delete **all** your times in ${speed}cc`
                        ),
                ],
                ephemeral: true,
                components: [
                    new ActionRowBuilder().addComponents(
                        new ButtonBuilder()
                            .setCustomId("Yes")
                            .setLabel("Yes")
                            .setStyle(ButtonStyle.Success),
                        new ButtonBuilder()
                            .setCustomId("No")
                            .setLabel("No")
                            .setStyle(ButtonStyle.Danger)
                    ),
                ],
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
                    fs.writeFile("./bdd.json", JSON.stringify(bdd, null, 4), (err) => {
                        if (err) {
                            i.reply({
                                content: `error while saving database`,
                                ephemeral: true,
                            });
                            return;
                        }
                    });
                    const embed = new EmbedBuilder()
                        .setTitle(`Time deleted`)
                        .setColor(0x47e0ff)
                        .setDescription(
                            `deleted all your times in ${speed}`
                        );
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
        else if(args.length == 1 && args[0].name == "item"){
            item = "NI";
            if (interaction.options.get("item").value == 1) {
                item = "Shroom";
            }
            interaction.reply({
                embeds: [
                    new EmbedBuilder()
                        .setTitle(`Are you sure?`)
                        .setColor(0xff0000)
                        .setDescription(
                            `you are about to delete **all** your times with ${item}`
                        ),
                ],
                ephemeral: true,
                components: [
                    new ActionRowBuilder().addComponents(
                        new ButtonBuilder()
                            .setCustomId("Yes")
                            .setLabel("Yes")
                            .setStyle(ButtonStyle.Success),
                        new ButtonBuilder()
                            .setCustomId("No")
                            .setLabel("No")
                            .setStyle(ButtonStyle.Danger)
                    ),
                ],
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
                    fs.writeFile("./bdd.json", JSON.stringify(bdd, null, 4), (err) => {
                        if (err) {
                            i.reply({
                                content: `error while saving database`,
                                ephemeral: true,
                            });
                            return;
                        }
                    });
                    const embed = new EmbedBuilder()
                        .setTitle(`Time deleted`)
                        .setColor(0x47e0ff)
                        .setDescription(
                            `deleted all your times with ${item}`
                        );
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
        else if(args.length == 1 && args[0].name == "track"){
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
                        .setDescription(
                            `you are about to delete **all** your times on ${track}`
                        ),
                ],
                ephemeral: true,
                components: [
                    new ActionRowBuilder().addComponents(
                        new ButtonBuilder()
                            .setCustomId("Yes")
                            .setLabel("Yes")
                            .setStyle(ButtonStyle.Success),
                        new ButtonBuilder()
                            .setCustomId("No")
                            .setLabel("No")
                            .setStyle(ButtonStyle.Danger)
                    ),
                ],
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
                    fs.writeFile("./bdd.json", JSON.stringify(bdd, null, 4), (err) => {
                        if (err) {
                            i.reply({
                                content: `error while saving database`,
                                ephemeral: true,
                            });
                            return;
                        }
                    });
                    const embed = new EmbedBuilder()
                        .setTitle(`Time deleted`)
                        .setColor(0x47e0ff)
                        .setDescription(
                            `deleted all your times on ${track}`
                        );
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
        else if(args.length == 2 && (args[0].name == "speed" && args[1].name == "item") || (args[0].name == "item" && args[1].name == "speed")){
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
                        .setDescription(
                            `you are about to delete **all** your times with ${item} on ${speed}cc`
                        ),
                ],
                ephemeral: true,
                components: [
                    new ActionRowBuilder().addComponents(
                        new ButtonBuilder()
                            .setCustomId("Yes")
                            .setLabel("Yes")
                            .setStyle(ButtonStyle.Success),
                        new ButtonBuilder()
                            .setCustomId("No")
                            .setLabel("No")
                            .setStyle(ButtonStyle.Danger)
                    ),
                ],
            });
            const collector = interaction.channel.createMessageComponentCollector({
                filter: (i) => i.user.id === interaction.user.id,
                max: 1,
                time: 15000,
            });
            collector.on("collect", async (i) => {
                if (i.customId == "Yes") {
                    bdd[interaction.user.id][speed][item] = {};
                    fs.writeFile("./bdd.json", JSON.stringify(bdd, null, 4), (err) => {
                        if (err) {
                            i.reply({
                                content: `error while saving database`,
                                ephemeral: true,
                            });
                            return;
                        }
                    });
                    const embed = new EmbedBuilder()
                        .setTitle(`Time deleted`)
                        .setColor(0x47e0ff)
                        .setDescription(
                            `deleted all your times in ${speed} with ${item}`
                        );
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
        else if(args.length == 2 && (args[0].name == "speed" && args[1].name == "track") || (args[0].name == "track" && args[1].name == "speed")){
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
                        .setDescription(
                            `you are about to delete **all** your times on ${track} in ${speed}cc`
                        ),
                ],
                ephemeral: true,
                components: [
                    new ActionRowBuilder().addComponents(
                        new ButtonBuilder()
                            .setCustomId("Yes")
                            .setLabel("Yes")
                            .setStyle(ButtonStyle.Success),
                        new ButtonBuilder()
                            .setCustomId("No")
                            .setLabel("No")
                            .setStyle(ButtonStyle.Danger)
                    ),
                ],
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
                    fs.writeFile("./bdd.json", JSON.stringify(bdd, null, 4), (err) => {
                        if (err) {
                            i.reply({
                                content: `error while saving database`,
                                ephemeral: true,
                            });
                            return;
                        }
                    });
                    const embed = new EmbedBuilder()
                        .setTitle(`Time deleted`)
                        .setColor(0x47e0ff)
                        .setDescription(
                            `deleted all your times on ${track} in ${speed}`
                        );
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
        else if(args.length == 2 && (args[0].name == "item" && args[1].name == "track") || (args[0].name == "track" && args[1].name == "item")){
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
                        .setDescription(
                            `you are about to delete **all** your times on ${track} with ${item}`
                        ),
                ],
                ephemeral: true,
                components: [
                    new ActionRowBuilder().addComponents(
                        new ButtonBuilder()
                            .setCustomId("Yes")
                            .setLabel("Yes")
                            .setStyle(ButtonStyle.Success),
                        new ButtonBuilder()
                            .setCustomId("No")
                            .setLabel("No")
                            .setStyle(ButtonStyle.Danger)
                    ),
                ],
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
                    fs.writeFile("./bdd.json", JSON.stringify(bdd, null, 4), (err) => {
                        if (err) {
                            interaction.reply({
                                content: `error while saving database`,
                                ephemeral: true,
                            });
                            return;
                        }
                    });
                    const embed = new EmbedBuilder()
                        .setTitle(`Time deleted`)
                        .setColor(0x47e0ff)
                        .setDescription(
                            `deleted all your times on ${track} with ${item}`
                        );
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
        if(!bdd[interaction.user.id]){
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
        fs.writeFile("./bdd.json", JSON.stringify(bdd, null, 4), (err) => {
            if (err) {
                interaction.reply({
                    content: `error while saving database`,
                    ephemeral: true,
                });
                return;
            }
        });
        const embed = new EmbedBuilder()
            .setTitle(`Times imported`)
            .setColor(0x47e0ff)
            .setDescription(
                `imported all your times from the list`
            );
        await interaction.reply({ embeds: [embed] });
    }
});

client.login(token.Quaxly);
