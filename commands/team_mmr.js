import { error_embed, averageMmr, teamFCs } from "../utils.js";

export const team_mmr = async (interaction) => {
    if (interaction.options.get("group").value.includes('<@&')) {
        interaction.guild.members.fetch()
            .then(async members => {
                const role = interaction.options.get("group").value.replace(/\D/g, '');
                const ids = members.filter(mmbr => mmbr.roles.cache.get(role)).map(m => m.user.id)
                let embed =
                {
                    title: "Average MMR ",
                    description: interaction.options.get("group").value,
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
                        averageMmr("discordid", ids, embed, interaction, embedArray, jsonArray, mmrArray)

                    })
                }
            });
    }
    else if (interaction.options.get("group").value.replace(/[0-9 ]/g, '').includes('<@><@>')) {
        let ids = interaction.options.get("group").value.replace(/[<> ]/g, '').split('@')
        ids.shift()
        let embed =
        {
            title: "Average MMR",
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
                    description: "Your command have too many users. Please retry with less than 300 users.",
                    color: 15863148
                }]
            })
        }
        else {
            interaction.reply({ embeds: [embed] }).then(async () => {
                averageMmr("discordid", ids, embed, interaction, embedArray, jsonArray, mmrArray)

            })
        }
    }
    else if (interaction.options.get("group").value.includes('https://www.mariokartcentral.com/mkc/registry/teams/') || interaction.options.get("group").value.match(/^[0-9]+$/) != null) {
        const team_id = interaction.options.get("group").value.replace(/\D/g, '')
        teamFCs(team_id, interaction)
    }
    else {
        fetch("https://www.mariokartcentral.com/mkc/api/registry/teams/category/150cc")
            .then((r) => {
                return r.text()
            }).then((r) => {
                let json = JSON.parse(r.toLowerCase())
                const team_name = interaction.options.get("group").value.toLowerCase()
                if (json.data.find(el => el.team_name == team_name) !== undefined) {
                    teamFCs(json.data.find(el => el.team_name == team_name).team_id, interaction)
                }
                else return error_embed(interaction, "Wrong option format: mention one role or multiple users");
            })
    }
}