
import { EmbedBuilder, } from "discord.js";

export const help = async (interaction) => {
    return await interaction.reply({
        embeds: [
            new EmbedBuilder()
                .setTitle("Help menu")
                .setColor(0x47e0ff)
                .setFooter({ text: "Made by @prrh, feel free to contact me if you have any questions" })
                .addFields(
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
                        name: "/tracks",
                        value: "Give buttons to select cups that then show tracks name to use with the bot",
                    },
                    {
                        name: "/name_history",
                        value: "Show the past name of the user and if he can change name or not (if you change uppercase this is likely to be broken this is not a lounge official tool)",
                    },
                    {
                        name: "/team_stats",
                        value: "Show stats and average of a group it can be from a discord role or an mkc roaster and can show events mmr or peak mmr",
                    },
                )
        ],
    })
}