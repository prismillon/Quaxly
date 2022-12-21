import { error_embed } from "../utils.js";

export const name_history = async (interaction) => {
    const discordId = interaction.options.get("player").value.replace(/\D/g, '');
    if (discordId.length === 18) {
        fetch("https://www.mk8dx-lounge.com/api/player?discordid=" + discordId).then(r => {
            return r.text()
        }).then(r => {
            const currentName = JSON.parse(r).name
            fetch("https://www.mk8dx-lounge.com/api/player/details?name=" + currentName).then(r => {
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