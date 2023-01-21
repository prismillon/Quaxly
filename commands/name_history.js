import { error_embed } from "../utils.js";

export const name_history = async (interaction) => {
    const discordId = interaction.options.get("player") != undefined ? interaction.options.get("player").value.replace(/[<>@]/gm, '') : interaction.user.id
    let json = (/^\d+$/.test(discordId)) ?
        await (await fetch("https://www.mk8dx-lounge.com/api/player/details?name=" + (await (await fetch("https://www.mk8dx-lounge.com/api/player?discordid=" + discordId + "&quaxly=true")).json().catch()).name + "&quaxly=true")).json().catch()
        : await (await fetch("https://www.mk8dx-lounge.com/api/player/details?name=" + discordId + "&quaxly=true")).json().catch()
    if (json.status == 404) return error_embed(interaction, "Please use a lounge name, @user or ID");
    const loungeId = json.playerId
    let nameDate = new Date(json.nameHistory[0].changedOn)
    let nextChange
    nameDate.setDate(nameDate.getDate() + 60)
    if (nameDate < new Date()) {
        nextChange = "✅ User can change name since <t:" + Math.floor(nameDate.getTime() / 1000) + '>'
    }
    else {
        nextChange = "⏳ User will be able to change name on <t:" + Math.floor(nameDate.getTime() / 1000) + '>'
    }
    let embed =
    {
        title: json.name + "'s name history",
        url: `https://www.mk8dx-lounge.com/PlayerDetails/${loungeId}`,
        description: nextChange,
        color: 15514131,
        fields: []
    }
    json.nameHistory.forEach(function (nameArray) {
        embed.fields.push({ name: nameArray.name, value: 'Changed on: <t:' + Math.floor(new Date(nameArray.changedOn).getTime() / 1000) + '>', inline: false })
    })
    interaction.reply({ embeds: [embed] })
}