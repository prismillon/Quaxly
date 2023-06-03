import { error_embed, playersStats, teamFCs, teamList } from "../utils.js";

export const team_stats = async (interaction) => {
    await interaction.deferReply()
    let season = interaction.options.get("season") && interaction.options.get("season").value != undefined ? "Season " + interaction.options.get("season").value + " " : ""
        switch (true) {
            case interaction.options.get("group").value.includes('<@&'):
                interaction.guild.members.fetch()
                    .then(async members => {
                        const role = interaction.options.get("group").value.replace(/\D/g, '');
                        const ids = members.filter(mmbr => mmbr.roles.cache.get(role)).map(m => m.user.id)
                        let embed =
                        {
                            title: season + "Average MMR ",
                            description: interaction.options.get("group").value,
                            color: 15514131,
                            fields: [
                            ],
                            thumbnail: {
                                url: interaction.guild.iconURL()
                            }
                        }
                        if (ids.length > 300) return error_embed(interaction, "Your role have too many members. Please retry with less than 300 members.");
                        else if (ids.length == 0) return error_embed(interaction, "Your role have no members. Please retry with another role with more than 0 members.");
                        else {
                            await playersStats("discordid", ids, embed, interaction)
                        }
                    });
                break
            case interaction.options.get("group").value.replace(/[0-9 ]/g, '').includes('<@><@>'):
                let ids = interaction.options.get("group").value.replace(/[<> ]/g, '').split('@')
                ids.shift()
                let embed =
                {
                    title: season + "Average MMR",
                    color: 15514131,
                    fields: [
                    ],
                    thumbnail: {
                        url: interaction.guild.iconURL()
                    }
                }
                if (ids.length > 300) return error_embed(interaction, "Your command have too many users. Please retry with less than 300 users.");
                else if (ids.length == 0) return error_embed(interaction, "Your command have no users. Please retry with more than 0 users.");
                else {
                    await playersStats("discordid", ids, embed, interaction)
                }
                break
            case interaction.options.get("group").value.includes('https://www.mariokartcentral.com/mkc/registry/teams/') || interaction.options.get("group").value.match(/^[0-9]+$/) != null:
                teamFCs(interaction.options.get("group").value.replace(/\D/g, ''), interaction)
                break
            default:
                let json = teamList
                const team_name = interaction.options.get("group").value.toLowerCase()
                try {
                    if (json.data.find(el => el.team_name.toLowerCase() == team_name) !== undefined) {
                        await teamFCs(json.data.find(el => el.team_name.toLowerCase() == team_name).team_id, interaction)
                    }
                    else return error_embed(interaction, "Wrong option format: mention a role, multiple users, a team url or a team name.");
                } catch (error) {
                    console.log(error, interaction.options.get("group").value, interaction);
                }
                break;
        }
}