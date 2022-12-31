import { EmbedBuilder } from "discord.js"
import { track_list } from "../utils.js"

function getTracks(cup) {
    switch (cup) {
        case "mushroom_cup":
            return track_list.filter((_, i) => i < 4)
        case "flower_cup":
            return track_list.filter((_, i) => i >= 4 && i < 8)
        case "star_cup":
            return track_list.filter((_, i) => i >= 8 && i < 12)
        case "special_cup":
            return track_list.filter((_, i) => i >= 12 && i < 16)
        case "shell_cup":
            return track_list.filter((_, i) => i >= 16 && i < 20)
        case "banana_cup":
            return track_list.filter((_, i) => i >= 20 && i < 24)
        case "leaf_cup":
            return track_list.filter((_, i) => i >= 24 && i < 28)
        case "lightning_cup":
            return track_list.filter((_, i) => i >= 28 && i < 32)
        case "egg_cup":
            return track_list.filter((_, i) => i >= 32 && i < 36)
        case "crossing_cup":
            return track_list.filter((_, i) => i >= 36 && i < 40)
        case "triforce_cup":
            return track_list.filter((_, i) => i >= 40 && i < 44)
        case "bell_cup":
            return track_list.filter((_, i) => i >= 44 && i < 48)
        case "golden_dash_cup":
            return track_list.filter((_, i) => i >= 48 && i < 52)
        case "lucky_cat_cup":
            return track_list.filter((_, i) => i >= 52 && i < 56)
        case "turnip_cup":
            return track_list.filter((_, i) => i >= 56 && i < 60)
        case "propeller_cup":
            return track_list.filter((_, i) => i >= 60 && i < 64)
        case "rock_cup":
            return track_list.filter((_, i) => i >= 64 && i < 68)
        case "moon_cup":
            return track_list.filter((_, i) => i >= 68 && i < 72)
    }
}

const emoji_to_links = {
    "mushroom_cup": "https://cdn.discordapp.com/attachments/1055130165782515803/1055130224636997734/MK8_MushroomCup.png",
    "flower_cup": "https://cdn.discordapp.com/attachments/1055130165782515803/1055130308460150875/MK8_FlowerCup.png",
    "star_cup": "https://cdn.discordapp.com/attachments/1055130165782515803/1055130334758457395/MK8_Star_Cup_Emblem.png",
    "special_cup": "https://cdn.discordapp.com/attachments/1055130165782515803/1055130369025904681/MK8_Special_Cup_Emblem.png",
    "shell_cup": "https://cdn.discordapp.com/attachments/1055130165782515803/1055130415305859082/MK8_Shell_Cup_Emblem.png",
    "banana_cup": "https://cdn.discordapp.com/attachments/1055130165782515803/1055130438567473152/MK8_Banana_Cup_Emblem.png",
    "leaf_cup": "https://cdn.discordapp.com/attachments/1055130165782515803/1055130520792596530/MK8_Leaf_Cup_Emblem.png",
    "lightning_cup": "https://cdn.discordapp.com/attachments/1055130165782515803/1055130541642498138/MK8_Lightning_Cup_Emblem.png",
    "egg_cup": "https://cdn.discordapp.com/attachments/1055130165782515803/1055130682646597743/MK8_Egg_Cup_Emblem.png",
    "crossing_cup": "https://cdn.discordapp.com/attachments/1055130165782515803/1055130705530736681/MK8_Crossing_Cup_Emblem.png",
    "triforce_cup": "https://cdn.discordapp.com/attachments/1055130165782515803/1055130730289713202/MK8_Triforce_Cup_Emblem.png",
    "bell_cup": "https://cdn.discordapp.com/attachments/1055130165782515803/1055130752402067476/MK8_Bell_Cup_Emblem.png",
    "golden_dash_cup": "https://cdn.discordapp.com/attachments/1055130165782515803/1055131041343475722/MK8D_BCP_Golden_Dash_Emblem.png",
    "lucky_cat_cup": "https://cdn.discordapp.com/attachments/1055130165782515803/1055131061765546005/MK8D_BCP_Lucky_Cat_Emblem.png",
    "turnip_cup": "https://cdn.discordapp.com/attachments/1055130165782515803/1055131093306724393/MK8D_BCP_Turnip_Emblem.png",
    "propeller_cup": "https://cdn.discordapp.com/attachments/1055130165782515803/1055131126563340379/MK8D_BCP_Propeller_Emblem.png",
    "rock_cup": "https://cdn.discordapp.com/attachments/1055130165782515803/1055131250362437632/MK8D_BCP_Rock_Emblem.png",
    "moon_cup": "https://cdn.discordapp.com/attachments/1055130165782515803/1055131264975384657/MK8D_BCP_Moon_Emblem.png",
}

let emoji_buttons = [{
    "type": 1,
    "components": [
        {
            "style": 2,
            "custom_id": `mushroom_cup`,
            "disabled": false,
            "emoji": {
                "id": `1055103822671925298`,
                "name": `MK8_MushroomCup`,
                "animated": false
            },
            "type": 2
        },
        {
            "style": 2,
            "custom_id": `flower_cup`,
            "disabled": false,
            "emoji": {
                "id": `1055103818968346705`,
                "name": `MK8_FlowerCup`,
                "animated": false
            },
            "type": 2
        },
        {
            "style": 2,
            "custom_id": `star_cup`,
            "disabled": false,
            "emoji": {
                "id": `1055104114238955592`,
                "name": `MK8_StarCup`,
                "animated": false
            },
            "type": 2
        },
        {
            "style": 2,
            "custom_id": `special_cup`,
            "disabled": false,
            "emoji": {
                "id": `1055103822671925298`,
                "name": `MK8_SpecialCup`,
                "animated": false
            },
            "type": 2
        },
        {
            "style": 2,
            "custom_id": `shell_cup`,
            "disabled": false,
            "emoji": {
                "id": `1055103823577878650`,
                "name": `MK8_ShellCup`,
                "animated": false
            },
            "type": 2
        }
    ]
},
{
    "type": 1,
    "components": [
        {
            "style": 2,
            "custom_id": `banana_cup`,
            "disabled": false,
            "emoji": {
                "id": `1055103812588806154`,
                "name": `MK8_BananaCup`,
                "animated": false
            },
            "type": 2
        },
        {
            "style": 2,
            "custom_id": `leaf_cup`,
            "disabled": false,
            "emoji": {
                "id": `1055103820268585020`,
                "name": `MK8_LeafCup`,
                "animated": false
            },
            "type": 2
        },
        {
            "style": 2,
            "custom_id": `lightning_cup`,
            "disabled": false,
            "emoji": {
                "id": `1055103821455564851`,
                "name": `MK8_LightningCup`,
                "animated": false
            },
            "type": 2
        },
        {
            "style": 2,
            "custom_id": `egg_cup`,
            "disabled": false,
            "emoji": {
                "id": `1055103817424834580`,
                "name": `MK8_EggCup`,
                "animated": false
            },
            "type": 2
        },
        {
            "style": 2,
            "custom_id": `crossing_cup`,
            "disabled": false,
            "emoji": {
                "id": `1055103816070090772`,
                "name": `MK8_CrossingCup`,
                "animated": false
            },
            "type": 2
        }
    ]
},
{
    "type": 1,
    "components": [
        {
            "style": 2,
            "custom_id": `triforce_cup`,
            "disabled": false,
            "emoji": {
                "id": `1055103826811699250`,
                "name": `MK8_TriforceCup`,
                "animated": false
            },
            "type": 2
        },
        {
            "style": 2,
            "custom_id": `bell_cup`,
            "disabled": false,
            "emoji": {
                "id": `1055103814438494319`,
                "name": `MK8_BellCup`,
                "animated": false
            },
            "type": 2
        },
        {
            "style": 2,
            "custom_id": `golden_dash_cup`,
            "disabled": false,
            "emoji": {
                "id": `1055103948345835582`,
                "name": `MK8_GoldenDashCup`,
                "animated": false
            },
            "type": 2
        },
        {
            "style": 2,
            "custom_id": `lucky_cat_cup`,
            "disabled": false,
            "emoji": {
                "id": `1055103946911399976`,
                "name": `MK8_LuckyCatCup`,
                "animated": false
            },
            "type": 2
        },
        {
            "style": 2,
            "custom_id": `turnip_cup`,
            "disabled": false,
            "emoji": {
                "id": `1055103834189463573`,
                "name": `MK8_TurnipCup`,
                "animated": false
            },
            "type": 2
        }
    ]
},
{
    "type": 1,
    "components": [
        {
            "style": 2,
            "custom_id": `propeller_cup`,
            "disabled": false,
            "emoji": {
                "id": `1055103943161696276`,
                "name": `MK8_PropellerCup`,
                "animated": false
            },
            "type": 2
        },
        {
            "style": 2,
            "custom_id": `rock_cup`,
            "disabled": false,
            "emoji": {
                "id": `1055103941345558609`,
                "name": `MK8_RockCup`,
                "animated": false
            },
            "type": 2
        },
        {
            "style": 2,
            "custom_id": `moon_cup`,
            "disabled": false,
            "emoji": {
                "id": `1055103830263595028`,
                "name": `MK8_MoonCup`,
                "animated": false
            },
            "type": 2
        },
    ]
}]

export const tracks = async (interaction) => {
    try {
        await interaction.reply({
            embeds: [
                new EmbedBuilder()
                    .setTitle("Tracks")
                    .setColor(0x47e0ff)
                    .setDescription("Here is the list of all the cups in Mario Kart 8 Deluxe")
                    .setThumbnail(interaction.guild.iconURL())
            ],
            components: emoji_buttons
        })
        const collector = interaction.channel.createMessageComponentCollector({
            time: 600000
        })
        collector.on('end', async () => {
            await interaction.editReply({
                components: []
            })
            collector.stop();
        })
        collector.on("collect", async (button) => {
            try {
                const tracks = getTracks(button.customId).join(",   ")
                await button.update({
                    embeds: [
                        {
                            Title: `Tracks in the ${button.customId.replace(/_/g, " ")}`,
                            Description: `\`\`\`${tracks}\`\`\``,
                            Color: 0x47e0ff,
                            thumbnail: {
                                url: emoji_to_links[button.customId]
                            }
                        }
                    ],
                    components: emoji_buttons
                })
            } catch (e) {
                await button.channel.send({
                    content: "You've clicked too fast for the bot to respond. Please dm pierre#1111 if you think this is a bug",
                    ephemeral: true
                }).catch((e) => {
                    console.log(e, interaction)
                })
            }
        })
    } catch (e) {
        throw e;
    }
}