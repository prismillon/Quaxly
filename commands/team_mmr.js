import { error_embed, averageMmr } from "../utils.js";

export const team_mmr = async (interaction) => {
    if (interaction.options.get("player").value.includes('<@&')) {
        interaction.guild.members.fetch()
            .then(async members => {
                const role = interaction.options.get("player").value.replace(/\D/g, '');
                const ids = members.filter(mmbr => mmbr.roles.cache.get(role)).map(m => m.user.id)
                let embed =
                {
                    title: "Average MMR ",
                    description: interaction.options.get("player").value,
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
                        averageMmr(ids, embed, interaction, embedArray, jsonArray, mmrArray)

                    })
                }
            });
    }
    else if (interaction.options.get("player").value.replace(/[0-9 ]/g, '').includes('<@><@>')) {
        let ids = interaction.options.get("player").value.replace(/[<> ]/g, '').split('@')
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
                averageMmr(ids, embed, interaction, embedArray, jsonArray, mmrArray)

            })
        }
    }
    else return error_embed(interaction, "Wrong option format: mention one role or multiple users");
}